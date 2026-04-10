from pathlib import Path

from fastapi.testclient import TestClient

from b2t.models import SourceRef, TranscriptResult
from b2t.web import create_app


class FakePipeline:
    def __init__(self, tmp_path: Path, provider: str, model: str) -> None:
        self.tmp_path = tmp_path
        self.provider = provider
        self.model = model

    def transcribe(self, source: str, *, prompt: str | None = None, output: Path | None = None) -> TranscriptResult:
        transcript_path = self.tmp_path / "demo.txt"
        metadata_path = self.tmp_path / "demo.json"
        transcript_path.write_text("demo text\n", encoding="utf-8")
        metadata_path.write_text("{}", encoding="utf-8")
        return TranscriptResult(
            source=SourceRef(raw_input=source, kind="bilibili", display_name="demo", url=source, bv="BV1xx411c7XD"),
            engine=self.provider,
            model=self.model,
            text="demo text",
            audio_path=self.tmp_path / "demo.wav",
            transcript_path=transcript_path,
            metadata_path=metadata_path,
            video_path=self.tmp_path / "demo.mp4",
        )


def test_index_page_renders_form(tmp_path: Path) -> None:
    app = create_app(
        lambda provider, model: FakePipeline(tmp_path, provider, model),
        default_provider="sensevoice",
        default_model="base",
    )
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "BV / URL / 本地路径" in response.text
    assert '<option value="sensevoice" selected>' in response.text
    assert 'value="base"' in response.text


def test_transcribe_form_renders_result(tmp_path: Path) -> None:
    app = create_app(lambda provider, model: FakePipeline(tmp_path, provider, model))
    client = TestClient(app)

    response = client.post(
        "/transcribe",
        data={"source": "https://www.bilibili.com/video/BV1xx411c7XD", "provider": "sensevoice", "model": "tiny", "prompt": ""},
    )
    assert response.status_code == 200
    assert "转写完成" in response.text
    assert "demo text" in response.text
    assert "sensevoice" in response.text
    assert "tiny" in response.text


def test_index_page_supports_english_language(tmp_path: Path) -> None:
    app = create_app(
        lambda provider, model: FakePipeline(tmp_path, provider, model),
        default_provider="whisper",
        default_model="small",
        language="en-US",
    )
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "BV / URL / local path" in response.text
    assert "Start" in response.text
