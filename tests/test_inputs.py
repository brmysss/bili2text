from pathlib import Path

from b2t.inputs import parse_source, safe_stem


def test_parse_bv_identifier() -> None:
    source = parse_source("BV1xx411c7XD")
    assert source.kind == "bilibili"
    assert source.bv == "BV1xx411c7XD"
    assert source.url == "https://www.bilibili.com/video/BV1xx411c7XD"


def test_parse_bilibili_url_keeps_page_information() -> None:
    source = parse_source("https://www.bilibili.com/video/BV1xx411c7XD?p=2")
    assert source.kind == "bilibili"
    assert source.url == "https://www.bilibili.com/video/BV1xx411c7XD?p=2"


def test_parse_local_audio_file(tmp_path: Path) -> None:
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"wav")

    source = parse_source(str(audio_path))
    assert source.kind == "audio"
    assert source.path == audio_path.resolve()


def test_safe_stem_removes_unsafe_characters() -> None:
    assert safe_stem("hello / world?") == "hello-world"
