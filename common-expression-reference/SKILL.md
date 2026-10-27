---
name: common-expression-reference
description: 通用·表达方法·提炼参考文风。根据目标搜集并阅读参考样本，提炼结构、节奏和表达动作形成 StyleCard，再用账号自己的事实创作；用于 few-shot、找文风和有参照的文案制作。
---

# 参考驱动创作

拥有 StyleCard 与基于它写出的 ContentPackage，可复用已有 EvidencePack。人设决定谁在说，参考样本帮助决定怎样组织这次内容。

形成 StyleCard 前读取已审查的 style-alchemy [适配说明](references/style-card-adapter.md)，实际按 [五维分析](references/upstream-style/analysis-five-dimensions.md) 标注样本，按需查 [profile字段模板](references/upstream-style/style-profile-schema.md)。固定 commit、MIT 许可与文件hash见 [来源记录](references/upstream-style/source.json)；模板示例不作为事实或默认风格。

## 找对参考对象

- 输入：内容目标、context.persona、已确认事实、期望风格、样本或可检索范围、平台与篇幅。
- 优先找同类内容任务，例如“普通人运动小插曲”而非只搜“高级文案”；文体接近比粉丝量更有参考价值。
- 要学某个账号的稳定写法时比较其多条内容；要找场景写法时比较不同作者，避免把一个人的经历当通用模板。
- 实际使用搜索与阅读工具取得样本正文，记录原始页面与访问范围；提供全文的用户样本可直接使用。
- 区分样本的文案表现与传播数据；不能仅凭点赞高证明某句式有效，也不能虚构阅读量。

## 把样本变成可迁移的规则

1. 每篇标出表达动作：直接抛事件、留悬念、转折、补一个细节、表达态度、收住。不要仅贴“松弛、有网感”标签。
2. 比较开头的信息量、长短句变化、段落停顿、具体词与抽象词、是否提问和如何收尾。
3. 提炼跨样本仍成立的写法与适用条件；偶发口头禅、作者姓名和个人经历不作为必选项。
4. 将观察写进 StyleCard。examples 用少量短片段或原创示例说明写法，不保存整篇仿写模板。
5. 用任务自己的事实重新搭内容，先借叙述动作，再写句子；不沿原文逐句换同义词。
6. 对照样本和草稿：事实归属是否串了、标志性句子是否过近、节奏是否适合账号本来口吻。

## 让参考可复用

- StyleCard 写可操作关系，例如“先报结果，再补造成反差的动作”；避免“高级、真实、温暖”这种无法验收的标签。
- 记录参考中不适合账号的部分，如夸张亲密、固定喊姐妹或过多煽情，放入 avoid。
- lexicon 记录用词类型与少量适用词，不变成每篇强制出现的词库。
- 当账号口吻与参考冲突，保留结构方法，回到账号自己的词汇与立场。
- 引用必须引用时保留出处；作为新创作的正文不暗示自己就是原作者，也不借走原作者人生。
- 已有适配 StyleCard 时不重复全网搜；只有目标、场景或参考不足时补充研究。

## 输出

先返回 StyleCard，再返回 ContentPackage；外部参考附 source_refs（EvidencePack 条目）。

```json
{"style_card":{"structure":["表达动作及条件"],"rhythm":["句段与停顿关系"],"lexicon":["用词偏好"],"avoid":["不适合该账号的样本特征"],"examples":[{"text":"短片段或原创示例","origin":"source_excerpt|original","source_ref":null}],"source_refs":[]},"content":{"title":"","body":"","media":[],"source_refs":[],"claims":[],"quality":{"status":"ready|hold","observations":[],"missing":[],"reference_transfer":"借用了哪些写法"}},"source_refs":[]}
```

- source_refs 每项包含 source_url、published_at、accessed_at、observations、usage；日期未知用 null。
- 不凭空补写未读样本的 StyleCard；只能访问摘要时标清依据范围并降低结论强度。
- 内容里的事实与媒体沿用任务依据；平台字段与排版留给平台 Skill。

- 统一 ContentPackage：media 使用 path/source_url/origin/usage_rights/generated_label_required/viewed，claims 包含 text/basis/kind，quality 包含 status/observations/missing；检查完成且无缺项才 ready，否则 hold。

## 示例与验收

任务：“找几条不鸡汤的下班运动碎碎念，学它们怎么开头和收尾，再用我提供的这件小事写一条。”

独有验收：StyleCard 能指导另一件新事实的创作，最终稿保留可辨认的写法，却没有借走参考作者的经历与标志性句子。

## 账号资料边界

身份、口吻、固定视觉形象与历史由当前账号档案提供；本技能不保存专属人设。创作中的虚拟设定与现实经历分开，公开资料只作参考，不当作账号亲历。
