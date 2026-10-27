# 项目接口导航

2026-10-09 本机核对。状态每次通过工具重查，当前代码覆盖本文历史快照。
统一工具简称 `API=/opt/operator/leo-project/agent-tools/leo-project-ops/scripts/leo_api.py`；示例中以 `python3 "$API" ...` 运行。

## 抖音 douyin

- 目录 `/opt/operator/leo-project/douyin`，服务 `douyin-web.service`，本机 `http://127.0.0.1:20001`，网页 `https://portal.example.com:20031`。
- 当前 systemd 明确以 `--demo` 启动。`GET /api/meta` 的 `demo` 为最终依据。
- API 路由与 HTTP 方法：`python3 "$API" routes douyin`，源码 `web/app.py`；字段/状态约束读对应 `accounts.py`、`search.py`、`tasks.py`、`library.py`、`service.py`。
- 查询：`GET /api/accounts`、`/api/users`、`/api/tasks`、`/api/overview`、`/api/tags`、`/api/message-templates`、`/api/send-records`。
- 标签/话术：`POST /api/tags`（`{"name":"标签名"}`）、`POST /api/message-templates`；更新/删除使用 `PATCH|DELETE /api/tags/<id>`、`/api/message-templates/<id>`，具体字段先看 library.py。
- 搜索：`POST /api/searches`，按 sid 查询 `/api/searches/<sid>`、`/results`，`POST /selection`、`/import` 管理选中与入库。
- 任务：`POST /api/tasks` 创建；`GET|PATCH|DELETE /api/tasks/<tid>`；`POST /api/tasks/<tid>/<action>`（允许动作看 app.py/service.py）。创建不等于开始，开始可能启动批量消息。
- 会话：`GET /api/users/<uid>/conversation`、`/messages`，`POST /api/users/<uid>/conversation/send`，发送正文及账号要求看 app.py；不要混淆 uid、sec_uid 和抖音号。
- 写请求需要 `X-App-Request: 1`、JSON、匹配 Origin；统一工具已处理。真实模式需要单独完成账号认证。

## 票务 ticket

- 目录 `/opt/operator/leo-project/ticket`，服务 `ticket-web.service`，本机 `http://127.0.0.1:20002`，网页 `https://portal.example.com:20030`。
- `GET /api/state`：账号和任务；`GET /api/stations`：站点；`GET /api/accounts/<id>/session-history`：诊断分页。
- 所有写请求是 POST。统一工具自动从首页 `meta[name=workbench-token]` 获取 `X-Workbench-Token`；不将令牌显示给用户。
- `POST /api/accounts`：`{"name":"账号名"}`；`/api/accounts/<id>/login` 发起扫码、`/cancel-login` 取消，`/passengers` 查询已登录乘车人。
- `POST /api/query`：`account_id, from_station, to_station, train_date`；价格 `/api/prices`、起售 `/api/sale-plan`、车次选项 `/api/train-options`。
- `POST /api/tasks` 创建任务；`/api/tasks/<id>/edit|start|stop|delete` 操作任务。字段读 `web/service.py`、`reservations.py` 和 `booking_options.py`，不要猜席别/站点编码。
- 查询、登录与乘车人访问会联系真实 12306。创建预约可能自动安排查询及提交，不能把创建预约理解为只保存草稿。执行前确定用户的下单意图及必需字段；自动验收不用真实查询/下单。

## 闲鱼 xianyu

- 目录 `/opt/operator/leo-project/xianyu`，Python `/opt/operator/leo-project/xianyu/.venv/bin/python`。
- 当前用已保存登录会话的 Python 接口；没有已核实的 Web 服务/端口。`web/` 正在建设，先检查最新文件再判断是否可用，不能自行启动未知自动回复服务。
- 只读检查：在项目目录运行 `.venv/bin/python run_local.py check [--item-id ID]`；更多能力探测 `account_probe.py --item-id ID [--cid CID]` 会建立 WebSocket 并读取同步/历史，按用户需求限定范围。
- 复用 `run_local.load_api()` 加载既有登录，调用 `goofish_apis.py` 的 `XianyuApis` 方法。先读方法签名与数据返回，不能打印 api.session 或 Token 响应。
- 写入入口：`.venv/bin/python account_action.py <私有JSON配置路径>`，只接受 `send`、`publish`，不自动重试。读取 account_action.py 核对字段。
- 文字发送配置：`{"action":"send","toid":"数字用户ID","cid":"已知会话ID","text":"正文"}`；没有 cid 时需对方 `item_id`，新会话尚未完成真实验证。成功回执不代表已读。
- 发布配置：`action: publish`、`images_path`、`goods_desc`、`price.current_price`、`delivery`、`location`。location 必须含 `area,city,divisionId,longitude,latitude,poiId,poi,prov`，从账号地址候选及用户要求核对，不照搬固定坐标或历史测试商品。
- 上传、发布、已存在会话文字发送有历史实测；没有已实现的订单管理、退款、商品编辑/下架/删除，不能虚构这些能力。
- `goofish_live.py` 示例会自动复述消息；`goofish_apis.py` 示例会打印 Cookie 并测试发布，均不能直接作为运行入口。

## 模型 model-bridge

