from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from b2t.transcribers.base import Transcriber


class VolcengineFlashTranscriber(Transcriber):
    name = "volcengine"

    def __init__(
        self,
        *,
        api_key: str = "",
        app_key: str = "",
        access_key: str = "",
        resource_id: str = "volc.bigasr.auc_turbo",
        model_name: str = "bigmodel",
        use_itn: bool = True,
    ) -> None:
        self.api_key = api_key.strip()
        self.app_key = app_key.strip()
        self.access_key = access_key.strip()
        self.resource_id = resource_id
        self.model_name = model_name
        self.use_itn = use_itn

    def transcribe(self, audio_path: Path, *, prompt: str | None = None) -> dict[str, Any]:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "Volcengine support is not installed. Run `uv sync --extra volcengine` first."
            ) from exc

        headers = self._build_headers()
        if not headers:
            raise RuntimeError("Volcengine provider requires API credentials. Run `bili2text bootstrap` first.")

        audio_data = base64.b64encode(audio_path.read_bytes()).decode("utf-8")
        payload = {
            "user": {"uid": "bili2text"},
            "audio": {"format": audio_path.suffix.lstrip(".").lower() or "wav", "data": audio_data},
            "request": {
                "model_name": self.model_name,
                "show_utterances": True,
                "enable_itn": self.use_itn,
                "result_type": "full",
            },
        }

        if prompt:
            payload["request"]["context"] = prompt

        response = requests.post(
            f"https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit?resource_id={self.resource_id}",
            headers=headers,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Volcengine request failed: {data.get('message') or data}")

        result = data.get("result", {})
        utterances = result.get("utterances") or []
        text = "\n".join(item.get("text", "") for item in utterances if item.get("text")).strip()
        if not text:
            text = (result.get("text") or "").strip()

        return {
            "text": text,
            "segments": utterances,
            "language": result.get("language"),
            "model": self.model_name,
            "raw_response": data,
        }

    def _build_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        if self.app_key and self.access_key:
            return {
                "X-Api-App-Key": self.app_key,
                "X-Api-Access-Key": self.access_key,
                "Content-Type": "application/json",
            }
        return {}
