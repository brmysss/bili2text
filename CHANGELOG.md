# 更新日志

## 2026-04-10

### 重构基础

- 建立 `src/b2t` 为核心目录，逐步替代旧脚本式结构
- 引入 CLI-first 架构，统一 `transcribe / web / server / window` 入口
- 下载流程统一收敛到 `yt-dlp`
- 新增 Bootstrap 初始化流程与本地配置文件机制

### Provider

- 接入本地 `whisper`
- 接入本地 `sensevoice`
- 增加火山引擎 Provider 骨架与配置项

### 交互与体验

- CLI 帮助信息改为中文优先
- 增加短命令别名：`tx / init / ui / srv / win / diag / lang`
- 增加 `language` / `lang` 命令
- Bootstrap 升级为交互式向导，并补充三类 Provider 说明
- Web UI 与 Tk Window 接入 i18n 文案

### 文档与仓库整理

- README 重新整理为中英双语门面
- 增加开发文档
- 将旧脚本与历史依赖迁移到 `archive/`
- 将 logo / favicon 等素材归档到 `assets/`
