---
name: common-expression-polish
description: 通用·表达方法·润色文案。结合账号语气、已确认事实与同场景生活观察，把模板化草稿改得具体自然，保留原意与信息；用于文案人化，区别于仅删“AI味”词汇。
---

# 有依据的文案人化

拥有改写后的 ContentPackage 与内部改动依据。目标是让这个账号对这件事有具体反应，不能靠加“哈哈、姐妹、谁懂”制造人感。

成稿诊断实际使用已审查的 humanizer-zh 参考：先读 [适配说明](references/humanizer-adapter.md)，按问题查 [中文句式诊断](references/upstream-humanizer/sentence-diagnostics.md)。固定 commit、MIT 许可与文件hash见 [来源记录](references/upstream-humanizer/source.json)；不加载上游名家voice与长文流程。

## 读懂草稿与事实边界

- 输入：原稿、context.persona、确认事实、相关媒体、最近表达、可用 StyleCard 和 EvidencePack。
- 先用一句内部笔记说清原稿真正想传达什么；保留必要结论、关键条件和事实关系。
- 判断生硬来源：说得太泛、解释太满、段落过于对称、每段都升华、情绪无对象，或口吻与账号冲突。
- 需要生活细节时调用 common-research-scenes；需要文体样本时调用 common-expression-reference，不机械要求每次都联网。
- 研究来的细节只在适当视角使用。不能为“生动”新增主人动作、时间、地点、亲密关系或购买体验。

## 按原因修稿

1. 先修观点和注意力：找账号对这件事最在意的一处，让它成为正文的具体中心。
2. 泛泛感受换成有依据的观察或选择；没有可用细节就把表达缩短，不编一个生活桥段。
3. 让信息按自然注意顺序出现：先说此刻最想说的，再补读者需要的背景；无需统一“背景—建议—感悟”。
4. 删去重复结论、无功能过渡与解释笑点的句子；保留必要条件，避免把准确内容改成含糊口语。
5. 用账号词汇和停顿重新写句子。允许长短变化与留白，不故意错字、乱标点或模仿打字失误。
6. 对照原稿逐条检查事实和意思；若为纠错而改变结论，内部注明依据，不悄悄改变用户观点。

## 检查这个账号是否会这样说

- 人设中的个性体现为选择和判断，例如“喜欢走平路”可以很明确，无需用夸张反差把每条写成段子。
- 不强迫每条正能量、每条提问、每条升华；结尾在表达完成处停住。
- 幽默沿已存在的事情发展，不把情绪低落的内容自动变成轻松梗。
- 表情、方言和流行语只在账号与场景适用时使用；真实样本中的惯用词也不要求每篇复现。
- 对照最近内容检查机械重复，尤其是开头、同一个口头禅和互动结尾；更换观察方式比换同义词有效。
- 不承诺“检测不出AI”或给虚构真人感分数；以可观察的表达与事实检查说明质量。

## 输出

返回改写后的 ContentPackage；必要时复用原媒体与 source_refs，不伪造新素材。

```json
{"title":"","body":"最终改稿","media":[],"source_refs":[],"claims":[{"text":"保留的事实","basis":"原稿确认信息或新依据","status":"confirmed","kind":"verified_fact|preference|creative"}],"quality":{"status":"ready|hold","observations":[],"missing":[],"main_reaction":"账号具体反应","changes":[{"before_problem":"具体问题","after_method":"实际改法","basis":"任务事实/StyleCard/场景观察"}],"meaning_preserved":true}}
```

- 新增外部观察时附 EvidencePack：source_url、published_at、accessed_at、observations、usage。
- 原稿本来已自然就做必要的小改，不能为证明工作量强行重写。
- 返回最终稿，不把诊断清单、候选和内部资料说明混入正文；平台排版交给平台 Skill。

- 统一 ContentPackage：media 使用 path/source_url/origin/usage_rights/generated_label_required/viewed，claims 包含 text/basis/kind，quality 包含 status/observations/missing；检查完成且无缺项才 ready，否则 hold。

## 示例与验收

任务：“这篇散步文案太像公众号，保留树影很好看这个事实，改成一个普通上班族顺口会发的两三句。”

独有验收：改稿有一个具体而符合账号的反应，原意和事实仍在，删去表情和流行语后也不退回模板腔。

## 账号资料边界

身份、口吻、固定视觉形象与历史由当前账号档案提供；本技能不保存专属人设。创作中的虚拟设定与现实经历分开，公开资料只作参考，不当作账号亲历。
