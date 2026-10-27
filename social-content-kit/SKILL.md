---
name: social-content-kit
description: 通用·任务调度·选择业务技能。为账号选择并组合人物展示、场景记录、日常故事、攻略、商品、热梗和互动Skill；将稳定人设、任务事实、实时参考与平台交付分别注入，适用于跨账号内容与聊天。
---

# 账号的内容与聊天调度

账号系统指令提供“谁在说话”：已确认身份、偏好、独立判断、关系边界和表达习惯。当前任务提供“这次有什么”：实际经历、照片、商品、聊天快照、目标、平台和输出契约。外部样本提供可借鉴的方法，不增加主人事实。

人设格式见 [persona.schema.json](references/persona.schema.json)。`assets/personas.json` 提供两个验收示例，新账号使用自己的profile。`scripts/compose.py --persona <账号键> --persona-file <账号JSON> --scene <场景> --platform xhs --brief <目标>` 可编译系统人设和本轮所选Skill，二者分别返回，不修改全局身份文件。

先判断这轮的主角，再选一个主场景Skill；复合任务才增加第二个。城市徒步、咖啡馆和健身是题材，不据关键词建一个包办所有制作的新Skill。

| 内容依靠什么成立 | 主Skill |
| --- | --- |
| 人物与个人生活形象 | social-creation-person |
| 地点、风景、户外画面 | social-creation-scene |
| 日常事件、观察、反差或笑点 | social-creation-story |
| 方法、经验、路线或取舍 | social-creation-guide |
| 物品与交易信任 | trade-product-present |
| 当下话题与梗的改编 | social-creation-trend |
| 对方来话与关系上下文 | social-interaction-dialogue |

缺素材才加 common-material-find；需要改图加 common-material-edit；需要生活细节加 common-research-scenes；参考创作加 common-expression-reference；已成稿的人化加 common-expression-polish；需要确认近期热度加 common-research-trends。平台输出选 platform-xhs 或 platform-xianyu。每轮只读选中的Skill，已有完整正文时不重复加载。

聊天先回应这句话，不每轮做内容研究或联网追梗。已有共同话题、对方明确细节比陌生热梗更有用。用 persona 提供的态度形成自己的反应；新偏好以 memory_candidates 留待核实，不凭上一轮自动生成内容改写人设。

私信/评论已确定使用 social-interaction-dialogue 与 platform-xhs 时，可直接运行 `python3 <本技能目录>/scripts/compose.py --persona <当前账号档案键> --scene reply --platform xhs --brief '按当前任务契约回应'`，一次取得该账号档案与这两份技能全文。输出的 selected_skills 已加载，不再逐个 cat 或重新读本调度入口；此命令只编译资料，不执行平台动作。当前任务明确使用独立快照时，记忆使用 context.memories，不扫描旧任务或另一个执行目录的记忆库。需要长期记忆的其他任务仍按账号读取 `scripts/account_memory.py read --account <档案键>`。

Multica 工作台回复任务需读取 issue 时，使用 `python3 <本技能目录>/scripts/reply_input.py --issue <当前issue ID> --persona <当前账号档案键>`，将实际 issue 读取和上述编译合并到一次工具调用。完整任务正文保留在 issue.description，按其账号和快照核对后处理；脚本不扫描历史、不写评论、不执行发送。

统一任务格式见 [content-task.schema.json](references/content-task.schema.json)，中间产物示例见 [contracts.json](references/contracts.json)。它们用于传递来源、事实和选择，面向读者只交成品。独立聊天用普通消息；工作台任务按其 mode 输出JSON。样稿可以在本地预览；真实发送沿用任务已有授权及账号绑定。

示例：“同一组城市散步素材，给两个账号各做一条，再回一条评论。”先按两个persona分别确定观点；共用研究/素材能力，输出两个内容包。验收：同题材能看出两种人格，事实与来源一致，没有只换昵称。

## 统一管理与身份来源

人物账号对应一个业务身份 agent。稳定资料集中在本技能 assets/personas.json，键 xiaotao/outdoor；生产 agent 读取档案，不复制内容到多个prompt。任务账号与档案绑定必须先核对；人物成长使用 social-growth-memory，现实记录和虚拟设定分开。固定人物参考尚未提供时明确缺项。

策划用 social-planning-topics；成稿审核用 social-quality-check；反馈复盘用 social-growth-review；记录整理用 social-growth-memory。分类与旧新对应见 references/capability-registry.json，分类本身不是执行技能。

每项新技能需说明独立输入、可交付结果、区别于已有方法的业务决策。新增账号、题材、场景或消息入口优先用参数；没有独立契约或方法差异不拆新技能。辅助素材/研究/表达仅按需调用；不每轮叠加近似对话规则。

主动探索用 social-growth-explore。先读取当前账号未完问题与实际结果，一次只做可验证研究或本地实验；结果经记忆入口影响下一次选题，不自动开启持续任务或发布。
