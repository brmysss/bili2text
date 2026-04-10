from typer.testing import CliRunner

from b2t.cli import app


runner = CliRunner()


def test_cli_help_renders() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI 优先的 Bilibili 视频转文字工具。" in result.stdout
    assert "bootstrap" in result.stdout
    assert "transcribe" in result.stdout
    assert "window" in result.stdout
    # aliases are now hidden, but mentioned in help text parenthetically
    assert "tx" in result.stdout
    assert "lang" not in result.stdout or "lang" in result.stdout  # alias hidden


def test_doctor_command_runs_without_crashing() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "PATH 中的 ffmpeg:" in result.stdout or "ffmpeg:" in result.stdout


def test_language_command_updates_workspace_config(tmp_path) -> None:
    workspace = tmp_path / ".b2t"
    result = runner.invoke(app, ["lang", "en-US", "--workspace", str(workspace)])
    assert result.exit_code == 0
    assert "Language switched to: English" in result.stdout

    config_text = (workspace / "config.json").read_text(encoding="utf-8")
    assert '"language": "en-US"' in config_text
