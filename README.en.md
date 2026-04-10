<p align="center">
  <img src="assets/light_logo2.png" alt="bili2text logo" width="360" />
</p>

<p align="center">
  <a href="README.md">简体中文</a>
  ·
  <a href="CHANGELOG.en.md">Changelog</a>
  ·
  <a href="docs/DEVELOPMENT.en.md">Development Docs</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/lanbinleo/bili2text" alt="GitHub stars" />
  <img src="https://img.shields.io/github/license/lanbinleo/bili2text" alt="GitHub license" />
  <img src="https://img.shields.io/github/last-commit/lanbinleo/bili2text" alt="GitHub last commit" />
  <img src="https://img.shields.io/github/v/release/lanbinleo/bili2text" alt="GitHub release" />
</p>

# bili2text

`bili2text` is being rebuilt as a CLI-first toolkit for turning Bilibili videos into text.

The current refactor direction is:

- keep the core inside `src/b2t`
- use `yt-dlp` as the only downloader path
- support multiple transcription providers behind one pipeline
- expose `window`, `web`, and `server` as features on top of the same core
- keep the web layer intentionally plain so a dedicated designer can polish it later
- standardize development on `uv`

![Refactor Preview](assets/new_v_sc.png)

## Positioning

This project is moving away from being “a collection of scripts” and toward being an application that normal users can still operate:

- `CLI` is the main entrypoint
- `window` keeps the Tk desktop feature alive
- `web` provides a minimal browser UI
- `server` supports Docker and LAN deployment
- `bootstrap` handles first-run setup and local configuration

## Features

- Accept a Bilibili URL, BV id, or a local media file
- Use `yt-dlp` for downloads
- Support multiple speech-to-text providers
- Prefer Chinese-first copy while keeping command names in English
- Ship command aliases, language switching, diagnostics, and first-run onboarding
- Preserve legacy screenshots and historical assets

## Providers

| Provider | Type | Best for |
| --- | --- | --- |
| `whisper` | local model | general local/offline transcription |
| `sensevoice` | local model | Chinese-heavy local workflows |
| `volcengine` | cloud API | deployment and service-oriented workflows |

## Quick Start

### 1. Clone

```bash
git clone https://github.com/lanbinleo/bili2text.git
cd bili2text
```

### 2. Install with `uv`

Core only:

```bash
uv sync
```

With Whisper and the web feature:

```bash
uv sync --extra whisper --extra web
```

Add more providers when needed:

```bash
uv sync --extra sensevoice --extra volcengine
```

### 3. Inspect the CLI

```bash
uv run bili2text --help
```

## Bootstrap

If no local config exists yet, `bili2text` will auto-start the bootstrap wizard on first run.

You can also launch it manually:

```bash
uv run bili2text bootstrap
uv run bili2text init
```

Bootstrap now does more than write config. It also generates and runs one correct `uv sync --extra ...` command based on the Providers and Features you selected.

The bootstrap flow currently covers:

- interface language
- provider selection
- feature selection
- default provider and default model
- SenseVoice local model directory
- Volcengine credentials and related options
- a confirmed environment sync command

Important:

- do not chain multiple `uv sync --extra ...` commands and expect them to merge automatically
- either run one combined sync command or let Bootstrap handle it
- if the environment gets out of sync, run:

```bash
uv run bili2text bootstrap --sync-only
```

The local config is written to:

```text
./.b2t/config.json
```

## Usage

### Main commands

| Command | Alias | What it does |
| --- | --- | --- |
| `bili2text transcribe` | `bili2text tx` | transcribe media |
| `bili2text bootstrap` | `bili2text init` | launch setup wizard |
| `bili2text web` | `bili2text ui` | start the plain web UI |
| `bili2text server` | `bili2text srv` | start server mode |
| `bili2text window` | `bili2text win` | start Tk window mode |
| `bili2text doctor` | `bili2text diag` | inspect dependencies |
| `bili2text language <code>` | `bili2text lang <code>` | switch language |

### Common examples

```bash
uv run bili2text tx "https://www.bilibili.com/video/BV1kfDTBXEfu"
uv run bili2text tx "https://www.bilibili.com/video/BV1kfDTBXEfu" --provider sensevoice --model "C:/path/to/sensevoice-small"
uv run bili2text lang en-US
uv run bili2text ui
uv run bili2text srv --host 0.0.0.0 --port 8000
uv run bili2text win
```

## Development

Start here if you want to maintain the refactor:

- [Development Guide](docs/DEVELOPMENT.en.md)
- [Changelog](CHANGELOG.en.md)
- [Archive Notes](archive/README.md)

## Layout

| Path | Purpose |
| --- | --- |
| `src/b2t` | new core implementation |
| `tests` | automated tests |
| `assets` | logos, screenshots, favicon, project materials |
| `archive` | preserved legacy scripts and historical files |
| `main.py` | compatibility entrypoint |
| `window.py` | compatibility window entrypoint |

## Legacy Screenshots

<img src="assets/screenshot3.png" alt="screenshot3" width="600" />
<img src="assets/screenshot2.png" alt="screenshot2" width="600" />
<img src="assets/screenshot1.png" alt="screenshot1" width="600" />

## License

MIT License.

## Notice

Please respect the copyright laws and platform rules in your region before downloading or processing any content.
