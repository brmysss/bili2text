from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from b2t.cli import main
except ModuleNotFoundError as exc:
    missing = exc.name or "dependency"
    from b2t.i18n import dependency_sync_guidance

    def main() -> None:
        raise SystemExit(
            f"Missing dependency '{missing}'. {dependency_sync_guidance('en-US')}"
        )


if __name__ == "__main__":
    main()
