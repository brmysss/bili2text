from b2t.transcribers.whisper_local import build_whisper_import_error_message


def test_build_whisper_import_error_message_reports_missing_install() -> None:
    message = build_whisper_import_error_message(
        whisper_available=False,
    )

    assert "Whisper support is not installed." in message
    assert "uv sync --extra whisper --extra web" in message


def test_build_whisper_import_error_message_reports_broken_environment() -> None:
    message = build_whisper_import_error_message(
        whisper_available=True,
    )

    assert "Whisper is installed, but the Python environment looks broken." in message
    assert ".venv" in message
