from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from b2t.i18n import dependency_sync_guidance
from b2t.transcribers.base import Transcriber


class LocalWhisperTranscriber(Transcriber):
    name = "whisper"

    def __init__(self, model: str = "small", device: str | None = None) -> None:
        self.model_name = model
        self.device = device
        self._model: Any | None = None

    def transcribe(
        self,
        audio_path: Path,
        *,
        prompt: str | None = None,
        progress=None,
    ) -> dict[str, Any]:
        model = self._ensure_model()
        if progress is not None:
            progress.running("transcribing", message="transcribing", indeterminate=True)
        transcribe_options: dict[str, Any] = {
            "initial_prompt": prompt or None,
            # `verbose=None` keeps the current Whisper release quiet on both text and frame progress.
            "verbose": None,
        }
        if self.device == "cpu":
            transcribe_options["fp16"] = False
        result = model.transcribe(str(audio_path), **transcribe_options)
        text = (result.get("text") or "").strip()
        return {
            "text": text,
            "segments": result.get("segments", []),
            "language": result.get("language"),
            "device": self.device,
            "model": self.model_name,
        }

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError(build_whisper_import_error_message()) from exc

        if self.device is None:
            self.device = "cuda" if whisper.torch.cuda.is_available() else "cpu"
        self._model = whisper.load_model(self.model_name, device=self.device)
        return self._model


def build_whisper_import_error_message(*, whisper_available: bool | None = None) -> str:
    if whisper_available is None:
        whisper_available = importlib.util.find_spec("whisper") is not None

    if whisper_available:
        return (
            "Whisper is installed, but the Python environment looks broken. "
            "Recreate `.venv` and sync the required extras again. "
            f"{dependency_sync_guidance('en-US')} "
            "Whisper currently needs Python 3.12 or below."
        )

    return (
        "Whisper support is not installed. "
        f"{dependency_sync_guidance('en-US')} "
        "Whisper currently needs Python 3.12 or below."
    )
