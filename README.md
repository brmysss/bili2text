# bili2text

`bili2text` is being rebuilt as a CLI-first toolkit for Bilibili transcription.

The new direction is:
- core pipeline in `src/b2t`
- `yt-dlp` as the only downloader path
- Whisper as the first transcription backend
- Web UI and server mode as thin features on top of the same core
- frontend kept intentionally plain so design can be layered later

## Status

This branch starts the refactor foundation.

Current focus:
- move packaging to `pyproject.toml`
- standardize development on `uv`
- ship a real CLI entrypoint
- keep the web layer minimal and mostly structure-only

## Python

The new baseline targets Python `>=3.10,<3.13`.

## Quick Start

```bash
uv sync --extra whisper --extra web
uv run bili2text --help
```

