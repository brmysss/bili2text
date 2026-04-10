from __future__ import annotations

from pathlib import Path
from typing import Any

from b2t.transcribers.base import Transcriber


class LocalWhisperTranscriber(Transcriber):
    name = "whisper"

    def __init__(self, model: str = "small", device: str | None = None) -> None:
        self.model_name = model
        self.device = device
        self._model: Any | None = None

    def transcribe(self, audio_path: Path, *, prompt: str | None = None) -> dict[str, Any]:
        model = self._ensure_model()
        result = model.transcribe(str(audio_path), initial_prompt=prompt or None, verbose=False)
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
            raise RuntimeError(
                "Whisper support is not installed. Run `uv sync --extra whisper` with Python 3.12 or below."
            ) from exc

        if self.device is None:
            self.device = "cuda" if whisper.torch.cuda.is_available() else "cpu"
        self._model = whisper.load_model(self.model_name, device=self.device)
        return self._model
