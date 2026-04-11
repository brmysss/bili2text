# Progress Tasks and Library Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a task-driven local backend for `bili2text` with unified progress reporting, SQLite-backed indexing, background transcription jobs, and management APIs for videos, transcript versions, categories, and tags.

**Architecture:** Keep local files as the true source of transcript content while adding `.b2t/app.db` as an operational index. Route CLI, Web, and API through a shared task and progress layer so every execution path uses the same pipeline and persisted task state.

**Tech Stack:** Python, FastAPI, Typer, sqlite3, tqdm, yt-dlp, ffmpeg, pytest

---

## File Structure

- Create: `src/b2t/progress.py`
- Create: `src/b2t/database.py`
- Create: `src/b2t/library.py`
- Create: `src/b2t/tasks.py`
- Create: `src/b2t/task_runner.py`
- Create: `tests/test_progress.py`
- Create: `tests/test_database.py`
- Create: `tests/test_tasks.py`
- Create: `tests/test_library_api.py`
- Modify: `src/b2t/config.py`
- Modify: `src/b2t/models.py`
- Modify: `src/b2t/pipeline.py`
- Modify: `src/b2t/downloaders/base.py`
- Modify: `src/b2t/downloaders/ytdlp.py`
- Modify: `src/b2t/transcribers/base.py`
- Modify: `src/b2t/transcribers/whisper_local.py`
- Modify: `src/b2t/transcribers/sensevoice_local.py`
- Modify: `src/b2t/transcribers/volcengine.py`
- Modify: `src/b2t/factory.py`
- Modify: `src/b2t/cli.py`
- Modify: `src/b2t/web.py`
- Modify: `src/b2t/i18n.py`
- Modify: `tests/test_pipeline.py`
- Modify: `tests/test_web.py`

## Implementation Batches

### Batch 1

- progress domain
- SQLite schema and repositories
- task service
- workspace indexing

### Batch 2

- pipeline progress integration
- downloader / ffmpeg / transcriber progress wiring
- CLI progress rendering

### Batch 3

- background task API
- polling endpoints
- video / transcript / tag / category APIs
- transcript edit and activate-version flow

## Self-Review Notes

- Spec coverage: progress, task persistence, SQLite indexing, library APIs, and true-source file rules are all represented in the batches above.
- Placeholder scan: no `TODO` / `TBD` placeholders kept in the executable plan sections.
- Type consistency: the plan uses `progress`, `task`, `video`, and `transcript version` terminology consistently with the spec.
