from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import typer

from b2t import __version__
from b2t.bootstrap import ensure_bootstrap, run_bootstrap
from b2t.config import Settings
from b2t.factory import build_pipeline
from b2t.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, resolve_language, tr
from b2t.user_config import AppConfig


def create_app(language: str = DEFAULT_LANGUAGE) -> typer.Typer:
    app = typer.Typer(
        add_completion=False,
        no_args_is_help=True,
        help=tr(language, "app_help"),
    )

    @app.callback(invoke_without_command=True)
    def version_callback(
        version: bool = typer.Option(
            False,
            "--version",
            help=tr(language, "show_version"),
            is_eager=True,
        ),
    ) -> None:
        if version:
            typer.echo(__version__)
            raise typer.Exit()

    @app.command("transcribe", help=tr(language, "cmd_transcribe_help"))
    @app.command("tx", hidden=True)
    def transcribe(
        source: str = typer.Argument(..., help=tr(language, "arg_source_help")),
        provider: str | None = typer.Option(None, "--provider", help=tr(language, "opt_provider_help")),
        model: str | None = typer.Option(None, "--model", help=tr(language, "opt_model_help")),
        prompt: str = typer.Option("", "--prompt", help=tr(language, "opt_prompt_help")),
        output: Path | None = typer.Option(None, "--output", help=tr(language, "opt_output_help")),
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Download or open media, then transcribe it with the selected provider."""
        try:
            settings, config = _load_runtime(workspace=workspace, provider=provider, model=model)
            pipeline = build_pipeline(settings=settings, config=config, provider=provider, model=model)
            result = pipeline.transcribe(source, prompt=prompt or None, output=output)
        except Exception as exc:
            message = tr(_detect_preferred_language(workspace), "error_prefix", message=exc)
            typer.secho(message, err=True, fg=typer.colors.RED)
            raise typer.Exit(code=1) from exc

        typer.echo(tr(config.language, "transcript_saved", path=result.transcript_path))
        typer.echo(tr(config.language, "metadata_saved", path=result.metadata_path))

    @app.command("doctor", help=tr(language, "cmd_doctor_help"))
    @app.command("diag", hidden=True)
    def doctor(
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Print the current runtime requirements and what is missing."""
        selected_language = _detect_preferred_language(workspace)
        ffmpeg = shutil.which("ffmpeg")
        rows: list[tuple[str, str]] = [(tr(selected_language, "doctor_ffmpeg"), ffmpeg or tr(selected_language, "status_missing"))]

        try:
            import yt_dlp  # noqa: F401
        except ImportError:
            rows.insert(0, (tr(selected_language, "doctor_yt_dlp"), tr(selected_language, "status_missing")))
        else:
            rows.insert(0, (tr(selected_language, "doctor_yt_dlp"), tr(selected_language, "status_ok")))

        try:
            import whisper  # noqa: F401
        except ImportError:
            rows.append((tr(selected_language, "doctor_whisper"), tr(selected_language, "status_missing")))
        else:
            rows.append((tr(selected_language, "doctor_whisper"), tr(selected_language, "status_ok")))

        try:
            import funasr_onnx  # noqa: F401
        except ImportError:
            rows.append((tr(selected_language, "doctor_sensevoice"), tr(selected_language, "status_missing")))
        else:
            rows.append((tr(selected_language, "doctor_sensevoice"), tr(selected_language, "status_ok")))

        try:
            import requests  # noqa: F401
        except ImportError:
            rows.append((tr(selected_language, "doctor_requests"), tr(selected_language, "status_missing")))
        else:
            rows.append((tr(selected_language, "doctor_requests"), tr(selected_language, "status_ok")))

        for label, status in rows:
            typer.echo(f"{label}: {status}")

    @app.command("bootstrap", help=tr(language, "cmd_bootstrap_help"))
    @app.command("init", hidden=True)
    def bootstrap(
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Create or update the local bili2text config."""
        settings = Settings.from_workspace(workspace)
        run_bootstrap(settings=settings, interactive=True)

    @app.command("web", help=tr(language, "cmd_web_help"))
    @app.command("ui", hidden=True)
    def web_ui(
        host: str = typer.Option("127.0.0.1", "--host", help=tr(language, "opt_host_help")),
        port: int = typer.Option(8000, "--port", help=tr(language, "opt_port_help")),
        provider: str | None = typer.Option(None, "--provider", help=tr(language, "opt_provider_help")),
        model: str | None = typer.Option(None, "--model", help=tr(language, "opt_model_help")),
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Launch the plain HTML web interface."""
        _run_server(host=host, port=port, provider=provider, model=model, workspace=workspace)

    @app.command("server", help=tr(language, "cmd_server_help"))
    @app.command("srv", hidden=True)
    def server_mode(
        host: str = typer.Option("0.0.0.0", "--host", help=tr(language, "opt_host_help")),
        port: int = typer.Option(8000, "--port", help=tr(language, "opt_port_help")),
        provider: str | None = typer.Option(None, "--provider", help=tr(language, "opt_provider_help")),
        model: str | None = typer.Option(None, "--model", help=tr(language, "opt_model_help")),
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Launch the server feature for Docker or LAN deployment."""
        _run_server(host=host, port=port, provider=provider, model=model, workspace=workspace)

    @app.command("window", help=tr(language, "cmd_window_help"))
    @app.command("win", hidden=True)
    def window_mode(
        provider: str | None = typer.Option(None, "--provider", help=tr(language, "opt_provider_help")),
        model: str | None = typer.Option(None, "--model", help=tr(language, "opt_model_help")),
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
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
            language=config.language,
        )

    @app.command("language", help=tr(language, "cmd_language_help"))
    @app.command("lang", hidden=True)
    def language_command(
        value: str = typer.Argument(..., help=tr(language, "opt_language_help")),
        workspace: Path | None = typer.Option(None, "--workspace", help=tr(language, "opt_workspace_help")),
    ) -> None:
        """Switch the preferred interface language."""
        resolved = resolve_language(value)
        if not resolved:
            typer.secho(tr(language, "unsupported_language", language=value), err=True, fg=typer.colors.RED)
            raise typer.Exit(code=1)

        settings = Settings.from_workspace(workspace)
        config = AppConfig.load(settings)
        config.language = resolved
        config.save(settings)
        typer.echo(tr(resolved, "language_updated", language=SUPPORTED_LANGUAGES[resolved]))

    return app


def main() -> None:
    create_app(_detect_preferred_language())(prog_name="bili2text")


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


def _run_server(*, host: str, port: int, provider: str | None, model: str | None, workspace: Path | None) -> None:
    selected_language = _detect_preferred_language(workspace)
    try:
        import uvicorn
    except ImportError as exc:
        typer.secho(
            tr(selected_language, "missing_dependency", name="web/server"),
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
        language=config.language,
    )
    uvicorn.run(app_instance, host=host, port=port)


def _detect_preferred_language(workspace: Path | None = None) -> str:
    env_language = resolve_language(os.getenv("B2T_LANG"))
    if env_language:
        return env_language

    settings = Settings.from_workspace(workspace)
    if settings.config_path.exists():
        return AppConfig.load(settings).language
    return DEFAULT_LANGUAGE


app = create_app(DEFAULT_LANGUAGE)
