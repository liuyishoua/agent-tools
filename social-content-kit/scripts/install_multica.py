#!/usr/bin/env python3
"""Register independent skill acceptance agents without changing live automation.

Credentials are used only by the existing Channel Multica client. The installer
state, backups and reports contain object references and hashes, never tokens or
raw runtime configuration. Uncertain creates are reconciled by name and payload;
an absent reconciliation result never causes another POST.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

from compose import persona_prompt, SCENES, SUPPORT

KIT = Path(__file__).resolve().parents[1]
SKILL_ROOT = KIT.parent
PROJECT_ROOT = SKILL_ROOT.parent
TEMPLATE_ID = "05f361ac-72f8-456a-9a89-31b31db57dff"
SKILL_NAMES = list(SCENES.values()) + list(SUPPORT.values()) + [
    "platform-xhs", "platform-xianyu", "social-content-kit",
]
AGENT_NAMES = {"xiaotao": "小桃·场景技能验收", "outdoor": "户外·场景技能验收"}


def digest(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(value.encode()).hexdigest()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    fd = os.open(temporary, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def skill_package(name):
    home = SKILL_ROOT / name
    content = (home / "SKILL.md").read_text(encoding="utf-8")
    header = content.split("---", 2)
    if len(header) != 3:
        raise ValueError("Missing skill frontmatter: " + name)
    match = re.search(r"(?m)^description:\s*(.+)$", header[1])
    if not match or not re.search(r"(?m)^name:\s*" + re.escape(name) + r"\s*$", header[1]):
        raise ValueError("Invalid skill identity: " + name)
    files = []
    for directory in ("references", "assets", "scripts"):
        for path in sorted((home / directory).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if not path.resolve().is_relative_to(home.resolve()):
                raise ValueError("Supporting file escapes skill directory: " + name)
            try:
                file_content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raise ValueError("Skill API supporting files must be UTF-8 text; store binary media as attachments: "
                                 + name + "/" + path.relative_to(home).as_posix()) from None
            files.append({"path": path.relative_to(home).as_posix(), "content": file_content})
    return {"name": name, "description": match[1].strip().strip('"'), "content": content, "files": files}


def skill_projection(value):
    return {"name": value["name"], "description": value.get("description", ""),
            "content": value.get("content", ""),
            "files": sorted(({"path": f["path"], "content": f["content"]} for f in value.get("files", [])),
                            key=lambda item: item["path"])}


def instructions(persona):
    paths = {name: str(SKILL_ROOT / name / "SKILL.md") for name in (
        "social-content-kit", "social-interaction-dialogue", "platform-xhs")}
    bootstrap = (
        "这是独立的场景技能验收账号。按以上账号人设参与当前任务。\n"
        "每轮先读取调度Skill：" + paths["social-content-kit"] + "。当前任务已经提供完整主体时视为已加载，避免重复读取。\n"
        "普通聊天再读取：" + "、".join(paths[name] for name in (
            "social-interaction-dialogue", "platform-xhs")) + "。"
        "内容创作按调度Skill选择相关场景与辅助Skill，路径统一为 " + str(SKILL_ROOT) + "/<skill-name>/SKILL.md，引用文件相对该Skill目录读取。\n"
        "上述路径属于当前部署主机；路径不存在时，使用当前运行时实际挂载的同名Skill目录或技能发现工具找到SKILL.md。"
        "参考文件相对找到的Skill目录读取，不凭路径猜测已加载；确实不可访问时如实说明缺少能力。\n"
        "若本轮来自Multica分配任务，先只读取得当前issue及触发评论/附件，按当前任务的事实和输出契约处理；"
        "读取当前任务是内部输入获取。普通直接聊天用自然文字接话，只有任务明确指定JSON时返回其契约。\n"
        "任务明确要求结构化输出时，最终回复本身必须是完整JSON对象，不能只把JSON放在评论或文件里，"
        "然后以已提交、已完成或验收摘要作为最终回复。若任务明确需要issue评论，评论也应为同一完整JSON；"
        "不要自行修改issue状态或负责人，除非当前任务明确要求。\n"
        "表达的个性来自以上人设，记忆与本人经历来自当前事实；技能提供方法。"
        "不要把Skill加载、内部判断或验收过程当聊天正文。平台发送由已有工作台执行，当前验收任务不自行发帖或私信。"
    )
    return persona_prompt(persona) + "\n\n" + bootstrap


def unique(rows, name):
    matches = [row for row in rows if row.get("name") == name]
    if len(matches) > 1:
        raise ValueError("Multiple remote objects have this name: " + name)
    return matches[0] if matches else None


def template_projection(value):
    """Compare persistent setup without volatile idle/busy task state."""
    keys = ("id", "name", "description", "instructions", "runtime_id", "runtime_config",
            "model", "thinking_level", "max_concurrent_tasks", "service_tier")
    return {**{key: value.get(key) for key in keys},
            "skills": sorted((s["id"], s.get("enabled")) for s in value.get("skills", []))}


class Installer:
    def __init__(self, remote, state_path):
        self.remote, self.state_path = remote, state_path
        self.state = json.loads(state_path.read_text()) if state_path.exists() else {
            "schema": 1, "skills": {}, "agents": {}, "pending": {},
        }
        if self.state.get("schema") != 1:
            raise ValueError("Unsupported installer state schema")
        backup = state_path.parent / "backups" / ("social-content-kit-" + str(time.time_ns()) + ".json")
        save_json(backup, self.state)

    def save(self):
        save_json(self.state_path, self.state)

    def lookup(self, kind, name):
        rows = self.remote.request("GET", "/api/" + kind)
        if not isinstance(rows, list):
            raise ValueError("Unexpected remote list shape: " + kind)
        return unique(rows, name)

    def mutation(self, key, method, path, payload, readback, matches):
        expected = digest(payload)
        pending = self.state["pending"].get(key)
        if pending:
            if pending["sha256"] != expected:
                raise ValueError("Unresolved mutation has a different local payload: " + key)
            found = readback()
            if found and matches(found):
                self.state["pending"].pop(key)
                self.save()
                return found
            raise ValueError("Previous remote mutation remains unresolved; no retry performed: " + key)
        self.state["pending"][key] = {"sha256": expected}
        self.save()
        try:
            result = self.remote.request(method, path, payload)
        except Exception as exc:
            # Even a lost response is resolved by reads, never another POST.
            found = readback()
            if found and matches(found):
                result = found
            else:
                if hasattr(exc, "ambiguous") and not exc.ambiguous:
                    self.state["pending"].pop(key)
                    self.save()
                raise
        found = readback()
        if not found or not matches(found):
            raise ValueError("Remote readback did not match; mutation retained for reconciliation: " + key)
        self.state["pending"].pop(key)
        self.save()
        return found

    def install_skill(self, payload):
        name, expected = payload["name"], digest(skill_projection(payload))
        registered = self.state["skills"].get(name)

        def readback():
            item = (self.remote.request("GET", "/api/skills/" + registered["id"])
                    if registered else self.lookup("skills", name))
            if item and not registered:
                item = self.remote.request("GET", "/api/skills/" + item["id"])
            return item

        matches = lambda item: digest(skill_projection(item)) == expected
        item = readback()
        if item and item["name"] != name:
            raise ValueError("Registered skill identity changed: " + name)
        if item and not registered and not matches(item):
            raise ValueError("Refusing to overwrite an unmanaged skill: " + name)
        key = "skill:" + name
        if key in self.state["pending"] or not item or not matches(item):
            item = self.mutation(key, "PUT" if item else "POST",
                                 "/api/skills" + ("/" + item["id"] if item else ""),
                                 payload, readback, matches)
        record = {"id": item["id"], "sha256": expected}
        self.state["skills"][name] = record
        self.save()
        return {"name": name, **record, "verified": True, "file_count": len(payload["files"])}

    def install_agent(self, persona, template, skill_ids):
        name = AGENT_NAMES[persona]
        prompt = instructions(persona)
        fields = {"name": name, "description": "独立账号人设与可插拔场景技能的内容、聊天验收。",
                  "instructions": prompt, "runtime_id": template["runtime_id"],
                  "runtime_config": template.get("runtime_config") or {},
                  "model": template.get("model", ""), "thinking_level": template.get("thinking_level") or "",
                  "max_concurrent_tasks": template.get("max_concurrent_tasks") or 2}
        expected = digest(fields)
        registered = self.state["agents"].get(persona)

        def readback():
            item = (self.remote.request("GET", "/api/agents/" + registered["id"])
                    if registered else self.lookup("agents", name))
            if item and not registered:
                item = self.remote.request("GET", "/api/agents/" + item["id"])
            return item

        matches = lambda item: digest({k: item.get(k) if item.get(k) is not None else fields[k] for k in fields}) == expected
        item = readback()
        if item and item["name"] != name:
            raise ValueError("Registered agent identity changed: " + name)
        if item and not registered and not matches(item):
            raise ValueError("Refusing to overwrite an unmanaged agent: " + name)
        key = "agent:" + persona
        if key in self.state["pending"] or not item or not matches(item):
            create = {**fields, "visibility": "workspace", "skill_ids": skill_ids}
            # An uncertain initial POST must reconcile against the same create
            # payload even when readback now finds the newly created object.
            payload = fields if registered else create
            item = self.mutation(key, "PUT" if item else "POST",
                                 "/api/agents" + ("/" + item["id"] if item else ""), payload, readback, matches)
        self.state["agents"][persona] = {"id": item["id"], "sha256": expected,
                                          "instructions_sha256": digest(prompt)}
        self.save()

        def mounted():
            value = self.remote.request("GET", "/api/agents/" + item["id"])
            return {"skill_ids": sorted(s["id"] for s in value.get("skills", []) if s.get("enabled"))}

        wanted = {"skill_ids": sorted(skill_ids)}
        if mounted() != wanted or "agent-skills:" + persona in self.state["pending"]:
            self.mutation("agent-skills:" + persona, "PUT", "/api/agents/" + item["id"] + "/skills",
                          wanted, mounted, lambda value: value == wanted)
        self.state["agents"][persona]["skills_sha256"] = digest(wanted)
        self.save()
        return {"persona": persona, "name": name, **self.state["agents"][persona],
                "verified": True, "mounted_skill_count": len(skill_ids),
                "url": self.remote.public_url + "/" + self.remote.slug + "/agents/" + item["id"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Register only the independent acceptance objects")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "channel/.local/multica.json")
    parser.add_argument("--state", type=Path, default=SKILL_ROOT / ".local/social-content-kit.json")
    parser.add_argument("--template-agent", default=TEMPLATE_ID)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.execute:
        parser.error("Acceptance-only installation is retired. Use publish_capabilities.py for the maintained registry; identity agents and account routes are managed separately.")
    packages = [skill_package(name) for name in SKILL_NAMES]
    assert len(packages) == len(set(SKILL_NAMES))
    if not args.execute:
        print(json.dumps({"execute": False, "skills": [{"name": p["name"], "sha256": digest(skill_projection(p)),
                          "file_count": len(p["files"])} for p in packages], "agents": AGENT_NAMES}, ensure_ascii=False, indent=2))
        return
    sys.path.insert(0, str(PROJECT_ROOT / "channel"))
    from channel_service.multica import Multica
    remote = Multica(args.config)
    template = remote.request("GET", "/api/agents/" + args.template_agent)
    template_before = digest(template_projection(template))
    installer = Installer(remote, args.state)
    skills = [installer.install_skill(payload) for payload in packages]
    agents = [installer.install_agent(persona, template, [s["id"] for s in skills]) for persona in AGENT_NAMES]
    if digest(template_projection(remote.request("GET", "/api/agents/" + args.template_agent))) != template_before:
        raise ValueError("Template agent changed during installation; inspect concurrent activity")
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "verified": True,
              "template_agent_id": args.template_agent, "template_unchanged": True,
              "runtime_id": template["runtime_id"], "model": template.get("model"),
              "thinking_level": template.get("thinking_level"), "skills": skills, "agents": agents,
              "live_routes_or_automation_modified": False}
    if args.report:
        save_json(args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Unexpected transport errors may include URLs; print only their class.
        print(json.dumps({"error": str(exc) if isinstance(exc, (ValueError, FileNotFoundError)) else type(exc).__name__,
                          "writes_retried": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
