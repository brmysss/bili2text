from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


SourceKind = Literal["bilibili", "audio", "video"]


@dataclass(slots=True)
class SourceRef:
    raw_input: str
    kind: SourceKind
    display_name: str
    url: str | None = None
    bv: str | None = None
    path: Path | None = None


@dataclass(slots=True)
class DownloadResult:
    source: SourceRef
    video_path: Path
    title: str | None = None
    webpage_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TranscriptResult:
    source: SourceRef
    engine: str
    model: str
    text: str
    audio_path: Path
    transcript_path: Path
    metadata_path: Path
    video_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
