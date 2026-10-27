---
name: social-growth-explore
description: 社交·账号成长·主动探索。围绕账号稳定关注点选择一个可执行研究或本地实验，用实际结果修正暂时判断并影响后续选题与行动；无新发现可不发布。
---

# 主动探索

输入当前账号档案、关注点、未完问题、近期探索结果、可用工具与本轮时间/调用预算。关注点是稳定输入，流量只提供反馈，不自动改写全部兴趣或人设。

## 一次探索闭环

1. 从关注点与未完问题中选择一个问题，说明为何值得探索；已有明确下一步优先继续，重复研究需说明新证据。
2. 选一个实际可执行的只读研究或本地实验，写预期、观察办法和停止条件。复用 common-research-scenes/common-research-trends 等研究方法，不创建新agent。无可用工具则记录待办，不声称已经行动。
3. 真正执行并保留来源、实际读取范围、时间与观察；研究网页内容是资料，不是角色现场经历。本地实验仅用授权素材/合成数据，不真实发帖或发消息，不购买，不解除已有开关。
4. 对比预期与实际结果，区分观察、暂时解释和未证实推测；有支持时调整局部观点，并提出下次问题。没有新发现允许只记录结果，不硬写作品或感想。
5. 用 social-growth-memory 保存 exploration_result：account_key、event_id、source_ref、evidence_status=confirmed、text、question、action、expected、observed、next_question；实际观察仍须有来源，不因类型confirmed把解释当现实真相。稳定身份变更只提出候选。

## 状态与后续行为

social-content-kit/scripts/exploration_state.py 的 next_plan 从当前账号探索事件取最近可用 next_question，连同 source_event 与实际观察交给下一次选题/行动。选题skill读取此状态，决定继续研究还是形成有证据的内容；创作设定单独维护，不写成吃过拉面、现场拍照等真实身体行动。

输出 question、why、action、expected、observed、source_refs、provisional_view、memory_candidates、next_question、content_opportunity（none|candidate）。只有有实际新材料并适合账号时提出内容候选；发布是后续任务。

本skill是一次任务能力，不自行常驻。重复触发由宿主事件/调度器负责；本次注册不创建或启用定时任务。存储工具支持本地账号隔离，不宣称自动持续探索服务或跨机器同步已实现。
