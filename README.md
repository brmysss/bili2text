<p align="center">
  <img src="assets/light_logo2.png" alt="bili2text logo" width="360" />
</p>

<p align="center">
  <a href="README.en.md">English</a>
  ·
  <a href="CHANGELOG.md">更新日志</a>
  ·
  <a href="docs/DEVELOPMENT.md">开发文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/lanbinleo/bili2text" alt="GitHub stars" />
  <img src="https://img.shields.io/github/license/lanbinleo/bili2text" alt="GitHub license" />
  <img src="https://img.shields.io/github/last-commit/lanbinleo/bili2text" alt="GitHub last commit" />
  <img src="https://img.shields.io/github/v/release/lanbinleo/bili2text" alt="GitHub release" />
</p>

# bili2text

`bili2text` 正在重构为一个以 CLI 为核心、可扩展多种转写 Provider 的 Bilibili 视频转文字工具。

当前重构方向：

- 核心逻辑统一收敛到 `src/b2t`
- 下载只保留 `yt-dlp`
- 转写 Provider 通过统一 Pipeline 接入
- `Window`、`Web UI`、`Server Mode` 都作为 Feature 挂载在同一核心之上
- Web 前端保持朴素 HTML 结构，方便后续由设计师继续接管
- 开发环境统一迁移到 `uv`

> 当前 `main` 分支仍然会被频繁下载，因此重构优先在独立分支推进，达到足够稳定和体面之后再合并。

![Refactor Preview](assets/new_v_sc.png)

## 项目定位

`bili2text` 不再只是一个“脚本集合”，而是一个面向普通用户也能使用的应用型工具：

- `CLI` 是核心入口
- `window` 是保留的桌面 Feature
- `web` 提供最小可用的浏览器界面
- `server` 用于 Docker / 局域网部署
- `bootstrap` 负责首次引导、Provider 选择与本地配置初始化

## 功能概览

- 支持直接输入 Bilibili 链接、BV 号或本地媒体文件
- 使用 `yt-dlp` 下载视频，避免维护多套备用下载逻辑
- 支持多个语音转文字 Provider
- 默认支持中文优先的使用说明和交互文案
- 提供 CLI 别名、语言切换、健康检查和首次启动引导
- 保留旧版截图与历史素材，方便对照演进

## Provider 支持

目前的 Provider 规划与现状如下：

| Provider | 类型 | 适合场景 |
| --- | --- | --- |
| `whisper` | 本地模型 | 本地离线转写，通用稳定 |
| `sensevoice` | 本地模型 | 中文场景、本地模型部署 |
| `volcengine` | 云端 API | 服务化、云端识别、部署型场景 |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/lanbinleo/bili2text.git
cd bili2text
```

### 2. 使用 `uv` 安装依赖

只安装核心：

```bash
uv sync
```

安装 Whisper、本地 Web UI：

```bash
uv sync --extra whisper --extra web
```

如果你要使用 SenseVoice 或火山引擎，也可以按需增加：

```bash
uv sync --extra sensevoice --extra volcengine
```

### 3. 查看命令帮助

```bash
uv run bili2text --help
```

## Bootstrap 初始化

首次运行如果没有本地配置，`bili2text` 会自动启动 Bootstrap 向导，也可以手动运行：

```bash
uv run bili2text bootstrap
uv run bili2text init
```

Bootstrap 目前会完成这些事情：

- 选择界面语言
- 介绍 `whisper`、`sensevoice`、`volcengine` 三种配置类型
- 写入默认 Provider 与默认模型
- 配置 SenseVoice 本地模型目录
- 配置火山引擎所需的凭据与参数

本地配置默认写入：

```text
./.b2t/config.json
```

## 使用文档

### 核心命令

| 命令 | 缩写 | 中文说明 |
| --- | --- | --- |
| `bili2text transcribe` | `bili2text tx` | 下载或读取媒体并执行转写 |
| `bili2text bootstrap` | `bili2text init` | 打开初始化向导 |
| `bili2text web` | `bili2text ui` | 启动朴素 Web UI |
| `bili2text server` | `bili2text srv` | 启动服务模式 |
| `bili2text window` | `bili2text win` | 启动 Tk 窗口模式 |
| `bili2text doctor` | `bili2text diag` | 检查依赖与运行环境 |
| `bili2text language <code>` | `bili2text lang <code>` | 切换语言 |

### 常见用法

转写一个 Bilibili 视频：

```bash
uv run bili2text tx "https://www.bilibili.com/video/BV1kfDTBXEfu"
```

指定 SenseVoice 本地模型：

```bash
uv run bili2text tx "https://www.bilibili.com/video/BV1kfDTBXEfu" --provider sensevoice --model "C:/path/to/sensevoice-small"
```

切换界面语言：

```bash
uv run bili2text lang zh-CN
uv run bili2text lang en-US
```

启动 Web UI：

```bash
uv run bili2text ui
```

启动服务模式：

```bash
uv run bili2text srv --host 0.0.0.0 --port 8000
```

启动窗口模式：

```bash
uv run bili2text win
```

### 工作目录结构

默认工作目录为 `./.b2t`，其中包含：

- `downloads/` 下载的视频文件
- `audio/` 抽取后的音频
- `transcripts/` 转写文本
- `metadata/` 转写元数据
- `config.json` 本地配置文件

## 开发文档

如果你准备继续维护这个项目，推荐先看这些文档：

- [开发总览](docs/DEVELOPMENT.md)
- [更新日志](CHANGELOG.md)
- [历史归档说明](archive/README.md)

开发文档会重点说明：

- 新架构在 `src/b2t` 中如何分层
- 如何使用 `uv` 准备环境
- Provider、Feature、入口脚本分别放在哪里
- 如何继续拆分功能并保持小步提交

## 目录说明

| 路径 | 作用 |
| --- | --- |
| `src/b2t` | 新核心代码 |
| `tests` | 自动化测试 |
| `assets` | logo、截图、favicon 等项目素材 |
| `archive` | 保留的旧版脚本与历史依赖文件 |
| `main.py` | 兼容入口 |
| `window.py` | 兼容窗口入口 |

## 更新日志

重构阶段的更新日志已经独立整理，请查看：

- [中文更新日志](CHANGELOG.md)
- [English Changelog](CHANGELOG.en.md)

## 运行截图

旧版截图和素材会继续保留：

<img src="assets/screenshot3.png" alt="screenshot3" width="600" />
<img src="assets/screenshot2.png" alt="screenshot2" width="600" />
<img src="assets/screenshot1.png" alt="screenshot1" width="600" />

## 许可证

本项目使用 MIT License。

## 贡献

欢迎继续提交 Issue / PR，一起把这次重构做成真正可长期维护的版本。

## 使用须知

使用 `bili2text` 时，请遵守你所在地区的版权法律与平台规则，并确保你有权下载、处理和转换相关内容。
