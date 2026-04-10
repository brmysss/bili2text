from __future__ import annotations

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel

from b2t.config import Settings
from b2t.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, tr
from b2t.user_config import ALL_PROVIDERS, AppConfig


def run_bootstrap(*, settings: Settings, interactive: bool = True) -> AppConfig:
    config = AppConfig.load(settings)
    if not interactive:
        config.save(settings)
        return config

    console = Console()
    lang = config.language or DEFAULT_LANGUAGE

    console.print()
    console.print(
        Panel.fit(
            tr(lang, "bootstrap_intro"),
            title=tr(lang, "bootstrap_title"),
            border_style="cyan",
        )
    )
    console.print()

    # ── 1. Language ──────────────────────────────────────────
    language_choices = [
        {"name": f"{label}  ({code})", "value": code}
        for code, label in SUPPORTED_LANGUAGES.items()
    ]
    config.language = inquirer.select(
        message=tr(lang, "bootstrap_language_prompt"),
        choices=language_choices,
        default=config.language,
    ).execute()
    lang = config.language

    # ── 2. Providers (checkbox) ──────────────────────────────
    console.print()
    provider_choices = [
        {
            "name": f"whisper    — {tr(lang, 'provider_whisper_short')}",
            "value": "whisper",
            "enabled": "whisper" in config.enabled_providers,
        },
        {
            "name": f"sensevoice — {tr(lang, 'provider_sensevoice_short')}",
            "value": "sensevoice",
            "enabled": "sensevoice" in config.enabled_providers,
        },
        {
            "name": f"volcengine — {tr(lang, 'provider_volcengine_short')}",
            "value": "volcengine",
            "enabled": "volcengine" in config.enabled_providers,
        },
    ]
    selected_providers: list[str] = inquirer.checkbox(
        message=tr(lang, "bootstrap_providers_prompt"),
        choices=provider_choices,
        validate=lambda result: len(result) >= 1,
        invalid_message=tr(lang, "bootstrap_providers_validate"),
    ).execute()
    config.enabled_providers = selected_providers

    # ── 3. Configure each selected provider ──────────────────
    for provider in selected_providers:
        console.print()
        console.rule(f"[bold cyan]{tr(lang, f'provider_{provider}_name')}[/bold cyan]")
        console.print(f"[dim]{tr(lang, f'provider_{provider}_desc')}[/dim]")
        console.print()

        if provider == "whisper":
            _configure_whisper(config, lang)
        elif provider == "sensevoice":
            _configure_sensevoice(config, lang)
        elif provider == "volcengine":
            _configure_volcengine(config, lang)

    # ── 4. Pick default provider ─────────────────────────────
    console.print()
    if len(selected_providers) == 1:
        config.default_provider = selected_providers[0]
    else:
        default_choices = [
            {"name": f"{p} — {tr(lang, f'provider_{p}_short')}", "value": p}
            for p in selected_providers
        ]
        config.default_provider = inquirer.select(
            message=tr(lang, "bootstrap_default_provider_prompt"),
            choices=default_choices,
            default=config.default_provider if config.default_provider in selected_providers else selected_providers[0],
        ).execute()

    # ── Save ─────────────────────────────────────────────────
    config.save(settings)
    console.print()
    console.print(f"[green]{tr(lang, 'bootstrap_saved', path=settings.config_path)}[/green]")
    console.print(tr(lang, "bootstrap_finish"))
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


# ── Provider configuration flows ─────────────────────────────


def _configure_whisper(config: AppConfig, lang: str) -> None:
    whisper_model = inquirer.select(
        message=tr(lang, "bootstrap_whisper_model_prompt"),
        choices=[
            {"name": "tiny    — " + tr(lang, "whisper_model_tiny"), "value": "tiny"},
            {"name": "base    — " + tr(lang, "whisper_model_base"), "value": "base"},
            {"name": "small   — " + tr(lang, "whisper_model_small"), "value": "small"},
            {"name": "medium  — " + tr(lang, "whisper_model_medium"), "value": "medium"},
            {"name": "large   — " + tr(lang, "whisper_model_large"), "value": "large"},
        ],
        default=config.default_model if config.default_model in ("tiny", "base", "small", "medium", "large") else "small",
    ).execute()
    # Only set default_model if whisper is (or becomes) default
    if config.default_provider == "whisper" or len(config.enabled_providers) == 1:
        config.default_model = whisper_model


def _configure_sensevoice(config: AppConfig, lang: str) -> None:
    config.sensevoice.model_dir = inquirer.text(
        message=tr(lang, "bootstrap_sensevoice_dir_prompt"),
        default=config.sensevoice.model_dir,
    ).execute().strip()
    config.sensevoice.language = inquirer.select(
        message=tr(lang, "bootstrap_sensevoice_lang_prompt"),
        choices=[
            {"name": "auto (" + tr(lang, "sensevoice_lang_auto") + ")", "value": "auto"},
            {"name": "zh", "value": "zh"},
            {"name": "en", "value": "en"},
            {"name": "ja", "value": "ja"},
            {"name": "ko", "value": "ko"},
            {"name": "yue (Cantonese)", "value": "yue"},
        ],
        default=config.sensevoice.language,
    ).execute()
    config.sensevoice.use_itn = inquirer.confirm(
        message=tr(lang, "bootstrap_sensevoice_itn_prompt"),
        default=config.sensevoice.use_itn,
    ).execute()


def _configure_volcengine(config: AppConfig, lang: str) -> None:
    config.volcengine.api_key = inquirer.secret(
        message=tr(lang, "bootstrap_volc_api_key_prompt"),
        default=config.volcengine.api_key,
    ).execute().strip()
    config.volcengine.app_key = inquirer.secret(
        message=tr(lang, "bootstrap_volc_app_key_prompt"),
        default=config.volcengine.app_key,
    ).execute().strip()
    config.volcengine.access_key = inquirer.secret(
        message=tr(lang, "bootstrap_volc_access_key_prompt"),
        default=config.volcengine.access_key,
    ).execute().strip()
    config.volcengine.resource_id = inquirer.text(
        message=tr(lang, "bootstrap_volc_resource_prompt"),
        default=config.volcengine.resource_id,
    ).execute().strip()
    config.volcengine.model_name = inquirer.text(
        message=tr(lang, "bootstrap_volc_model_prompt"),
        default=config.volcengine.model_name,
    ).execute().strip()
    config.volcengine.use_itn = inquirer.confirm(
        message=tr(lang, "bootstrap_volc_itn_prompt"),
        default=config.volcengine.use_itn,
    ).execute()
