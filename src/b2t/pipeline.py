from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from b2t.config import Settings
from b2t.downloaders.base import Downloader
from b2t.inputs import parse_source, safe_stem
from b2t.models import DownloadResult, TranscriptResult
from b2t.transcribers.base import Transcriber


class B2TPipeline:
    def __init__(
        self,
        *,
        settings: Settings,
        downloader: Downloader,
        transcriber: Transcriber,
    ) -> None:
        self.settings = settings
        self.downloader = downloader
        self.transcriber = transcriber

    def transcribe(
        self,
        source_input: str,
        *,
        prompt: str | None = None,
        output: Path | None = None,
    ) -> TranscriptResult:
        self.settings.ensure_directories()
        source = parse_source(source_input)
        downloaded: DownloadResult | None = None

        if source.kind == "bilibili":
            downloaded = self.downloader.download(source, self.settings)
            audio_path = self._extract_audio(downloaded.video_path, safe_stem(downloaded.title or source.display_name))
            base_name = downloaded.title or source.display_name
            video_path = downloaded.video_path
        elif source.kind == "video":
            assert source.path is not None
            audio_path = self._extract_audio(source.path, safe_stem(source.display_name))
            base_name = source.display_name
            video_path = source.path
        else:
            assert source.path is not None
            audio_path = source.path
            base_name = source.display_name
            video_path = None

        transcription = self.transcriber.transcribe(audio_path, prompt=prompt)
        text = transcription.get("text", "").strip()
        if not text:
            raise RuntimeError("transcriber returned an empty transcript")

        transcript_path = self._resolve_output_path(base_name, output)
        metadata_path = transcript_path.with_suffix(".json")
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(text + "\n", encoding="utf-8")

        metadata = {
            "source": {
                "raw_input": source.raw_input,
                "kind": source.kind,
                "bv": source.bv,
                "url": source.url,
                "path": str(source.path) if source.path else None,
            },
            "engine": self.transcriber.name,
            "model": transcription.get("model"),
            "audio_path": str(audio_path),
            "video_path": str(video_path) if video_path else None,
            "download": downloaded.metadata if downloaded else None,
            "language": transcription.get("language"),
            "generated_at": datetime.now().isoformat(),
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        return TranscriptResult(
            source=source,
            engine=self.transcriber.name,
            model=str(transcription.get("model") or ""),
            text=text,
            audio_path=audio_path,
            transcript_path=transcript_path,
            metadata_path=metadata_path,
            video_path=video_path,
            metadata=metadata,
        )

    def _extract_audio(self, video_path: Path, stem: str) -> Path:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("ffmpeg is required to extract audio but was not found on PATH")

        audio_path = self.settings.audio_dir / f"{stem}.wav"
        result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or "unknown ffmpeg error"
            raise RuntimeError(f"ffmpeg failed to extract audio: {stderr}")
        return audio_path

    def _resolve_output_path(self, base_name: str, output: Path | None) -> Path:
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            return self.settings.transcripts_dir / f"{safe_stem(base_name)}-{timestamp}.txt"

        output = output.expanduser()
        if output.suffix.lower() != ".txt":
            if output.exists() and output.is_dir():
                return output / f"{safe_stem(base_name)}.txt"
            return output.with_suffix(".txt")
        return output
