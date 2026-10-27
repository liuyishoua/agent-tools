# 开源机制与选型记录

核对日期：2026-10-11。只读审查公开文档、GitHub 主源与 SkillHub 下载包；没有运行这些产品，也没有把私聊数据库导入生产。本 Skill 的指令和验收情境均为原创。

## 可借鉴的成熟产品机制

| 主源 | 已核对能力与许可 | 在本 Skill 中的应用 |
| --- | --- | --- |
| [SillyTavern character design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)、[源码许可](https://github.com/SillyTavern/SillyTavern/blob/release/LICENSE) | 角色身份、人格、情境、首句与多轮示例分开；项目 AGPL-3.0。是产品，不是即装即用的聊天 Skill | 人设由账号注入；带上下文的说话样本用于定节奏；没有复制其角色台词或实现代码 |
| [SillyTavern World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/) | 关联信息可按角色、用户 persona 与聊天挂载，并按关键词或相似度触发 | 相关共同记忆按关系作用域提供，避免整库塞进每轮；本 Skill 不实现检索服务 |
| [Character Card V2](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md) | 卡格式有 description、personality、scenario、mes_example、角色 lorebook 等字段；仓库未发现独立许可文件，GitHub license 元数据为空 | 参考字段区分方法，不将社区角色卡视为默认可商用素材，不复制未授权内容 |
| [Letta Code](https://github.com/letta-ai/letta-code)、[persona 源码](https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/persona.mdx)、[human 源码](https://github.com/letta-ai/letta-code/blob/main/src/agent/prompts/human.mdx) | 当前活跃源码在 letta-code，Apache-2.0；persona 与 human 记忆分开，有持久记忆、消息检索与 MemFS | 稳定自我与对方信息分离；记忆候选带来源，事实变化可纠正；本次未接入 Letta 运行时 |
| [AIRI](https://github.com/moeru-ai/airi)、[关系与个性提示源](https://github.com/moeru-ai/airi/blob/main/integrations/satori-bot/src/core/planner/prompts/personality-v1.velin.md)、[许可](https://github.com/moeru-ai/airi/blob/main/LICENSE) | MIT；同一人格对不同关系有不同取向，表达随情境与轻重变化。是完整陪伴产品 | 个性来自关心什么、怎么选择；同一人不会所有情境只有一个语气。没有复制动漫角色、身份设定或固定句式 |

上表支持的是产品机制存在，不证明这些产品在中文小红书上已经达到目标自然感。自然感需由本账号、多轮真实运行和用户检查确认。

## SkillHub 的实物检查

检索使用公开 `GET /api/skills`，关键词覆盖“人格、聊天、陪伴、对话、persona、character、conversation、memory”；按场景过滤后只读下载以下四包。目录与包内容不是同一质量保证。

| 技能 | 只读结果 | 采用决定 |
| --- | --- | --- |
| [聊天 chat-toolkit-free](https://skillhub.cn/skills/chat-toolkit-free)，1.1.2 | frontmatter 声明 MIT；包只有规范文本与元数据。主体混有营销场景、付费表格、无依据效果数字，输出示例非合法 JSON；没有可复用的多轮接话机制 | 不集成 |
| [三色人格陪伴](https://skillhub.cn/skills/threeperson)，3.3.1 | 有多角色文件与独立记忆思路，主规范主要为产品说明，并附身份水印；下载包未发现显式 LICENSE | 借鉴关系记忆分离的思路，未复制或安装 |
| [角色个性管理](https://skillhub.cn/skills/character-handler-skill)，1.0.0 | 通过完整覆盖全局 SOUL.md 切换角色；下载包未发现显式许可 | 不适合一个运行时管理多个账号的人设注入方式，不集成 |
| [conversation-memory](https://skillhub.cn/skills/conversation-memory)，1.0.0 | 标注源于 Apache 2.0 项目，但未附许可文本；中文规范在第一条原则中断，剩余多为模式名称，未提供存储或检索实现 | 不把它宣称为可运行的记忆能力，不集成 |

接话动作、误解修复、媒体语义与自然停止设计统一由 `social-interaction-dialogue` 处理，平台媒体和发送契约由 `platform-xhs` 适配。账号人设和事实取自当前账号档案与上下文，避免重复加载旧入口或混入其他账号身份。
