from __future__ import annotations

import shutil
from pathlib import Path

import typer

from b2t import __version__
from b2t.config import Settings
from b2t.downloaders import YtDlpDownloader
from b2t.pipeline import B2TPipeline
from b2t.transcribers import LocalWhisperTranscriber


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="CLI-first Bilibili to text toolkit.",
)


@app.callback(invoke_without_command=True)
def version_callback(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the current version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def build_pipeline(*, workspace: Path | None, model: str) -> B2TPipeline:
    settings = Settings.from_workspace(workspace)
    return B2TPipeline(
        settings=settings,
        downloader=YtDlpDownloader(),
        transcriber=LocalWhisperTranscriber(model=model),
    )


@app.command()
def transcribe(
    source: str = typer.Argument(..., help="BV id, Bilibili URL, or local audio/video path."),
    model: str = typer.Option("small", "--model", help="Whisper model name."),
    prompt: str = typer.Option("", "--prompt", help="Optional transcription prompt."),
    output: Path | None = typer.Option(None, "--output", help="Target transcript file or directory."),
    workspace: Path | None = typer.Option(None, "--workspace", help="Workspace root. Defaults to ./.b2t"),
) -> None:
    """Download or open media, then transcribe it with Whisper."""
    try:
        pipeline = build_pipeline(workspace=workspace, model=model)
        result = pipeline.transcribe(source, prompt=prompt or None, output=output)
    except Exception as exc:
        typer.secho(f"error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Transcript saved to: {result.transcript_path}")
    typer.echo(f"Metadata saved to: {result.metadata_path}")


@app.command()
def doctor() -> None:
    """Print the current runtime requirements and what is missing."""
    ffmpeg = shutil.which("ffmpeg")
    rows = [
        ("python package: yt-dlp", "ok"),
        ("ffmpeg on PATH", ffmpeg or "missing"),
    ]

    try:
        import whisper  # noqa: F401
    except ImportError:
        rows.append(("python package: whisper", "missing"))
    else:
        rows.append(("python package: whisper", "ok"))

    for label, status in rows:
        typer.echo(f"{label}: {status}")


@app.command(name="web")
def web_ui(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    model: str = typer.Option("small", "--model"),
    workspace: Path | None = typer.Option(None, "--workspace"),
) -> None:
    """Launch the plain HTML web interface."""
    _run_server(host=host, port=port, model=model, workspace=workspace)


@app.command(name="server")
def server_mode(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
    model: str = typer.Option("small", "--model"),
    workspace: Path | None = typer.Option(None, "--workspace"),
) -> None:
    """Launch the server feature for Docker or LAN deployment."""
    _run_server(host=host, port=port, model=model, workspace=workspace)


def main() -> None:
    app(prog_name="bili2text")


def _run_server(*, host: str, port: int, model: str, workspace: Path | None) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        typer.secho(
            "error: web/server support is not installed. Run `uv sync --extra web`.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1) from exc

    from b2t.web import create_app

    app_instance = create_app(
        lambda selected_model: build_pipeline(workspace=workspace, model=selected_model or model),
        default_model=model,
    )
    uvicorn.run(app_instance, host=host, port=port)
