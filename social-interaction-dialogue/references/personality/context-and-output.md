# 人设输入与输出约定

以下是宿主可提供的信息，不要求用户填写表格。字段已有别名时沿用实际任务格式。

| 信息 | 用途 |
| --- | --- |
| `account_id`、`contact_id` | 账号与关系范围；记忆按二者隔离 |
| `persona.identity` | 已确认身份与经历事实 |
| `persona.preferences`、`persona.values` | 有内容的偏好与取舍，例如更愿意边走边看景、讨厌专门排队打卡 |
| `persona.expression_examples` | 原主人或明确创作的人设样本，含前文及来源；不是只有口头禅 |
| `persona.unknowns`、`availability` | 当前不能确认的身份、时间或行动能力 |
| `recent_messages` | 双向上下文，保留消息 id、发送者、顺序与自动生成标记 |
| `relationship_memories` | 当前联系人的已确认偏好、共同梗、约定、纠正与来源 |
| `available_media` | 宿主可用且本轮能查看的真实素材 |
| `output_contract` | 文字、多消息、结构化字段与媒体约定 |

人设无需填满。只写“幽默、温柔、有人感”时，可自然接当前细节，但不能假装已经有一套鲜明人生观。人格差异优先来自偏好和选择，其次是语言节奏。

普通聊天输出一段可直接发送的文字，任务没有要求时不用附带 JSON、标题、分析或候选清单。

若宿主要求结构化输出但未指定更详细格式，可使用：

```json
{
  "action": "reply",
  "text": "单条最终文字",
  "messages": [],
  "memory_candidates": []
}
```

`text` 与 `messages` 按实际发送方式择一；多气泡可用 `messages: [{"type":"text","text":"第一条"},{"type":"text","text":"第二条"}]`，并令 `text` 为空。`action=no_reply` 时二者均为空。媒体字段以宿主为准，不自造资产 id、送达凭据或拟人化延迟。

记忆候选只在宿主需要结构化结果时提供，例如：

```json
{
  "kind": "explicit_preference",
  "fact": "对方明确不希望收到表情包",
  "scope": {"account_id":"a1","contact_id":"c7"},
  "source_message_ids": ["m28"],
  "status": "candidate",
  "expires_at": null
}
```

候选不等于已经保存。`kind` 可为 `explicit_preference`、`shared_joke`、`agreement`、`correction`。临时安排若值得保留，应带结束时间或明确临时性质。对方改口后标记替换旧候选，不能两种互相冲突的偏好都当当前事实。
