# Progress Tasks and Library Management Design

## Goal

Turn `bili2text` into a task-driven local application with:

- background transcription jobs
- unified progress reporting for CLI, Web, and API
- a SQLite index stored in `.b2t`
- local files as the true source of transcript content
- project-style management features such as video listing, transcript editing, categories, and tags

## Product Direction

The project is still in an early refactor phase, so this design favors clear architecture over backwards-compatibility preservation.

The application should support two usage styles at the same time:

1. direct CLI execution for individual transcription tasks
2. local app / backend usage through Web and API for project management

## Non-Negotiable Data Rules

### Local Files Are the True Source

Transcript content and media artifacts must always exist as local files under `.b2t`.

SQLite is an index and management layer only. It must not become the only place where transcript text lives.

That means:

- original transcript output must be written to disk first
- edited transcript versions must also be written to disk
- SQLite may store paths, summaries, status, and searchable metadata
- SQLite may cache derived fields for listing and filtering
- any text edit must update the target local file and then synchronize SQLite state

### SQLite Is the Operational Index

SQLite should live at `.b2t/app.db` and store:

- video records
- transcript version records
- current active transcript version pointer
- categories
- tags
- video-to-tag mappings
- transcription tasks
- latest progress snapshot per task

If SQLite is deleted or corrupted, the application should be able to rebuild the index by scanning the local workspace files.

## Workspace Layout

The workspace should evolve to:

```text
.b2t/
  app.db
  config.json
  downloads/
  audio/
  transcripts/
    original/
    edited/
  metadata/
  tasks/
```

Rules:

- `transcripts/original/` stores first-pass transcription results
- `transcripts/edited/` stores user-edited versions
- `metadata/` stores file-based metadata JSON
- `tasks/` can store optional task logs or debug snapshots
- `app.db` stores only index / state

## Core Architecture

Split the app into six layers:

### 1. Progress Domain

Create a shared progress model that can describe:

- task id
- stage key
- stage label
- message key
- percent or stage-local percent
- indeterminate vs determinate progress
- timestamps
- status (`queued`, `running`, `completed`, `failed`, `cancelled`)

This domain must be transport-agnostic. CLI, Web, and API should all consume it.

### 2. Task Orchestration

Add a task service that:

- creates background transcription jobs with task ids
- stores task state in SQLite
- updates progress snapshots as work advances
- records result paths and error messages
- lets callers poll task status by id

For this phase, task execution can remain in-process, but task state must be persisted in SQLite so history survives restarts.

### 3. File Repository Layer

Add helpers responsible for:

- deciding where original transcripts are written
- deciding where edited transcripts are written
- loading active transcript content from disk
- writing edited versions to disk
- syncing metadata JSON files

These helpers enforce the “file first, index second” rule.

### 4. SQLite Repository Layer

Add focused repositories for:

- videos
- transcript versions
- categories
- tags
- tasks

This layer should use the standard library `sqlite3` module.

### 5. Transcription Pipeline

Extend the pipeline so it can:

- emit progress events
- run under a task id
- write artifacts to file storage
- register outputs in SQLite

The pipeline remains the shared execution path for CLI, Web, and API.

### 6. Interface Layer

- CLI starts a task and can either stream updates inline or block while rendering progress
- Web submits a job, receives a task id, and polls for status
- API exposes task creation, task polling, video listing, transcript detail, editing, category assignment, and tag assignment

## Progress Model

Use stage-based progress with optional fine-grained updates inside a stage.

Recommended stages:

1. `queued`
2. `preparing`
3. `downloading`
4. `extracting_audio`
5. `transcribing`
6. `writing_outputs`
7. `indexing`
8. `completed`

Each stage should have:

- stable machine key
- i18n label key
- optional human message key
- stage order
- stage weight for overall percent calculation

### Progress Detail by Provider / Tool

#### yt-dlp

Use `progress_hooks` to capture real download progress.

#### ffmpeg

Run with machine-readable progress output so the pipeline can estimate extraction progress from processed time.

#### Whisper

Whisper already uses internal `tqdm` loops during transcription. Intercept or wrap those loops so we can convert frame progress into shared task progress events.

If exact progress is not available for some path, the system must still emit stage-level status with an indeterminate flag instead of pretending nothing is happening.

#### SenseVoice / Volcengine

If no native incremental callback exists, emit at least:

- stage entered
- model loading
- request / inference running
- stage completed

When exact percent is unavailable, use indeterminate progress with informative messages.

