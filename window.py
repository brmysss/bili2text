from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from b2t.bootstrap import ensure_bootstrap
    from b2t.config import Settings
    from b2t.factory import build_pipeline
    from b2t.window_app import run_window
except ModuleNotFoundError as exc:
    missing = exc.name or "dependency"

    def main() -> None:
        raise SystemExit(
            f"Missing dependency '{missing}'. Run `uv sync --extra whisper --extra web` first."
        )
else:
    def main() -> None:
        settings = Settings.from_workspace(None)
        config = ensure_bootstrap(settings=settings, allow_prompt=sys.stdin.isatty())
        run_window(
            pipeline_factory=lambda provider, model, workspace: build_pipeline(
                settings=Settings.from_workspace(workspace or settings.workspace_root),
                config=config,
                provider=provider or config.default_provider,
                model=model or config.default_model,
            ),
            default_provider=config.default_provider,
            default_model=config.default_model,
            default_workspace=settings.workspace_root,
        )


if __name__ == "__main__":
    main()
