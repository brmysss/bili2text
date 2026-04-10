from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Transcriber(ABC):
    name = "transcriber"

    @abstractmethod
    def transcribe(self, audio_path: Path, *, prompt: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
