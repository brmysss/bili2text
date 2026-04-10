from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from b2t.cli import build_pipeline
    from b2t.window_app import run_window
except ModuleNotFoundError as exc:
    missing = exc.name or "dependency"

    def main() -> None:
        raise SystemExit(
            f"Missing dependency '{missing}'. Run `uv sync --extra whisper --extra web` first."
        )
else:
    def main() -> None:
        run_window(
            pipeline_factory=lambda model, workspace: build_pipeline(workspace=workspace, model=model),
            default_model="small",
        )


if __name__ == "__main__":
    main()
