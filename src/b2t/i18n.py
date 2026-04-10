from __future__ import annotations

from typing import Any


DEFAULT_LANGUAGE = "zh-CN"
SUPPORTED_LANGUAGES = {
    "zh-CN": "简体中文",
    "en-US": "English",
}


MESSAGES: dict[str, dict[str, str]] = {
    "zh-CN": {
        # ── CLI help ─────────────────────────────────────────
        "app_help": "CLI 优先的 Bilibili 视频转文字工具。",
        "show_version": "显示版本号。",
        "cmd_transcribe_help": "转写视频或音频（缩写: tx）。",
        "cmd_doctor_help": "检查运行环境（缩写: diag）。",
        "cmd_bootstrap_help": "初始化配置文件（缩写: init）。",
        "cmd_web_help": "启动 Web 界面（缩写: ui）。",
        "cmd_server_help": "启动服务模式，适用于 Docker / 局域网（缩写: srv）。",
        "cmd_window_help": "启动桌面窗口（缩写: win）。",
        "cmd_language_help": "切换界面语言（缩写: lang）。",
        "arg_source_help": "BV 号、Bilibili 链接或本地文件路径。",
        "opt_provider_help": "转写引擎: whisper / sensevoice / volcengine。",
        "opt_model_help": "模型名称。",
        "opt_prompt_help": "转写提示词（可选）。",
        "opt_output_help": "输出文件或目录。",
        "opt_workspace_help": "工作目录，默认 ./.b2t。",
        "opt_host_help": "监听地址。",
        "opt_port_help": "监听端口。",
        "opt_language_help": "语言代码，如 zh-CN、en-US。",

        # ── Runtime messages ─────────────────────────────────
        "missing_dependency": "缺少依赖 '{name}'，请运行 `uv sync --extra whisper --extra web` 安装。",
        "transcript_saved": "转写结果已保存: {path}",
        "metadata_saved": "元数据已保存: {path}",
        "error_prefix": "出错了: {message}",

        # ── Doctor ───────────────────────────────────────────
        "doctor_yt_dlp": "yt-dlp",
        "doctor_ffmpeg": "ffmpeg",
        "doctor_whisper": "whisper",
        "doctor_sensevoice": "funasr-onnx",
        "doctor_requests": "requests",
        "status_ok": "✓ 可用",
        "status_missing": "✗ 缺失",

        # ── Bootstrap ────────────────────────────────────────
        "bootstrap_title": "bili2text 初始化向导",
        "bootstrap_intro": "欢迎！接下来会帮你选好语言和转写引擎，几步就能搞定。",
        "bootstrap_language_prompt": "选一个你习惯的语言",
        "bootstrap_providers_prompt": "勾选你要用的转写引擎（空格选中，回车确认）",
        "bootstrap_providers_validate": "至少选一个引擎",
        "bootstrap_default_provider_prompt": "哪个作为默认引擎？",
        "bootstrap_provider_prompt": "选择默认转写引擎",
        "bootstrap_model_prompt": "模型名称",
        "bootstrap_whisper_model_prompt": "选择 Whisper 模型（越大越准，也越慢）",
        "bootstrap_sensevoice_dir_prompt": "SenseVoice 模型目录（留空用默认）",
        "bootstrap_sensevoice_lang_prompt": "SenseVoice 识别语言",
        "bootstrap_sensevoice_itn_prompt": "开启逆文本正则化（把数字、日期转为自然格式）",
        "bootstrap_volc_api_key_prompt": "火山引擎 API Key",
        "bootstrap_volc_app_key_prompt": "火山引擎 App Key（旧版，没有可留空）",
        "bootstrap_volc_access_key_prompt": "火山引擎 Access Key（旧版，没有可留空）",
        "bootstrap_volc_resource_prompt": "火山引擎 Resource ID",
        "bootstrap_volc_model_prompt": "火山引擎模型名称",
        "bootstrap_volc_itn_prompt": "开启逆文本正则化",
        "bootstrap_saved": "配置已保存到 {path}",
        "bootstrap_auto_start": "还没有配置文件，来走一下初始化向导吧……",
        "bootstrap_finish": "搞定！随时可以用 `bili2text bootstrap` 重新配置，或 `bili2text lang <代码>` 切换语言。",

        # ── Whisper model descriptions ───────────────────────
        "whisper_model_tiny": "最快，精度一般，适合快速测试",
        "whisper_model_base": "速度较快，精度尚可",
        "whisper_model_small": "平衡之选，推荐大多数场景",
        "whisper_model_medium": "精度更高，速度较慢",
        "whisper_model_large": "最高精度，需要较多显存",

        # ── SenseVoice language descriptions ─────────────────
        "sensevoice_lang_auto": "自动检测",

        # ── Provider short descriptions (for select menu) ────
        "provider_whisper_short": "本地离线，零云依赖，开箱即用",
        "provider_sensevoice_short": "本地 ONNX 模型，中文效果好",
        "provider_volcengine_short": "火山引擎云端 ASR，需要凭据",
        # ── Provider full descriptions (kept for reference) ──
        "provider_whisper_name": "Whisper 本地模型",
        "provider_whisper_desc": "离线运行，不依赖任何云服务。需要本机安装 Whisper 环境。",
        "provider_sensevoice_name": "SenseVoice 本地模型",
        "provider_sensevoice_desc": "基于 ONNX 的本地模型，中文识别效果不错。需要模型文件和运行依赖。",
        "provider_volcengine_name": "火山引擎云端识别",
        "provider_volcengine_desc": "商用云端 ASR，适合服务化部署。需要配置火山引擎凭据。",

        # ── Language ─────────────────────────────────────────
        "language_updated": "语言已切换为: {language}",
        "unsupported_language": "不支持的语言: {language}",

        # ── Window ───────────────────────────────────────────
        "window_title": "bili2text",
        "window_source": "输入源",
        "window_provider": "转写引擎",
        "window_model": "模型",
        "window_workspace": "工作目录",
        "window_prompt": "提示词",
        "window_choose_file": "选择文件",
        "window_browse": "浏览",
        "window_start": "开始转写",
        "window_clear_log": "清空日志",
        "window_open_transcript": "打开结果",
        "window_open_workspace": "打开目录",
        "window_open_repo": "打开仓库",
        "window_log": "日志",
        "window_result_preview": "转写预览",
        "window_choose_workspace": "选择工作目录",
        "window_status_ready": "就绪",
        "window_status_running": "运行中",
        "window_status_completed": "完成",
        "window_status_failed": "失败",
        "window_missing_source": "请输入 BV 号、视频链接或本地文件路径。",
        "window_no_result": "还没有转写结果。",
        "window_starting": "开始转写: provider={provider}, model={model}",
        "window_pipeline_ready": "Pipeline 就绪，工作目录: {workspace}",
        "window_error": "出错了: {message}",

        # ── Web ──────────────────────────────────────────────
        "web_title": "bili2text",
        "web_subtitle": "Bilibili 视频转文字",
        "web_error": "出错了",
        "web_form_title": "开始转写",
        "web_source": "BV / URL / 本地路径",
        "web_provider": "转写引擎",
        "web_model": "模型",
        "web_prompt": "提示词",
        "web_submit": "开始",
        "web_result_title": "转写完成",
        "web_back_home": "返回首页",
        "web_result_files": "输出文件",
        "web_result_provider": "转写引擎",
        "web_result_model": "模型",
        "web_result_transcript": "文本文件",
        "web_result_metadata": "元数据",
        "web_result_audio": "音频",
        "web_result_video": "视频",
        "web_result_text": "文本内容",
    },
    "en-US": {
        # ── CLI help ─────────────────────────────────────────
        "app_help": "CLI-first Bilibili video-to-text toolkit.",
        "show_version": "Show version.",
        "cmd_transcribe_help": "Transcribe a video or audio file (alias: tx).",
        "cmd_doctor_help": "Check runtime dependencies (alias: diag).",
        "cmd_bootstrap_help": "Set up your config file (alias: init).",
        "cmd_web_help": "Launch the web UI (alias: ui).",
        "cmd_server_help": "Start server mode for Docker / LAN (alias: srv).",
        "cmd_window_help": "Launch the desktop window (alias: win).",
        "cmd_language_help": "Switch the interface language (alias: lang).",
        "arg_source_help": "BV id, Bilibili URL, or a local media file.",
        "opt_provider_help": "Transcription engine: whisper / sensevoice / volcengine.",
        "opt_model_help": "Model name.",
        "opt_prompt_help": "Optional transcription prompt.",
        "opt_output_help": "Output file or directory.",
        "opt_workspace_help": "Workspace root, defaults to ./.b2t.",
        "opt_host_help": "Bind address.",
        "opt_port_help": "Bind port.",
        "opt_language_help": "Language code, e.g. zh-CN or en-US.",

        # ── Runtime messages ─────────────────────────────────
        "missing_dependency": "Missing dependency '{name}'. Run `uv sync --extra whisper --extra web` to install.",
        "transcript_saved": "Transcript saved: {path}",
        "metadata_saved": "Metadata saved: {path}",
        "error_prefix": "Error: {message}",

        # ── Doctor ───────────────────────────────────────────
        "doctor_yt_dlp": "yt-dlp",
        "doctor_ffmpeg": "ffmpeg",
        "doctor_whisper": "whisper",
        "doctor_sensevoice": "funasr-onnx",
        "doctor_requests": "requests",
        "status_ok": "✓ ok",
        "status_missing": "✗ missing",

        # ── Bootstrap ────────────────────────────────────────
        "bootstrap_title": "bili2text setup",
        "bootstrap_intro": "Welcome! Let's pick your language and transcription engine — it only takes a moment.",
        "bootstrap_language_prompt": "Pick your preferred language",
        "bootstrap_providers_prompt": "Check the engines you want to use (space to toggle, enter to confirm)",
        "bootstrap_providers_validate": "Select at least one engine",
        "bootstrap_default_provider_prompt": "Which one should be the default?",
        "bootstrap_provider_prompt": "Choose the default transcription engine",
        "bootstrap_model_prompt": "Model name",
        "bootstrap_whisper_model_prompt": "Pick a Whisper model (bigger = more accurate but slower)",
        "bootstrap_sensevoice_dir_prompt": "SenseVoice model directory (leave empty for default)",
        "bootstrap_sensevoice_lang_prompt": "SenseVoice recognition language",
        "bootstrap_sensevoice_itn_prompt": "Enable inverse text normalization (formats numbers, dates, etc.)",
        "bootstrap_volc_api_key_prompt": "Volcengine API key",
        "bootstrap_volc_app_key_prompt": "Volcengine App key (legacy, skip if you don't have one)",
        "bootstrap_volc_access_key_prompt": "Volcengine Access key (legacy, skip if you don't have one)",
        "bootstrap_volc_resource_prompt": "Volcengine resource ID",
        "bootstrap_volc_model_prompt": "Volcengine model name",
        "bootstrap_volc_itn_prompt": "Enable inverse text normalization",
        "bootstrap_saved": "Config saved to {path}",
        "bootstrap_auto_start": "No config file found — let's set things up...",
        "bootstrap_finish": "All done! Run `bili2text bootstrap` anytime to reconfigure, or `bili2text lang <code>` to switch languages.",

        # ── Whisper model descriptions ───────────────────────
        "whisper_model_tiny": "Fastest, low accuracy, good for quick tests",
        "whisper_model_base": "Fast, decent accuracy",
        "whisper_model_small": "Balanced — recommended for most use cases",
        "whisper_model_medium": "Higher accuracy, slower",
        "whisper_model_large": "Best accuracy, needs more VRAM",

        # ── SenseVoice language descriptions ─────────────────
        "sensevoice_lang_auto": "auto-detect",

        # ── Provider short descriptions (for select menu) ────
        "provider_whisper_short": "Local & offline, no cloud needed",
        "provider_sensevoice_short": "Local ONNX model, great for Chinese",
        "provider_volcengine_short": "Volcengine cloud ASR, needs credentials",
        # ── Provider full descriptions ───────────────────────
        "provider_whisper_name": "Whisper local model",
        "provider_whisper_desc": "Runs fully offline. Needs a local Whisper installation.",
        "provider_sensevoice_name": "SenseVoice local model",
        "provider_sensevoice_desc": "ONNX-based local model, solid Chinese recognition. Requires model files and runtime deps.",
        "provider_volcengine_name": "Volcengine cloud ASR",
        "provider_volcengine_desc": "Commercial cloud ASR for service deployments. Requires Volcengine credentials.",

        # ── Language ─────────────────────────────────────────
        "language_updated": "Language switched to: {language}",
        "unsupported_language": "Unsupported language: {language}",

        # ── Window ───────────────────────────────────────────
        "window_title": "bili2text",
        "window_source": "Source",
        "window_provider": "Engine",
        "window_model": "Model",
        "window_workspace": "Workspace",
        "window_prompt": "Prompt",
        "window_choose_file": "Choose File",
        "window_browse": "Browse",
        "window_start": "Start",
        "window_clear_log": "Clear Log",
        "window_open_transcript": "Open Transcript",
        "window_open_workspace": "Open Workspace",
        "window_open_repo": "Open Repo",
        "window_log": "Log",
        "window_result_preview": "Transcript Preview",
        "window_choose_workspace": "Choose Workspace",
        "window_status_ready": "Ready",
        "window_status_running": "Running",
        "window_status_completed": "Done",
        "window_status_failed": "Failed",
        "window_missing_source": "Enter a BV id, URL, or local media file path.",
        "window_no_result": "No transcript result yet.",
        "window_starting": "Starting transcription: provider={provider}, model={model}",
        "window_pipeline_ready": "Pipeline ready. Workspace: {workspace}",
        "window_error": "Error: {message}",

        # ── Web ──────────────────────────────────────────────
        "web_title": "bili2text",
        "web_subtitle": "Bilibili video-to-text toolkit.",
        "web_error": "Error",
        "web_form_title": "Transcribe",
        "web_source": "BV / URL / local path",
        "web_provider": "Engine",
        "web_model": "Model",
        "web_prompt": "Prompt",
        "web_submit": "Start",
        "web_result_title": "Transcription Complete",
        "web_back_home": "Back to Home",
        "web_result_files": "Output Files",
        "web_result_provider": "Engine",
        "web_result_model": "Model",
        "web_result_transcript": "Transcript",
        "web_result_metadata": "Metadata",
        "web_result_audio": "Audio",
        "web_result_video": "Video",
        "web_result_text": "Transcript Text",
    },
}


def normalize_language(value: str | None) -> str:
    resolved = resolve_language(value)
    if resolved:
        return resolved
    return DEFAULT_LANGUAGE


def resolve_language(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    lowered = normalized.lower()
    if lowered in {"zh", "zh-cn", "zh_hans"}:
        return "zh-CN"
    if lowered in {"en", "en-us"}:
        return "en-US"
    return None


def tr(locale: str | None, key: str, **kwargs: Any) -> str:
    lang = normalize_language(locale)
    template = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE]).get(key, key)
    return template.format(**kwargs)