- 目录 `/opt/operator/leo-project/model-bridge`，容器 `leo-model-webui`，本机 Open WebUI `http://127.0.0.1:20015`，公网 `https://portal.example.com`。
- `GET /health`、登录后 `GET /api/models`；统一工具利用既有 `deploy/cloud.env` 的账号配置在内存登录，输出模型数据时脱敏。
- Open WebUI `POST /api/chat/completions` 可使用 `model, messages, stream:false`。例如模型 `leo-gpt-oss:20b`，实际模型 ID 先列表确认。此调用会占用远程 GPU。
- 模型通用公网 API 契约：`/opt/operator/leo-project/model-bridge/openapi.json`；`/v1` 是 WebUI 认证，`/inference/v1` 是 Windows 主机的独立认证，不可混用 Key。
- Windows GPU/权重不在此服务器。诊断入口 `scripts/diagnose-cloud.py` 从已配置文件安全使用凭据，执行前检查其输出是否符合当前任务范围。维护命令和 GPU 边界见 README.md。
- 新增账号或权限调整应查当前 Open WebUI API/现有 scripts/cloud-admin.py，不执行带 create/publish/configure 的示例验收作为普通状态查询。

## Multica

- 目录 `/opt/operator/leo-project/multica`，网页 `https://portal.example.com:20033`，工作区 Leo。
- 任务内使用 `multica` CLI：`issue list/get/create/status/assign`、`project`、`skill`、`agent` 等，先看相应 `--help`。也可统一工具调用 `/api/`，继承当前 `MULTICA_TOKEN` 与 `MULTICA_WORKSPACE_ID`。
- task 缺少凭据时停止请求，不回退读取 owner PAT；不将 owner PAT 或其他智能体的私有环境传入任务。
- 运行时服务 `multica-agent-runtime.service`；重启会影响正在执行的智能体，不能在自身普通业务操作中重启它。

## Bifrost 门户

- 目录 `/opt/operator/leo-project/bifrost`，服务 `bifrost-preview.service`，本机 `http://127.0.0.1:20017`，公网 `https://portal.example.com:20029`。
- 当前门户是 HTML 页面和 `links.json` 文件配置，没有统一业务 API，不能继续使用历史 gateway/service_control 工具调用业务系统。
- 链接接口：读取/修改 `links.json`；稳定 id 对应可见性授权，保留其他条目与用户改动。门户接入/整理请先读 `/opt/operator/.codex/skills/leo-portal-websites/SKILL.md`，用户明确要求后才编辑。
- 账号页面 `/admin`、`POST /admin/user/<id>`、`POST /admin/reset/<id>` 是登录后的表单接口，需合法会话及该页 CSRF；当前统一工具不自动登录门户管理账号。需要用户提供或选用既有已授权登录方式，不重置管理员密码来获得访问。
- 不直接修改 `portal.sqlite3` 绕过账号审计、权限与 CSRF。


## 新增平台工作台（2026-10-10）

| 工具名称 | 项目 | 本机端口 | 浏览器入口 |
| --- | --- | --- | --- |
| bilibili | bilibili | 20005 | https://portal.example.com:20037/ |
| weibo | weibo | 20006 | https://portal.example.com:20038/ |
| jd | jd | 20007 | https://portal.example.com:20039/ |
| kuaishou | kuaishou | 20008 | https://portal.example.com:20040/ |
| zhihu | zhihu | 20009 | https://portal.example.com:20041/ |

统一工具已支持上述名称，读取各项目 `.local/web/admin-password` 在内存登录工作台，不输出密码或会话。平台账号仍需用户在网页连接；不能把工作台登录视为平台认证。

- 定位接口：`python3 "$API" routes bilibili`；查询能力/账号：`python3 "$API" call bilibili /api/meta`。
- 搜索：`POST /api/searches`（`keyword,order,page,request_id`）；详情：`POST /api/details`（`value,request_id`）；返回任务 ID 后查询 `/api/jobs/<id>`。
- 专项工具及入参从 `/api/meta` 的 `tools` 获取；不猜接口或参数。知乎使用 `/api/tools/collect`（`value,kind,pages,children,request_id`），当前不支持内容搜索或发布。
- 数据：`/api/library`、`/api/drafts`、`/api/jobs`，按平台用户 ID 隔离；收藏和草稿仅保存本地。
- B站与微博文字发布必须由用户明确提供账号与正文；`confirm:true` 只能在实际获得授权后传入。请求 ID 去重，结果不确定必须先检查平台记录，不换 ID 重试。
- 京东订单/关注、快手直播状态及用户列表只主动读取，不启动自动回复或后台批量轮询。
- 各项目 `docs/workspace.md` 记录功能、登录、部署与验证边界。上游例程可能含写入或凭据输出，不直接运行。


## Channel 消息中枢

- 目录 `/opt/operator/leo-project/channel`；服务 `channel.service` / `channel-proxy.service`；本机 `http://127.0.0.1:20010`，公网 `https://portal.example.com:20042/`。
- 统一工具支持 `routes channel` / `call channel /api/meta`，在内存读取私有访问密码登录，来源凭据不会输出。
- 管理：`/api/sources`、`/api/routes`、`/api/messages`、`/api/threads`、`/api/overview`、`/api/audit`；修改规则会产生新版本，旧消息不会自动迁移。
- `POST /api/messages` 是真实模型业务操作：会根据规则新建或追加 Multica 任务；提交不代表模型完成，按 event_id 查询最终 result 和 task_id。
- 工作台使用服务端 SDK 和独立来源凭据调用 `/v1/messages`、`/v1/assets`、`/v1/results`。不得把 Channel PAT、来源凭据或平台 Cookie 放入任务上下文。
- 未投递/前置失败可人工重新排队；投递不确定只能核对原批次，不换 ID 重发。结果仅供查看/采用，不自动发送社交消息。
- 接入字段、归并策略和运行边界见 `channel/docs/api.md`、`design.md`、`operations.md`。
