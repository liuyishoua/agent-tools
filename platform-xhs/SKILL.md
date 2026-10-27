---
name: platform-xhs
description: 平台·小红书·适配交付。将已有内容或互动草稿适配为小红书笔记、评论、私信与图文审稿结果；处理表达、图片顺序和现有工作台JSON契约，账号人设由任务提供。
---

# 小红书表达与交付

先识别本轮是笔记、评论、私信还是审稿。账号身份来自 persona/account_nickname，创作方法来自所选 social-creation-*，不从“小红书风格”推断每个人都叫姐妹或都在种草。

## 笔记

依据画面和核心观察确定标题，标题让人知道在看什么；避免空泛“治愈一切”和无依据的结果承诺。当前工作台标题上限20字，提交前按实际平台约束复核。照片主导时正文可以很短，确有步骤、路线、取舍再展开。标签跟内容有关即可，不设固定数量。

首图承担停留理由，后图增加场景、动作、细节或信息。图文必须说同一件事。图库照片和生成的生活场景都不能自动证明主人到过、买过或亲自拍过；有真实记录才写第一人称事实，偏好、观点可按人设表达。

平台适配可以改开头、分段、标题与节奏；保存原来的具体观察、包袱和态度。不要把每条内容统一成钩子、三点、升华、提问。素材来源和生成记录留在内部；实际要求的署名及合成标识须随发布素材保留。

## 互动

评论围绕原帖与来话接一句；私信结合双向上下文，用 social-interaction-dialogue 决定交流动作。不要为平台适配抹掉账号性格，不默认陌生人暧昧。发送、账号与目标绑定交工作台。

## 审稿

实际查看全部最终图片，并对照最终文字。核对主体/地点/时间/商品、重复与叙事连续性；不能按文件名或下载成功推断看过。输出具体观察，未查看全图则留稿。修改后验收新的最终版本。

## 输出

一般任务按其指定交付物返回。旧工作台的 mode 必须使用下列结构，不能把 ContentPackage 直接交给发送端：

工作台私信/评论要求最终 JSON 时，在最终回答中直接返回其对象；ContentPackage 是内部组织方式，无需另写中间文件。任务明确“无需发表评论”时，不把同一 JSON 再写入 issue 评论，不为只读起草重复查询负责人/状态。只有任务要求评论交付或保存文件时才执行对应操作。

- post：`{"decision":"publish|hold","title":"","body":"","photos":[{"id":"已核实Pexels数字ID","page_url":"摄影页面","caption":"可见内容"}],"sources":[{"url":"","observation":""}],"trend":{"checked_at":"ISO时间","used":false,"phrase":"","source_urls":[],"fit":""},"reason":"内部依据"}`。publish 只表示候选稿；旧下载器只接Pexels。其他授权图片/生成图保留在通用 ContentPackage，不伪造数字ID，通过支持本地图片的手工发布接口交付。
- review：`{"decision":"approve|hold","viewed_photo_ids":[],"photo_checks":[{"id":"","observation":"","pass":true}],"text_pass":true,"reason":""}`。
- comment：`{"decision":"reply|no_reply|stop|handoff","text":"","reason":"","requires_human":false}`。
- dm：`{"decision":"reply|no_reply|handoff","reply_messages":[{"type":"text","text":"","delay_seconds":0}],"summary":"","intent":"","style":"","relationship_stage":"","expression_memory":"","requires_human":false}`。媒体使用本轮实际看过的 asset_id 和原生 kind；只有任务列出的类型才可发送。control_mode 沿用工作台，不在Skill增加审批。

示例任务：“把这组三张公园照片与这个观察适配成小红书笔记，保留说话人的冷幽默。”验收：标题、正文和图片形成一条内容，原来的冷幽默没有被改成通用种草腔。
