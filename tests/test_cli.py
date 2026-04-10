from typer.testing import CliRunner

from b2t.cli import app


runner = CliRunner()


def test_cli_help_renders() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI-first Bilibili to text toolkit." in result.stdout
    assert "transcribe" in result.stdout


def test_doctor_command_runs_without_crashing() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "ffmpeg on PATH:" in result.stdout
