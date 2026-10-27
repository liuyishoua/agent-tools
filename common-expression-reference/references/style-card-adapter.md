# style-alchemy 到 StyleCard 的适配

固定源码、文件hash与许可证见 [source.json](upstream-style/source.json) 和 [MIT LICENSE](upstream-style/LICENSE)。已审查上游SKILL及核心模板；实际复用 [五维分析](upstream-style/analysis-five-dimensions.md) 与 [结构化profile schema](upstream-style/style-profile-schema.md)。

逐条阅读真实样本，标注标题、开头、节奏、语言、结尾。每个风格判断连接样本中的短片段或可复查位置，缺少支持就留空。上游schema中的样例公司、事件、数字、日期、口头禅和默认参数仅解释字段，不是事实或待套用内容。

| 上游字段 | 本项目 StyleCard |
| --- | --- |
| title_craft / opening_craft / ending_craft | structure：表达动作、顺序、适用条件 |
| rhythm / tone_transitions | rhythm：句段长短与停顿、语气切换 |
| language_style 的动词/用词/标点功能 | lexicon：用词偏好与适用语境 |
| forbidden / 不适合该账号的样本特征 | avoid：本轮不采用的写法及原因 |
| formulas / templates / examples | examples：必要短摘录或明确标记的原创例子 |
| 样本定位与分析记录 | source_refs：真实页面或用户提供材料 |

只记录实际观察到的维度。次数、比例、平均值必须真数过，否则用有依据的定性说明；少量样本可做当前任务的局部风格卡，不能声称代表一个人的稳定文风。

原项目“至少5篇”“20个动词”“长报告十章”、固定CTA、默认emoji和2000字等均不作为本集成的门槛或默认值。不开接案审批、不执行normalize脚本、不自动安装依赖、不新建模仿某作者的Skill。

账号personality来自系统人设，StyleCard只表达当前内容写法；样本经历、社会关系、身份与成绩不注入账号记忆。创作完成后输出统一ContentPackage，并确认未逐句换词复刻原文。
