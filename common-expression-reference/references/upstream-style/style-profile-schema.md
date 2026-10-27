# 风格档案 Schema（Style Profile Schema）

> 风格档案是分析结果的**机器可读浓缩**——人读分析报告，机器读这份 yaml。它是"分析报告"和"生成写作 skill"之间的标准中间产物。
>
> 设计原则：**每一条都必须能追溯到样本原文**。空泛的形容词（"幽默"、"严肃"）不要写在这里，要写成可操作的规则。

---

## 1. 顶层结构

文件名：`style_profile.yaml`，放在用户指定的输出目录。

```yaml
schema_version: "1.0"
profile_id: 该账号或作者的短标识（kebab-case，会用于生成的 skill 名）
display_name: 人类可读的名字
analyzed_at: 2026-05-15            # 分析日期
sample_count: 15                    # 用了多少篇样本
sample_platforms: [公众号, 知乎]    # 样本来自哪些平台
language: zh

# 一段话画像（200字以内）
portrait: |
  ...

# 通用维度（任何文章类型都有）
title_craft: { ... }
opening_craft: { ... }
rhythm: { ... }
language_style: { ... }
ending_craft: { ... }

# 场景增量维度（根据 sample_platforms 选择性填充）
scene_extras:
  公众号: { ... }
  知乎: { ... }
  # ...

# 整体禁区
forbidden: [ ... ]

# 写作时的可调参数（生成写作 skill 时会暴露给用户）
tunables: { ... }
```

---

## 2. 通用维度详细字段

### 2.1 `title_craft` — 标题术

```yaml
title_craft:
  avg_length: 28              # 平均字符数
  length_range: [12, 45]
  info_density: high          # low | mid | high（一个标题塞几层信息）
  
  punctuation_usage:          # 各标点使用频率 0-1
    exclamation: 0.6
    question: 0.2
    quote: 0.3
    dash: 0.1
    ellipsis: 0.05
  
  number_usage_rate: 0.4      # 含精确数字的标题占比
  named_entity_rate: 0.7      # 含人名/品牌名的标题占比
  
  emotion_words:              # 高频情绪词（按频率降序）
    - { word: 炸裂, count: 5 }
    - { word: 离谱, count: 3 }
  
  formulas:                   # 可复用的标题公式（3-7 条）
    - id: f1
      pattern: "[主体]+[反常识动作]，[情绪反应]！"
      example: "OpenAI收购Astral，Python包管理神器uv现在姓O了"
      when_to_use: 突发新闻、产品发布
    - id: f2
      pattern: "[数据]，[主体]终于[动作]"
      example: "ARR冲到20亿，Cursor终于盈利了"
      when_to_use: 行业分析
  
  notes: |
    其他需要写作 skill 知道的细节（自由文本）
```

### 2.2 `opening_craft` — 开篇手法

```yaml
opening_craft:
  first_sentence_avg_chars: 18
  
  hook_distribution:          # 各类钩子占比，加起来 ≈ 1
    震惊式: 0.3
    立场式: 0.2
    反常识式: 0.2
    痛点式: 0.05
    社区式: 0.05
    引语式: 0.1
    数据式: 0.05
    场景式: 0.05
  
  preferred_hooks: [震惊式, 立场式, 反常识式]   # 前 3 名
  
  hook_templates:             # 每种偏好钩子的具体可复用句式
    - hook: 震惊式
      template: "[加粗的核心事实]。\n\n[一句极短反应]。"
      example: "**OpenAI收购Astral。**\n\n全网炸锅。"
    - hook: 反常识式
      template: "[反常识陈述]，[补一句解释悬念]。"
      example: "..."
  
  background_placement: late  # early | late（背景信息靠前还是靠后）
  pronoun_usage:              # 人称代词偏好
    second_person: high       # "你""你们" 使用程度
    inclusive_we: mid         # "我们" 使用程度
    first_person_singular: low # "我" 使用程度
```

### 2.3 `rhythm` — 段落节奏与结构

```yaml
rhythm:
  avg_sentences_per_paragraph: 1.8
  
  short_paragraph_rate: 0.35      # ≤8 字独立成段的比例
  
  rhythm_pattern: "L-L-S-I-L-S-L"  # 典型节奏序列
  rhythm_pattern_notes: |
    每 2-3 个信息段后必出一个极短段，每 4-5 段插一张图
  
  uses_subheadings: true
  subheading_style:
    info_density: high
    has_emotion: true
    example: "Cursor 撑住了，VS Code 还在追"
  
  image_frequency: "every 4-5 paragraphs"  # 自然语言描述
  
  transition_style:
    - 短句转折
    - 小标题切换
    - 图片分隔
```

### 2.4 `language_style` — 语言风格（最核心）

```yaml
language_style:
  # 动词库（至少 20 个）
  power_verbs:
    - { verb: 炸出, replaces: 发布, intensity: 5, polarity: positive, example: "..." }
    - { verb: 锤, replaces: 批评, intensity: 5, polarity: negative, example: "..." }
    # ...
  
  # 语气色板
  tone_palette:
    - tone: 正经
      ratio: 0.3
      features: 完整句、术语
      typical_context: 给数据/讲技术原理时
    - tone: 调侃
      ratio: 0.5
      features: 自创词、引号反讽、emoji
      typical_context: 评价当事人或行业现象时
    - tone: 震惊
      ratio: 0.2
      features: 感叹号、加粗、极短句
      typical_context: 开篇或转折处
  
  tone_transitions:           # 语气如何切换
    - "开篇通常震惊 → 中段降到正经讲事实 → 结尾回到调侃"
  
  # 标点叙事规则
  punctuation_rules:
    bold:
      function: 信息锚点 + 情绪强调
      density: high
      examples: ["**OpenAI收购Astral**"]
    dash_em:                  # —— 破折号
      function: 制造悬念
      density: mid
    ellipsis:                 # ……
      function: 留白讽刺
      density: low
    quote_chinese:            # 「」 / ""
      function: 概念高亮 + 反讽
      density: high
  
  # 口头禅与惯用表达
  signature_phrases:
    - { phrase: "怎么说呢", context: 引出评论 }
    - { phrase: "属实", context: 强调判断 }
    - { phrase: "划重点", context: 段首提示 }
    - { phrase: "这不，", context: 引出新事件 }
    # 至少 10 条
  
  # 技术概念处理（如果适用）
  technical_concept_handling:
    style: 必配类比
    analogy_domains: [日常生活, 游戏, 影视]
    example: "Transformer 就像一个超大型的"完形填空"机器"
  
  # 自创词典
  custom_vocabulary:
    - { word: "量子君", meaning: 编辑部自称 }
    - { word: "硅基生命", meaning: AI 模型的拟人化称呼 }
```

