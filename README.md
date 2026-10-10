# agent-tools

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-orange)](LICENSE)

本地业务 agent 的 skill 和工具集合，为项目接口操作、自然表达、内容研究和视觉素材检索提供说明与脚本。
各 skill 只在相应任务和已授权范围内使用，不携带平台 Cookie、账号密码或机器访问令牌。

## 使用

```bash
git clone https://github.com/liuyishoua/agent-tools.git
cd agent-tools
python3 leo-project-ops/scripts/leo_api.py --help
```

将需要的 skill 按你使用的 agent 客户端方式安装。`leo-project-ops` 需要本机实际运行的项目与已授权连接；
首次使用前调整脚本中的项目根目录和文档中的本机地址。
工具中的真实写入参数只在用户明确授权相应业务操作后使用。

## 数据与验证

运行凭据保存在各业务项目的忽略目录，工具按需在内存中读取并脱敏输出。
`workspace-previews/` 为本机工作产物，不纳入发布。

```bash
python3 -m py_compile leo-project-ops/scripts/leo_api.py
```

## 目录

- `leo-project-ops/`：项目接口导航和统一 CLI。
- `xhs-natural-expression/`：自然表达与素材引用约定。
- `xhs-lifestyle-publisher/`：内容研究与发布流程说明。
- `gifgrep/`：GIF 搜索工具使用说明，不分发第三方二进制。

## 使用许可

**本项目仅供学习、研究、测试及其他非商业用途，不得用于商业目的。**
对本仓库中版权所有者拥有权利的代码，采用
[PolyForm Noncommercial License 1.0.0](LICENSE)；商业使用须事先取得版权所有者的单独授权。
本项目属于**源码可见、限制商用**，不应标为 MIT 或 OSI 意义上的开源许可证。

第三方代码、素材和依赖仍受其各自许可条件约束，来源与许可范围见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本声明不追溯改变第三方代码或此前已发布版本的许可。
