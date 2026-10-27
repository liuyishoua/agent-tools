#!/usr/bin/env python3
"""Apply scoped reply instructions without changing models, routes or sending modes."""
import argparse
import json
from pathlib import Path
import sys

from install_multica import Installer, save_json, skill_package

PROJECT = Path(__file__).resolve().parents[3]
TARGETS = {
    "da72f33e-cac4-4ff0-a99d-d415219f3efc": ("小红书-leo", "xhs-leo"),
    "05f361ac-72f8-456a-9a89-31b31db57dff": ("小红书-小桃先吃一口", "xiaotao"),
}
MARKER = "\n\n## 工作台私信与评论的资料读取和交付\n"


def reply_instructions(original, profile):
    base = original.split(MARKER, 1)[0]
    return base + MARKER + (
        "以下只适用于工作台的私信/评论回复起草，其他创作、研究、记忆任务沿用上面的流程。\n"
        "首次资料读取用下面的一个工具调用取得当前 issue 和技能资料，再核对绑定账号。只用该任务允许的上下文；"
        "明确独立快照的任务以 context.messages/context.memories 为准，不另查旧任务或本地记忆库。\n"
        "本轮已确定回应对话能力：定位已挂载 social-content-kit 目录后，直接运行 "
        "python3 <该目录>/scripts/reply_input.py --issue <当前issue ID> --persona " + profile + "。"
        "该脚本实际执行 multica issue get，并一次取得完整任务正文、当前账号档案及 "
        "social-interaction-dialogue、platform-xhs 全文；"
        "这满足上面的任务/档案/业务技能读取要求，不再额外 issue get 或逐个 cat 已加载技能、调度入口或整份多账号档案。"
        "路径不存在时按上面的运行时技能发现方式找到同名目录，不猜测已加载。\n"
        "工作台明确独立快照且只需最终 JSON 的任务，资料只读该冻结请求："
        "禁止额外执行独立 multica issue get 或 multica issue comment list；"
        "reply_input.py 已实际取得完整任务，不重复读取，不发加载技能/计划说明。"
        "此 Agent Identity 对资料范围和交付方式的限定优先于通用 issue 工作流。"
        "附件已在当前执行输入提供时直接查看；需要补取的实际图片才用附件工具，"
        "不为未选用的表情候选反复查询命令帮助。选用媒体仍须实际查看，不按标签猜图。\n"
        "任务明确只需最终 JSON、无需发表评论时，直接在最终回答返回完整对象。"
        "不要另写 reply.json、调用 json.tool、发相同 issue 评论或再查状态/负责人；"
        "这些任务没有要求的写入和核验不属于回复起草。只有明确要求评论/文件交付时才执行。"
        "内部分析和技能加载过程不输出给对话对象；保持账号事实、授权边界与工作台输出契约。\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--config", type=Path, default=PROJECT / "channel/.local/multica.json")
    parser.add_argument("--state", type=Path, default=Path.home() / ".local/state/leo-capability-rebuild/publish-state.json")
    parser.add_argument("--backup", type=Path, default=Path.home() / ".local/state/leo-capability-rebuild/reply-optimization-backup.json")
    args = parser.parse_args()
    sys.path.insert(0, str(PROJECT / "channel"))
    from channel_service.multica import Multica
    remote = Multica(args.config)
    agents = []
    for agent_id, (name, profile) in TARGETS.items():
        agent = remote.request("GET", "/api/agents/" + agent_id)
        if agent["name"] != name:
            raise ValueError("Account agent identity changed: " + agent_id)
        agents.append((agent, reply_instructions(agent["instructions"], profile)))
    if not args.execute:
        print(json.dumps([{"id": a["id"], "name": a["name"],
                           "changed": a["instructions"] != prompt} for a, prompt in agents], ensure_ascii=False))
        return
    if not args.backup.exists():
        save_json(args.backup, [{"id": a["id"], "name": a["name"],
                                 "instructions": a["instructions"]} for a, _ in agents])
    installer = Installer(remote, args.state)
    for name in ("social-content-kit", "platform-xhs"):
        installer.install_skill(skill_package(name))
    for agent, prompt in agents:
        agent_id = agent["id"]
        installer.mutation(
            "reply-instructions:" + agent_id, "PUT", "/api/agents/" + agent_id,
            {"instructions": prompt},
            lambda agent_id=agent_id: remote.request("GET", "/api/agents/" + agent_id),
            lambda found, prompt=prompt: found.get("instructions") == prompt,
        )
        print("Verified reply instructions:", agent["name"])


if __name__ == "__main__":
    main()
