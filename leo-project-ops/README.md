# Leo Project 运维工具

## 任务元数据缓存清理

`scripts/runtime_cache_cleanup.py` 默认只统计；加 `--execute` 才删除 24 小时前的任务插件目录、工具描述缓存 JSON。仅处理受管理任务的固定缓存目录，不处理账号、配置、会话、数据库或记忆。定时服务示例在 `deploy/runtime-cache-cleanup.*`，每 6 小时检查一次。