## SQLite Data Model

### `videos`

Represents one managed video / source item.

Suggested fields:

- `id`
- `source_kind`
- `source_input`
- `source_url`
- `source_bv`
- `title`
- `display_name`
- `language`
- `engine`
- `model`
- `video_path`
- `audio_path`
- `metadata_path`
- `current_transcript_version_id`
- `category_id`
- `created_at`
- `updated_at`

### `transcript_versions`

Represents one text file on disk.

Suggested fields:

- `id`
- `video_id`
- `kind` (`original`, `edited`)
- `file_path`
- `text_sha256`
- `char_count`
- `is_active`
- `created_at`
- `updated_at`

### `categories`

- `id`
- `name`
- `slug`
- `created_at`

Each video belongs to zero or one category.

### `tags`

- `id`
- `name`
- `slug`
- `created_at`

### `video_tags`

- `video_id`
- `tag_id`

Each video may have many tags.

### `tasks`

- `id`
- `kind`
- `status`
- `source_input`
- `provider`
- `model`
- `workspace_root`
- `video_id`
- `progress_percent`
- `current_stage`
- `current_message`
- `error_message`
- `created_at`
- `started_at`
- `finished_at`

### `task_progress_events`

Optional but recommended for debug/history.

- `id`
- `task_id`
- `status`
- `stage`
- `message`
- `percent`
- `indeterminate`
- `created_at`

### Active Transcript Rule

The active transcript is represented in two places:

- file path on disk
- `videos.current_transcript_version_id`

The DB points to the active version, but the actual text lives in the file.

## Editing Model

Use “dual version + active pointer”.

When a user edits a transcript:

1. load the currently active text from disk
2. write a new edited file under `transcripts/edited/`
3. create a new `transcript_versions` row
4. repoint `videos.current_transcript_version_id`
5. keep the original transcript file untouched

This gives us:

- auditability
- safe rollback
- project-style iteration on transcript content

## Initial Indexing

On first startup with the new system:

- create `.b2t/app.db` if missing
- scan existing workspace files
- index historical transcript / metadata / media outputs
- create `videos` and `transcript_versions` rows for anything already present

This scan can also be reused as a manual repair / resync command later.

## API Surface

### Task APIs

- `POST /api/tasks/transcribe`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/progress`

### Video APIs

- `GET /api/videos`
- `GET /api/videos/{video_id}`
- `GET /api/videos/{video_id}/transcript`

### Transcript Editing APIs

- `PUT /api/videos/{video_id}/transcript`
- `GET /api/videos/{video_id}/versions`
- `POST /api/videos/{video_id}/versions/{version_id}/activate`

### Category APIs

- `GET /api/categories`
- `POST /api/categories`
- `POST /api/videos/{video_id}/category`

### Tag APIs

- `GET /api/tags`
- `POST /api/tags`
- `POST /api/videos/{video_id}/tags`
- `DELETE /api/videos/{video_id}/tags/{tag_id}`

## CLI Behavior

CLI should remain blocking for `bili2text transcribe`, but internally it should create a task and render task progress using the same shared progress stream.

CLI output should combine:

- current stage text
- tqdm bar when percent is determinate
- spinner / text when the stage is indeterminate

All user-facing labels should go through i18n.

## Web Behavior

The Web UI should move from “submit form and wait synchronously” to:

1. submit transcription request
2. receive task id
3. poll task progress
4. redirect or render result when complete

The initial UI can stay plain, but it must use the new API shape.

## Testing Strategy

1. Unit-test the progress model and percent aggregation.
2. Unit-test SQLite repositories against temporary workspaces.
3. Unit-test task orchestration and persisted progress snapshots.
4. Unit-test pipeline progress emission with fake downloader / transcriber implementations.
5. Unit-test Web/API task flow with FastAPI test client.
6. Unit-test transcript editing to guarantee disk writes happen before DB pointer changes.
7. Keep existing pipeline and CLI behavior covered where still applicable.

## Risks

### Scope Size

This is a large step. Implementation should land in batches:

1. progress core + SQLite core + task orchestration
2. pipeline integration + CLI progress
3. Web/API task flow
4. video library management APIs

### Provider Progress Limitations

Not every provider exposes exact progress. The shared progress model must support indeterminate stages cleanly instead of forcing fake percentages everywhere.

### Data Drift

The design depends on always writing files first and syncing SQLite second. Repository helpers must centralize that rule so individual endpoints do not accidentally violate it.
