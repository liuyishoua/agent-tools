---
name: social-growth-memory
description: 社交·账号成长·整理记忆。整理当前账号的发布记录、互动事实与创作设定，保留来源并产出或保存隔离的记忆事件，不从模型推测改写人设。
---

# 社交·账号成长·整理记忆

先读取 social-content-kit 的账号档案与当前任务记录。区分 stable_profile（固定身份/风格）、creative_setting（虚拟故事设定）、published_content（实际已发作品）、interaction_fact（有对话来源的事实）和 preference_candidate（待确认）和 exploration_result（有行动证据的探索结果）。生成稿件不等于实际已发，没有receipt不能记成已发布。
每条记忆提供 account_key、event_id、kind、text、source_ref 和 evidence_status。固定身份变更只提出建议，由账号维护者确认；不能从模型回复推断年龄职业、私下关系或真实经历。
可使用 social-content-kit/scripts/account_memory.py read|append：默认隔离保存于技能目录外的私有状态，append仅写当前账号、有来源且类型有效的事件，同event_id相同内容幂等，不同内容冲突。执行时使用当前运行时可持久化的state-dir；路径不可写时交付memory_candidates并明确未保存。此工具是事件记录，不宣称跨机器自动同步或自动提取全部历史。

身份、平台和执行账号由任务/账号档案提供。只处理绑定账号资料，不读取其他账号历史；真实发送沿用已有授权和工作台执行，不由分类或记忆变更开启。
