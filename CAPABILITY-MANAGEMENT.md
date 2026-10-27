# 人物 Agent 与业务技能管理

一个人物/业务身份对应一个 agent；身份与历史集中管理，平台执行账号保持隔离。业务域和能力类别是筛选标签，具体任务才是可执行 skill。

## 技能清单

| 中文业务名称 | 稳定技能名 | 层级 | 复用来源 |
|---|---|---|---|
| 社交·作品创作·人物图文 | social-creation-person | 业务任务 | content-self-presentation |
| 社交·作品创作·场景图文 | social-creation-scene | 业务任务 | content-place-story |
| 社交·作品创作·日常故事 | social-creation-story | 业务任务 | content-daily-story |
| 社交·作品创作·经验攻略 | social-creation-guide | 业务任务 | content-experience-guide |
| 社交·作品创作·热点改编 | social-creation-trend | 业务任务 | content-trend-remix |
| 社交·社交互动·回应对话 | social-interaction-dialogue | 业务任务 | content-social-reply |
| 交易·商品管理·展示商品 | trade-product-present | 业务任务 | content-item-showcase |
| 通用·素材处理·查找图片 | common-material-find | 辅助方法 | content-visual-asset-scout |
| 通用·素材处理·改造图片 | common-material-edit | 辅助方法 | content-visual-remix |
| 通用·资料研究·研究生活场景 | common-research-scenes | 辅助方法 | content-lived-scene-research |
| 通用·表达方法·提炼参考文风 | common-expression-reference | 辅助方法 | content-reference-writing |
| 通用·表达方法·润色文案 | common-expression-polish | 辅助方法 | content-grounded-humanize |
| 通用·资料研究·研究热点 | common-research-trends | 辅助方法 | content-trend-radar |
| 社交·内容策划·安排选题 | social-planning-topics | 业务任务 | 新补齐 |
| 社交·内容验收·检查图文 | social-quality-check | 业务任务 | 新补齐 |
| 社交·账号成长·复盘表现 | social-growth-review | 业务任务 | 新补齐 |
| 社交·账号成长·整理记忆 | social-growth-memory | 业务任务 | 新补齐 |
| 交易·商品管理·创建商品 | trade-product-create | 业务任务 | 新补齐 |
| 交易·商品管理·维护商品信息 | trade-product-maintain | 业务任务 | 新补齐 |
| 交易·买家沟通·解答咨询与议价 | trade-buyer-dialogue | 业务任务 | 新补齐 |
| 交易·经营分析·分析经营反馈 | trade-business-review | 业务任务 | 新补齐 |
| 平台·小红书·适配交付 | platform-xhs | 平台适配 | 保留 |
| 平台·闲鱼·适配交付 | platform-xianyu | 平台适配 | 保留 |
| 通用·任务调度·选择业务技能 | social-content-kit | 调度入口 | 保留 |
| 通用·素材处理·搜索表情 | gifgrep | 辅助方法 | 保留 |

| 社交·账号成长·主动探索 | social-growth-explore | 业务任务 | 新补齐 |

## 新增准入

每个技能需有独立输入、明确交付和可独立维护的方法。新增账号、题材、地点、消息入口优先采用参数；不要复制同一套技能。共享研究、素材、表达是辅助方法，按需读取。平台交付不承担账号身份。

## 账号资料与记忆

小桃稳定资料唯一来源：social-content-kit/assets/personas.json 的 xiaotao；agent 指令仅引用它。人物固定形象尚缺参考，不能宣称已建立视觉连续性；不依赖固定形象的日常创作仍可自动完成。闲鱼业务身份以真实执行账号为准，不假定多个账号是同一个人。

记忆工具 social-content-kit/scripts/account_memory.py 按账号保存有来源事件，固定档案与成长事件分开。草稿不得记成已发布，虚拟设定不得记成现实亲历。工具已实现本地隔离事件存储；跨机器同步、自动抓取全历史未实现。

## 迁移和平台边界

语义重命名保留Multica skill ID，已有绑定因此不丢失；vendor原文、许可证及来源哈希保留。工作台通过账号 Agent 单选绑定业务；旧兼容入口从维护目录移除，旧验收 Agent 在确认无运行任务和队列依赖后归档，历史任务保持原归属。

小红书旧自动下载器只接受Pexels数字ID，生成图片需要支持本地图片的发布链路，本次未扩展。闲鱼真实发布/消息均未测试；商品PATCH只维护本地备注标签，不能冒充平台改价。留言回复当前源码已有实现，账号实际可用需能力检查。

此重构不启用关闭的自动化，不真实发帖、发布商品或发送消息。

主动探索已定义并绑定，结果可经本地记忆交给下一次选题/行动；未开启调度器或持续探索服务。

## 已部署结果

身份 agent 的展示名称统一为“平台-平台账号真实昵称”。小桃生产内容 agent 保留原ID，名称为“小红书-小桃先吃一口”，统一挂载业务能力、共享方法与小红书交付；主动探索归“社交账号经营 / 账号成长 / 主动探索”，与记忆、复盘并列。旧小桃验收身份确认无未完成任务或队列依赖后归档。Leo 独立身份沿用原ID，展示名称为“小红书-leo”，挂载同一套社交业务能力、共享方法和平台适配；档案键与长期记忆键固定为 xhs-leo，与小桃隔离。未提供的个人背景保留未知，不把小桃的人设复制进来。

闲鱼“福来day”和“liuyishou”各有一个业务身份 agent，展示名称为“闲鱼-福来day”和“闲鱼-liuyishou”，挂载商品创建/维护/展示、买家沟通与经营分析。工作台私信、评论、内容模型和监控路由已迁移；保持原enabled、auto_reply、control_mode及验证阻塞。户外号原身份和禁用的自动化保持原样，只更新共享技能引用。

管理入口为 social-content-kit/scripts/publish_capabilities.py；支持语义重命名保持skill ID、写意图记录与读后核验。旧验收安装器和旧小桃/通用私信设置脚本已停止执行，避免重跑覆盖身份架构。账号资料和生产绑定分别维护，发布技能不自动改变账号路由。

小红书工作台的私信/评论起草可使用 social-content-kit/scripts/compose.py 一次读取绑定档案和对话、平台技能；独立快照任务使用其提供的 memories。只需最终 JSON 的任务直接返回，不重复写文件或 issue 评论。部署该指令使用 `python3 social-content-kit/scripts/optimize_reply_agents.py --execute`，不带参数先检查目标；原指令备份保存在 `~/.local/state/leo-capability-rebuild/reply-optimization-backup.json`。该入口只维护两个指定的小红书身份的回复指令及上述共享技能，不改变模型、执行节点、路由或发送模式。

技能全文和支持资源已发布并读回核验；完整Channel与闲鱼临时/demo测试通过。真实账号路由投影在内存中验证，未提交真实事件。未真实发帖、商品发布或测试发送私信；未创建新的定时任务。

### 小桃日常笔记发布控制

小桃日常笔记采用持续授权的自动创作、自检和发布，不逐篇等待人工审核；人物档案 `xiaotao.publishing_policy` 维护该规则。默认执行身份为 owner 1 / 小红书用户 `60d73b36000000002002dc93`，PC 账号 2 与 Creator 账号 3 是同一人的不同端绑定。任务省略重复账号字段时继承默认绑定，由执行端自动核验。正文不强制添加虚拟人物或 AI 身份说明，平台实际要求的素材标识和署名按要求处理。真实执行故障与结果未知仍需如实记录、查询核验，不能据此假报成功或重复发布。此授权不改变其他账号，也不把明确仅要求 JSON 起草的互动任务变为真实发送。
