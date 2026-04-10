# bili2text

`bili2text` is being rebuilt as a CLI-first toolkit for Bilibili transcription.

The new direction is:
- core pipeline in `src/b2t`
- `yt-dlp` as the only downloader path
- multiple transcription providers behind the same pipeline
- Web UI, server mode, and Tk window as thin features on top of the same core
- frontend kept intentionally plain so design can be layered later

## Status

This branch starts the refactor foundation.

Current focus:
- move packaging to `pyproject.toml`
- standardize development on `uv`
- ship a real CLI entrypoint and bootstrap flow
- keep the web layer minimal and mostly structure-only
- preserve a Tk desktop entrypoint as the `window` feature

## Python

The new baseline targets Python `>=3.10,<3.13`.

## Quick Start

```bash
uv sync --extra whisper --extra web
uv run bili2text --help
```

## Bootstrap

The first interactive run can create a local config in `./.b2t/config.json`.

You can also run it directly:

```bash
uv run bili2text bootstrap
```

## Providers

Current provider plan:
- `whisper`: local Whisper models
- `sensevoice`: local SenseVoice Small style model directories
- `volcengine`: Volcengine ASR API

## Commands

```bash
uv run bili2text bootstrap
uv run bili2text transcribe "https://www.bilibili.com/video/BV1xx411c7XD"
uv run bili2text transcribe "https://www.bilibili.com/video/BV1xx411c7XD" --provider sensevoice --model "C:/path/to/sensevoice-small"
uv run bili2text web
uv run bili2text server --host 0.0.0.0 --port 8000
uv run bili2text window
uv run bili2text doctor
```

## Notes

- `ffmpeg` is required for audio extraction.
- `window.py` now routes into the new Tk window feature instead of the legacy flow.
- `main.py` remains as a compatibility entrypoint.

