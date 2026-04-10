from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WORKSPACE_NAME = ".b2t"


@dataclass(slots=True)
class Settings:
    workspace_root: Path
    downloads_dir: Path
    audio_dir: Path
    transcripts_dir: Path
    metadata_dir: Path

    @classmethod
    def from_workspace(cls, workspace: Path | None = None) -> "Settings":
        root = workspace or Path(os.getenv("B2T_HOME", DEFAULT_WORKSPACE_NAME)).expanduser()
        return cls(
            workspace_root=root,
            downloads_dir=root / "downloads",
            audio_dir=root / "audio",
            transcripts_dir=root / "transcripts",
            metadata_dir=root / "metadata",
        )

    def ensure_directories(self) -> None:
        for directory in (
            self.workspace_root,
            self.downloads_dir,
            self.audio_dir,
            self.transcripts_dir,
            self.metadata_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
