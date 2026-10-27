#!/usr/bin/env python3
"""Compile a persona and selected skills without mixing account identities."""
import argparse
import hashlib
import json
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ROOT = KIT.parent
SCENES = {
    "self": "social-creation-person", "place": "social-creation-scene",
    "daily": "social-creation-story", "guide": "social-creation-guide",
    "item": "trade-product-present", "trend": "social-creation-trend",
    "reply": "social-interaction-dialogue",
}
SUPPORT = {
    "assets": "common-material-find", "remix": "common-material-edit",
    "life-research": "common-research-scenes", "references": "common-expression-reference",
    "humanize": "common-expression-polish", "trends": "common-research-trends",
}


def skill_body(name):
    text = (ROOT / name / "SKILL.md").read_text()
    return text.split("---", 2)[2].strip()


def persona_prompt(key, persona_file=None):
    profiles = json.loads(Path(persona_file or KIT / "assets/personas.json").read_text())
    persona = profiles if "identity" in profiles else profiles[key]
    return "\n".join([
        persona["identity"], "偏好：" + "；".join(persona["preferences"]),
        "态度：" + "；".join(persona["attitudes"]), "表达：" + persona["voice"],
        "已经确认的本人事实：" + ("；".join(persona["known_facts"]) or "本轮任务另行提供"),
        "尚未确认：" + "、".join(persona["unknown_facts"]), persona["boundaries"],
        "偏好可以直接表达；本人经历和现实行动须由本轮记录支持。不要为有个性捏造履历。",
    ])


def compose(persona, scene, platform, support=(), brief="", context=None, persona_file=None):
    selected = [SCENES[scene]]
    selected.extend(SUPPORT[name] for name in support)
    selected.append("platform-" + platform)
    selected = list(dict.fromkeys(selected))
    sections = []
    hashes = {}
    for name in selected:
        body = skill_body(name)
        hashes[name] = hashlib.sha256(body.encode()).hexdigest()
        sections.append("\n## 当前已加载 Skill：" + name + "\n" + body)
    return {
        "persona": persona, "scene": scene, "platform": platform, "selected_skills": selected,
        "skill_hashes": hashes, "system_prompt": persona_prompt(persona, persona_file),
        "task_prompt": "\n".join(sections) + "\n\n## 本轮任务\n" + brief +
                       "\n\n## 本轮事实与素材\n" + json.dumps(context or {}, ensure_ascii=False),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persona", required=True, help="Account profile key; shipped examples: xiaotao, outdoor")
    parser.add_argument("--persona-file", type=Path, help="External account profile or keyed profile registry")
    parser.add_argument("--scene", choices=SCENES, required=True)
    parser.add_argument("--platform", choices=["xhs", "xianyu"], required=True)
    parser.add_argument("--support", choices=SUPPORT, action="append", default=[])
    parser.add_argument("--brief", required=True)
    parser.add_argument("--context-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    context = json.loads(args.context_file.read_text()) if args.context_file else {}
    result = compose(args.persona, args.scene, args.platform, args.support, args.brief, context, args.persona_file)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