### 2.5 `ending_craft` — 结尾模式

```yaml
ending_craft:
  ending_type_distribution:
    one_more_thing: 0.3
    poetic_summary: 0.1
    open_question: 0.2
    cta: 0.3
    summary: 0.1
  
  preferred_endings: [one_more_thing, cta]
  
  ending_templates:
    - type: one_more_thing
      template: "One More Thing：\n[一个延伸事实或彩蛋]"
      example: "..."
    - type: cta
      template: "[固定的关注引导]"
      example: "..."
  
  has_fixed_cta: true
  fixed_cta_text: "—— 完 ——\n\n关注量子位，第一时间获取..."
```

---

## 3. 场景增量维度

只在样本平台对应的 key 下填充。其他 key 留空或省略。

```yaml
scene_extras:
  
  公众号:
    has_brand_header: true
    has_brand_footer: true
    community_naming: { reader: 量子位朋友, editor: 量子君 }
    fixed_sections: [一线, 报道, ...]   # 固定栏目
    cta_position: 文末固定
  
  知乎:
    answer_opening_strategy: [先抛结论, 立场鲜明]
    credential_display: high           # 是否爱秀背景
    debate_posture: 引战 | 调和 | 中立
    formatting: { bold_heavy: true, uses_lists: true }
  
  小红书:
    emoji_density: high
    emoji_typical: [✨, 💡, 🔥]
    tag_strategy: 文末密集
    persona_implant: high              # 人设植入强度
    line_break_style: 极短行
  
  Twitter_X:
    thread_strategy: 1/N 串
    sentence_per_tweet: 1-2
    quote_tweet_usage: high
    hashtag_strategy: low | high
  
  博客_严肃:
    argument_structure: 总分总 | 层进 | 反驳式
    citation_style: 链接 | 脚注 | 内嵌
    para_length: long
  
  学术:
    citation_format: APA | GB/T 7714 | 其他
    abstract_style: 结构式 | 叙事式
    hedging_density: high              # "可能""或许"使用频率
    term_density: high
  
  个人散文:
    imagery_density: high
    sensory_word_distribution: { 视觉: 0.4, 听觉: 0.2, 触觉: 0.2, 嗅味觉: 0.2 }
    rhythm_preference: 缓慢 | 急促
    first_person_density: very high
```

---

## 4. 禁区与可调参数

```yaml
forbidden:
  - 学术腔（如"综上所述""本研究表明"）
  - 官方通稿语气
  - 长复合句堆砌
  - 滥用感叹号（每段 >1 个）

tunables:                # 生成的写作 skill 会暴露给用户调节
  intensity:             # 风格强度 0-1（0=轻度致敬，1=完全模仿）
    default: 0.7
    description: 风格强度。低时只学结构，高时连口头禅都用上。
  
  formality:             # 正式度 0-1（覆盖 tone_palette）
    default: 0.3
  
  emoji_enable:
    default: false
    description: 是否使用 emoji（小红书风格档案默认 true）
  
  length_target:
    default: 2000
    description: 目标字数
```

---

## 5. 完整最小可用示例

```yaml
schema_version: "1.0"
profile_id: qbitai
display_name: 量子位
analyzed_at: 2026-05-15
sample_count: 15
sample_platforms: [公众号]
language: zh

portrait: |
  量子位是一个以"硬核 AI 资讯 + 强烈情绪化语言"为特色的科技自媒体。
  标题信息密度极高，开篇必带震惊感，段落节奏快、极短句频繁。
  动词偏好"力量型"（炸/锤/封神），语气在调侃和震惊之间快速切换。
  读者粘性来自"量子君""硅基生命"等自创词构成的社群语言。

title_craft:
  avg_length: 28
  info_density: high
  punctuation_usage: { exclamation: 0.6, question: 0.2 }
  emotion_words:
    - { word: 炸裂, count: 5 }
  formulas:
    - id: f1
      pattern: "[主体]+[反常识动作]，[情绪反应]！"
      example: "OpenAI收购Astral，Python包管理神器uv现在姓O了"
      when_to_use: 突发新闻

# ... 其余字段省略
```

---

## 6. 字段填充规则

| 规则 | 说明 |
|------|------|
| 不要瞎编 | 任何一个 `example` 字段必须是真的从样本里摘的原文 |
| 不要全部填满 | 没观察到的字段留空（删掉 key），不要硬凑 |
| 数字要可验证 | `ratio`、`count`、`rate` 必须能从样本统计出来，不能拍脑袋 |
| `intensity 1-5` 用 5 档 | 1=最弱 5=最强 |
| 比例字段加起来 ≈ 1 | `hook_distribution`、`tone_palette.ratio`、`ending_type_distribution` 总和应该在 0.9-1.1 之间 |
