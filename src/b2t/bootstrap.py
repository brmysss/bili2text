from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from b2t.config import Settings
from b2t.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, tr
from b2t.user_config import AppConfig


def run_bootstrap(*, settings: Settings, interactive: bool = True) -> AppConfig:
    config = AppConfig.load(settings)
    if not interactive:
        config.save(settings)
        return config

    console = Console()
    initial_language = config.language or DEFAULT_LANGUAGE
    console.print(
        Panel.fit(
            tr(initial_language, "bootstrap_intro"),
            title=tr(initial_language, "bootstrap_title"),
            border_style="cyan",
        )
    )

    config.language = _prompt_language(console, default=config.language or DEFAULT_LANGUAGE)
    console.print()
    console.print(f"[bold]{tr(config.language, 'bootstrap_section_providers')}[/bold]")
    console.print(tr(config.language, "bootstrap_provider_tip"))
    console.print(_provider_overview_table(config.language))
    console.print()

    config.default_provider = Prompt.ask(
        tr(config.language, "bootstrap_provider_prompt"),
        choices=["whisper", "sensevoice", "volcengine"],
        default=config.default_provider,
        console=console,
    ).strip()
    config.default_model = Prompt.ask(
        tr(config.language, "bootstrap_model_prompt"),
        default=config.default_model,
        console=console,
    ).strip()

    console.print()
    console.rule(tr(config.language, "bootstrap_section_defaults"))
    config.sensevoice.model_dir = Prompt.ask(
        tr(config.language, "bootstrap_sensevoice_dir_prompt"),
        default=config.sensevoice.model_dir,
        console=console,
    ).strip()
    config.sensevoice.language = Prompt.ask(
        tr(config.language, "bootstrap_sensevoice_lang_prompt"),
        default=config.sensevoice.language,
        console=console,
    ).strip()
    config.sensevoice.use_itn = Confirm.ask(
        tr(config.language, "bootstrap_sensevoice_itn_prompt"),
        default=config.sensevoice.use_itn,
        console=console,
    )

    config.volcengine.api_key = Prompt.ask(
        tr(config.language, "bootstrap_volc_api_key_prompt"),
        default=config.volcengine.api_key,
        show_default=False,
        console=console,
    ).strip()
    config.volcengine.app_key = Prompt.ask(
        tr(config.language, "bootstrap_volc_app_key_prompt"),
        default=config.volcengine.app_key,
        show_default=False,
        console=console,
    ).strip()
    config.volcengine.access_key = Prompt.ask(
        tr(config.language, "bootstrap_volc_access_key_prompt"),
        default=config.volcengine.access_key,
        show_default=False,
        console=console,
    ).strip()
    config.volcengine.resource_id = Prompt.ask(
        tr(config.language, "bootstrap_volc_resource_prompt"),
        default=config.volcengine.resource_id,
        console=console,
    ).strip()
    config.volcengine.model_name = Prompt.ask(
        tr(config.language, "bootstrap_volc_model_prompt"),
        default=config.volcengine.model_name,
        console=console,
    ).strip()
    config.volcengine.use_itn = Confirm.ask(
        tr(config.language, "bootstrap_volc_itn_prompt"),
        default=config.volcengine.use_itn,
        console=console,
    )

    config.save(settings)
    console.print()
    console.print(f"[green]{tr(config.language, 'bootstrap_saved', path=settings.config_path)}[/green]")
    console.print(tr(config.language, "bootstrap_finish"))
    return config


def ensure_bootstrap(*, settings: Settings, allow_prompt: bool = True) -> AppConfig:
    if settings.config_path.exists():
        return AppConfig.load(settings)

    if allow_prompt:
        Console().print(f"[yellow]{tr(DEFAULT_LANGUAGE, 'bootstrap_auto_start')}[/yellow]")
        return run_bootstrap(settings=settings, interactive=True)

    config = AppConfig()
    config.save(settings)
    return config


def _prompt_language(console: Console, *, default: str) -> str:
    console.rule(tr(default, "bootstrap_section_language"))
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column(tr(default, "bootstrap_language_choices"))
    for index, (code, label) in enumerate(SUPPORTED_LANGUAGES.items(), start=1):
        table.add_row(str(index), f"{label} ({code})")
    console.print(table)

    choices = {str(index): code for index, code in enumerate(SUPPORTED_LANGUAGES.keys(), start=1)}
    reverse = {code: key for key, code in choices.items()}
    selected = Prompt.ask(
        tr(default, "bootstrap_language_prompt"),
        choices=list(choices.keys()),
        default=reverse.get(default, "1"),
        console=console,
    )
    return choices[selected]


def _provider_overview_table(language: str) -> Table:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column(tr(language, "bootstrap_provider_name_col"), style="bold")
    table.add_column(tr(language, "bootstrap_provider_usage_col"))
    table.add_row("whisper", _provider_label(language, "whisper"))
    table.add_row("sensevoice", _provider_label(language, "sensevoice"))
    table.add_row("volcengine", _provider_label(language, "volcengine"))
    return table


def _provider_label(language: str, provider: str) -> str:
    return f"{tr(language, f'provider_{provider}_name')}\n{tr(language, f'provider_{provider}_desc')}"
