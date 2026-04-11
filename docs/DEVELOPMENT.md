# 开发文档

## 当前目标

这个仓库正在从旧版脚本式实现迁移到一个更稳定的应用结构：

- `CLI` 作为核心入口
- `Window / Web / Server` 作为 Feature
- `Provider` 与核心逻辑解耦
- 依赖管理与开发流程统一到 `uv`

## 目录结构

```text
src/b2t/
  cli.py            CLI 入口
  bootstrap.py      首次启动向导
  user_config.py    本地配置读写
  pipeline.py       核心转写流程
  factory.py        Provider / Downloader 组装
  downloaders/      下载实现
  transcribers/     转写 Provider
  templates/        朴素 Web 模板
  window_app.py     Tk Feature
tests/              自动化测试
assets/             logo、截图、favicon 等素材
archive/            旧版脚本与历史文件
```

## 本地开发

### 环境准备

```bash
uv sync --extra whisper --extra web
```

如需 SenseVoice / 火山引擎：

```bash
uv sync --extra sensevoice --extra volcengine
```

更推荐直接用 Bootstrap 管理组合环境：

```bash
uv run bili2text bootstrap
uv run bili2text bootstrap --sync-only
```

### 常用命令

```bash
uv run bili2text --help
uv run bili2text doctor
uv run bili2text bootstrap
uv run bili2text tx "<bilibili-url>"
uv run bili2text ui
uv run bili2text win
pytest -q
```

## 配置机制

本地配置默认保存在：

```text
./.b2t/config.json
```

当前配置主要包含：

- `language`
- `enabled_providers`
- `enabled_features`
- `default_provider`
- `default_model`
- `sensevoice.*`
- `volcengine.*`

## Provider 约定

新增 Provider 时，尽量遵守下面的边界：

- 下载逻辑不要塞进 Provider
- Provider 只负责“把音频转成文本”
- 配置项写入 `AppConfig`
- 创建逻辑统一走 `factory.py`
- 真实工作流统一走 `pipeline.py`

## Feature 约定

`Window / Web / Server` 都应该尽量只做壳层：

- 接受输入
- 调用统一 Pipeline
- 输出结果
- 不复制核心业务逻辑

## 提交建议

当前分支偏向小步提交：

- 一个功能点一个 commit
- 一个修复点一个 commit
- 改结构和改行为尽量拆开
- 提交前先跑相关测试

## 清理策略

- 根目录尽量只保留真正的项目入口和元信息
- 历史脚本放进 `archive/`
- 项目素材放进 `assets/`
- 兼容入口暂时保留 `main.py` 和 `window.py`

## 后续建议

接下来继续推进时，优先顺序建议为：

1. 继续完善 Provider 抽象与错误处理
2. 补充更多自动化测试
3. 为 Server Mode 增加更稳定的部署说明
4. 让 Web UI 继续保持结构简单，等待设计稿接管
