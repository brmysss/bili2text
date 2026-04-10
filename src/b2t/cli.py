from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer

from b2t import __version__
from b2t.bootstrap import ensure_bootstrap, run_bootstrap
from b2t.config import Settings
from b2t.factory import build_pipeline
from b2t.user_config import AppConfig


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


def _load_runtime(
    *,
    workspace: Path | None,
    provider: str | None = None,
    model: str | None = None,
    allow_bootstrap: bool = True,
) -> tuple[Settings, AppConfig]:
    settings = Settings.from_workspace(workspace)
    config = ensure_bootstrap(
        settings=settings,
        allow_prompt=allow_bootstrap and sys.stdin.isatty(),
    )
    if provider:
        config.default_provider = provider
    if model:
        config.default_model = model
    return settings, config


@app.command()
def transcribe(
    source: str = typer.Argument(..., help="BV id, Bilibili URL, or local audio/video path."),
    provider: str | None = typer.Option(None, "--provider", help="Transcriber provider: whisper, sensevoice, volcengine."),
    model: str | None = typer.Option(None, "--model", help="Model name or provider-specific identifier."),
    prompt: str = typer.Option("", "--prompt", help="Optional transcription prompt."),
    output: Path | None = typer.Option(None, "--output", help="Target transcript file or directory."),
    workspace: Path | None = typer.Option(None, "--workspace", help="Workspace root. Defaults to ./.b2t"),
) -> None:
    """Download or open media, then transcribe it with the selected provider."""
    try:
        settings, config = _load_runtime(workspace=workspace, provider=provider, model=model)
        pipeline = build_pipeline(settings=settings, config=config, provider=provider, model=model)
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
    rows: list[tuple[str, str]] = [("ffmpeg on PATH", ffmpeg or "missing")]

    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        rows.insert(0, ("python package: yt-dlp", "missing"))
    else:
        rows.insert(0, ("python package: yt-dlp", "ok"))

    try:
        import whisper  # noqa: F401
    except ImportError:
        rows.append(("python package: whisper", "missing"))
    else:
        rows.append(("python package: whisper", "ok"))

    try:
        import funasr_onnx  # noqa: F401
    except ImportError:
        rows.append(("python package: funasr-onnx", "missing"))
    else:
        rows.append(("python package: funasr-onnx", "ok"))

    try:
        import requests  # noqa: F401
    except ImportError:
        rows.append(("python package: requests", "missing"))
    else:
        rows.append(("python package: requests", "ok"))

    for label, status in rows:
        typer.echo(f"{label}: {status}")


@app.command()
def bootstrap(
    workspace: Path | None = typer.Option(None, "--workspace", help="Workspace root. Defaults to ./.b2t"),
) -> None:
    """Create or update the local bili2text config."""
    settings = Settings.from_workspace(workspace)
    run_bootstrap(settings=settings, interactive=True)


@app.command(name="web")
def web_ui(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    workspace: Path | None = typer.Option(None, "--workspace"),
) -> None:
    """Launch the plain HTML web interface."""
    _run_server(host=host, port=port, provider=provider, model=model, workspace=workspace)


@app.command(name="server")
def server_mode(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    workspace: Path | None = typer.Option(None, "--workspace"),
) -> None:
    """Launch the server feature for Docker or LAN deployment."""
    _run_server(host=host, port=port, provider=provider, model=model, workspace=workspace)


@app.command(name="window")
def window_mode(
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    workspace: Path | None = typer.Option(None, "--workspace"),
) -> None:
    """Launch the Tk window feature."""
    from b2t.window_app import run_window

    settings, config = _load_runtime(workspace=workspace, provider=provider, model=model)

    run_window(
        pipeline_factory=lambda selected_provider, selected_model, selected_workspace: build_pipeline(
            settings=Settings.from_workspace(selected_workspace or settings.workspace_root),
            config=config,
            provider=selected_provider or provider or config.default_provider,
            model=selected_model or model or config.default_model,
        ),
        default_provider=provider or config.default_provider,
        default_model=model or config.default_model,
        default_workspace=settings.workspace_root,
    )


def main() -> None:
    app(prog_name="bili2text")


def _run_server(*, host: str, port: int, provider: str | None, model: str | None, workspace: Path | None) -> None:
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

    settings, config = _load_runtime(workspace=workspace, provider=provider, model=model)
    app_instance = create_app(
        lambda selected_provider, selected_model: build_pipeline(
            settings=settings,
            config=config,
            provider=selected_provider or provider or config.default_provider,
            model=selected_model or model or config.default_model,
        ),
        default_provider=provider or config.default_provider,
        default_model=model or config.default_model,
    )
    uvicorn.run(app_instance, host=host, port=port)
