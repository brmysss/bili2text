from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from b2t.config import Settings
from b2t.models import ProgressSnapshot, TaskRecord, TranscriptVersionRecord, VideoRecord


def utc_now() -> str:
    return datetime.now().isoformat()


class AppDatabase:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_directories()
        self.path = settings.app_db_path
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_input TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    workspace_root TEXT NOT NULL,
                    progress_percent REAL NOT NULL DEFAULT 0,
                    current_stage TEXT NOT NULL DEFAULT 'queued',
                    current_message TEXT NOT NULL DEFAULT '',
                    error_message TEXT NOT NULL DEFAULT '',
                    video_id INTEGER,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );

                CREATE TABLE IF NOT EXISTS task_progress_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    message TEXT NOT NULL DEFAULT '',
                    percent REAL NOT NULL DEFAULT 0,
                    indeterminate INTEGER NOT NULL DEFAULT 0,
                    detail_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_kind TEXT NOT NULL,
                    source_input TEXT NOT NULL,
                    source_url TEXT,
                    source_bv TEXT,
                    title TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    language TEXT,
                    engine TEXT NOT NULL,
                    model TEXT NOT NULL,
                    video_path TEXT,
                    audio_path TEXT NOT NULL,
                    metadata_path TEXT NOT NULL UNIQUE,
                    current_transcript_version_id INTEGER,
                    category_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS transcript_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    text_sha256 TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS video_tags (
                    video_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (video_id, tag_id)
                );
                """
            )

    def create_task(self, *, kind: str, source_input: str, provider: str, model: str) -> TaskRecord:
        now = utc_now()
        task = TaskRecord(
            id=uuid.uuid4().hex,
            kind=kind,
            status="queued",
            source_input=source_input,
            provider=provider,
            model=model,
            workspace_root=str(self.settings.workspace_root),
            created_at=now,
        )
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, kind, status, source_input, provider, model, workspace_root,
                    progress_percent, current_stage, current_message, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.kind,
                    task.status,
                    task.source_input,
                    task.provider,
                    task.model,
                    task.workspace_root,
                    task.progress_percent,
                    task.current_stage,
                    task.current_message,
                    task.error_message,
                    task.created_at,
                ),
            )
        return task

    def record_progress(self, snapshot: ProgressSnapshot) -> None:
        with self._connect() as conn:
            if snapshot.status == "running":
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, progress_percent = ?, current_stage = ?, current_message = ?,
                        started_at = COALESCE(started_at, ?)
                    WHERE id = ?
                    """,
                    (
                        snapshot.status,
                        snapshot.percent,
                        snapshot.stage,
                        snapshot.message,
                        snapshot.updated_at,
                        snapshot.task_id,
                    ),
                )
            else:
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, progress_percent = ?, current_stage = ?, current_message = ?
                    WHERE id = ?
                    """,
                    (
                        snapshot.status,
                        snapshot.percent,
                        snapshot.stage,
                        snapshot.message,
                        snapshot.task_id,
                    ),
                )
            conn.execute(
                """
                INSERT INTO task_progress_events (
                    task_id, status, stage, message, percent, indeterminate, detail_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.task_id,
                    snapshot.status,
                    snapshot.stage,
                    snapshot.message,
                    snapshot.percent,
                    1 if snapshot.indeterminate else 0,
                    json.dumps(snapshot.detail, ensure_ascii=False),
                    snapshot.updated_at,
                ),
            )

    def complete_task(self, task_id: str, *, video_id: int | None = None, message: str = "") -> None:
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = 'completed', progress_percent = 1.0, current_stage = 'completed',
                    current_message = ?, video_id = ?, finished_at = ?
                WHERE id = ?
                """,
                (message, video_id, now, task_id),
            )

    def fail_task(self, task_id: str, *, error_message: str) -> None:
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = 'failed', current_stage = 'failed', error_message = ?, finished_at = ?
                WHERE id = ?
                """,
                (error_message, now, task_id),
            )

    def get_task(self, task_id: str) -> TaskRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return None if row is None else self._task_from_row(row)

    def list_tasks(self) -> list[TaskRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        return [self._task_from_row(row) for row in rows]

    def create_video(
        self,
        *,
        source_kind: str,
        source_input: str,
        source_url: str | None,
        source_bv: str | None,
        title: str,
        display_name: str,
        language: str | None,
        engine: str,
        model: str,
        video_path: str | None,
        audio_path: str,
        metadata_path: str,
    ) -> int:
        now = utc_now()
        with self._connect() as conn:
            row = conn.execute("SELECT id FROM videos WHERE metadata_path = ?", (metadata_path,)).fetchone()
            if row is not None:
                return int(row["id"])
            cursor = conn.execute(
                """
                INSERT INTO videos (
                    source_kind, source_input, source_url, source_bv, title, display_name,
                    language, engine, model, video_path, audio_path, metadata_path,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_kind,
                    source_input,
                    source_url,
                    source_bv,
                    title,
                    display_name,
                    language,
                    engine,
                    model,
                    video_path,
                    audio_path,
                    metadata_path,
                    now,
                    now,
                ),
            )
            return int(cursor.lastrowid)

    def create_transcript_version(
        self,
        *,
        video_id: int,
        kind: str,
        file_path: str,
        text_sha256: str,
        char_count: int,
        is_active: bool,
    ) -> int:
        now = utc_now()
        with self._connect() as conn:
            if is_active:
                conn.execute("UPDATE transcript_versions SET is_active = 0 WHERE video_id = ?", (video_id,))
            cursor = conn.execute(
                """
                INSERT INTO transcript_versions (
                    video_id, kind, file_path, text_sha256, char_count, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (video_id, kind, file_path, text_sha256, char_count, 1 if is_active else 0, now, now),
            )
            version_id = int(cursor.lastrowid)
            if is_active:
                conn.execute(
                    "UPDATE videos SET current_transcript_version_id = ?, updated_at = ? WHERE id = ?",
                    (version_id, now, video_id),
                )
            return version_id

    def activate_transcript_version(self, video_id: int, version_id: int) -> None:
        now = utc_now()
        with self._connect() as conn:
            conn.execute("UPDATE transcript_versions SET is_active = 0 WHERE video_id = ?", (video_id,))
            conn.execute("UPDATE transcript_versions SET is_active = 1, updated_at = ? WHERE id = ?", (now, version_id))
            conn.execute(
                "UPDATE videos SET current_transcript_version_id = ?, updated_at = ? WHERE id = ?",
                (version_id, now, video_id),
            )

    def list_videos(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT v.*, c.name AS category_name
                FROM videos v
                LEFT JOIN categories c ON c.id = v.category_id
                ORDER BY v.created_at DESC
                """
            ).fetchall()
            tags = self._load_tags_by_video(conn)
        return [self._video_payload(row, tags.get(int(row["id"]), [])) for row in rows]

    def get_video(self, video_id: int) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT v.*, c.name AS category_name
                FROM videos v
                LEFT JOIN categories c ON c.id = v.category_id
                WHERE v.id = ?
                """,
                (video_id,),
            ).fetchone()
            if row is None:
                return None
            tags = self._load_tags_by_video(conn)
        return self._video_payload(row, tags.get(video_id, []))

    def list_transcript_versions(self, video_id: int) -> list[TranscriptVersionRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM transcript_versions WHERE video_id = ? ORDER BY created_at DESC",
                (video_id,),
            ).fetchall()
        return [self._version_from_row(row) for row in rows]

    def get_active_transcript_version(self, video_id: int) -> TranscriptVersionRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM transcript_versions WHERE video_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1",
                (video_id,),
            ).fetchone()
        return None if row is None else self._version_from_row(row)

    def create_category(self, name: str) -> dict[str, object]:
        slug = slugify(name)
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name, slug, created_at) VALUES (?, ?, ?)",
                (name, slug, now),
            )
            row = conn.execute("SELECT * FROM categories WHERE slug = ?", (slug,)).fetchone()
        assert row is not None
        return dict(row)

    def list_categories(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
        return [dict(row) for row in rows]

    def assign_category(self, video_id: int, category_id: int | None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE videos SET category_id = ?, updated_at = ? WHERE id = ?",
                (category_id, utc_now(), video_id),
            )

    def create_tag(self, name: str) -> dict[str, object]:
        slug = slugify(name)
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tags (name, slug, created_at) VALUES (?, ?, ?)",
                (name, slug, now),
            )
            row = conn.execute("SELECT * FROM tags WHERE slug = ?", (slug,)).fetchone()
        assert row is not None
        return dict(row)

    def list_tags(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        return [dict(row) for row in rows]

    def add_video_tag(self, video_id: int, tag_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO video_tags (video_id, tag_id) VALUES (?, ?)",
                (video_id, tag_id),
            )

    def remove_video_tag(self, video_id: int, tag_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM video_tags WHERE video_id = ? AND tag_id = ?", (video_id, tag_id))

    def _load_tags_by_video(self, conn: sqlite3.Connection) -> dict[int, list[dict[str, object]]]:
        rows = conn.execute(
            """
            SELECT vt.video_id, t.id, t.name, t.slug
            FROM video_tags vt
            JOIN tags t ON t.id = vt.tag_id
            ORDER BY t.name ASC
            """
        ).fetchall()
        tags: dict[int, list[dict[str, object]]] = {}
        for row in rows:
            tags.setdefault(int(row["video_id"]), []).append(
                {"id": int(row["id"]), "name": row["name"], "slug": row["slug"]}
            )
        return tags

    def _video_payload(self, row: sqlite3.Row, tags: list[dict[str, object]]) -> dict[str, object]:
        return {
            **dict(row),
            "tags": tags,
        }

    def _task_from_row(self, row: sqlite3.Row) -> TaskRecord:
        return TaskRecord(
            id=row["id"],
            kind=row["kind"],
            status=row["status"],
            source_input=row["source_input"],
            provider=row["provider"],
            model=row["model"],
            workspace_root=row["workspace_root"],
            progress_percent=float(row["progress_percent"]),
            current_stage=row["current_stage"],
            current_message=row["current_message"],
            error_message=row["error_message"],
            video_id=row["video_id"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
        )

    def _version_from_row(self, row: sqlite3.Row) -> TranscriptVersionRecord:
        return TranscriptVersionRecord(
            id=int(row["id"]),
            video_id=int(row["video_id"]),
            kind=row["kind"],
            file_path=row["file_path"],
            text_sha256=row["text_sha256"],
            char_count=int(row["char_count"]),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


def slugify(value: str) -> str:
    return "-".join(value.strip().lower().split())
