from __future__ import annotations

import typer

from b2t.config import Settings
from b2t.user_config import AppConfig


def run_bootstrap(*, settings: Settings, interactive: bool = True) -> AppConfig:
    config = AppConfig.load(settings)
    if not interactive:
        config.save(settings)
        return config

    typer.secho("Welcome to bili2text bootstrap.", fg=typer.colors.CYAN)
    config.default_provider = typer.prompt(
        "Choose default provider [whisper/sensevoice/volcengine]",
        default=config.default_provider,
    ).strip().lower()
    config.default_model = typer.prompt(
        "Choose default model or provider identifier",
        default=config.default_model,
    ).strip()

    config.sensevoice.model_dir = typer.prompt(
        "SenseVoice model directory (optional)",
        default=config.sensevoice.model_dir,
    ).strip()
    config.sensevoice.language = typer.prompt(
        "SenseVoice language",
        default=config.sensevoice.language,
    ).strip()
    config.sensevoice.use_itn = typer.confirm(
        "SenseVoice enable ITN?",
        default=config.sensevoice.use_itn,
    )

    config.volcengine.api_key = typer.prompt(
        "Volcengine API key (optional)",
        default=config.volcengine.api_key,
        show_default=False,
    ).strip()
    config.volcengine.app_key = typer.prompt(
        "Volcengine legacy app key (optional)",
        default=config.volcengine.app_key,
        show_default=False,
    ).strip()
    config.volcengine.access_key = typer.prompt(
        "Volcengine legacy access key (optional)",
        default=config.volcengine.access_key,
        show_default=False,
    ).strip()
    config.volcengine.resource_id = typer.prompt(
        "Volcengine resource id",
        default=config.volcengine.resource_id,
    ).strip()
    config.volcengine.model_name = typer.prompt(
        "Volcengine model name",
        default=config.volcengine.model_name,
    ).strip()
    config.volcengine.use_itn = typer.confirm(
        "Volcengine enable ITN?",
        default=config.volcengine.use_itn,
    )

    config.save(settings)
    typer.echo(f"Config saved to: {settings.config_path}")
    return config


def ensure_bootstrap(*, settings: Settings, allow_prompt: bool = True) -> AppConfig:
    if settings.config_path.exists():
        return AppConfig.load(settings)

    if allow_prompt:
        typer.secho("No bili2text config found. Starting bootstrap...", fg=typer.colors.YELLOW)
        return run_bootstrap(settings=settings, interactive=True)

    config = AppConfig()
    config.save(settings)
    return config
