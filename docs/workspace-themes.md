# 工作台明暗主题

普通页面、加载状态、错误提示、表单、下拉框、表格、模型流程、对话与弹窗应跟随当前主题。保留页面 DOM 时，通过颜色变量切换；不依赖页面重新挂载才能更新颜色。

- 原生工作台使用 `data-workspace-theme` 与 `--ui-*` 色板。通用色板和独立主题按钮源码在 `agent-tools/frontend/`；运行时资源保存在各应用静态目录内，部署相互独立。
- `workspace.css` 继续维护原有布局与公共主题，颜色变量覆盖遗留组件。原生页面不用固定白色或黑色表示普通背景和文字。
- 小红书将组件内的固定颜色接入色板，菜单与 Ant Design tokens 同时切换。图片预览的黑色遮罩、品牌图标、真实二维码属于内容，保持其图像语义。
- 应用中心的目录与按需挂载的 AI 对话同步主题。刷新、同源多标签页和缓存恢复后，主题偏好与按钮图标保持一致。
- 经营目标、Channel、抖音发送、票务、账号中心使用独立主题控制器；不改变业务按钮与页面布局。
- 修改颜色时同时检查两种模式。新增组件应使用语义颜色，不以降低正文对比度表达次要信息；禁用状态单独表达。

离线浏览器验证：`account-maintenance/.venv/bin/python agent-tools/tests/browser/workspace_themes.py`。通过 `XHS_BUILD` 指向小红书隔离构建。测试使用合成 API、临时 DemoPlatform 数据，检查实际主题按钮、同源新页面偏好、手机溢出、缓存编辑保留、正文对比度并生成截图。

闲鱼单独验证：`account-maintenance/.venv/bin/python xianyu/web/tests/browser/themes.py`，覆盖十个主页面、两种模式、模型流程与提示栏、弹窗和草稿恢复。截图与报告保存在被忽略的 `.local/workspace-themes/`，不作为真实账号操作或真实平台数据验收。

Multica 已使用 `next-themes`、语义色板与暗色变体，本次保留其现有机制。
