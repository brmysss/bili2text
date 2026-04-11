# Bootstrap UV Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Bootstrap generate and run one correct `uv sync --extra ...` command from the selected providers and features.

**Architecture:** Keep environment planning in pure helper functions and let the interactive Bootstrap flow orchestrate prompts, summary rendering, confirmation, and command execution. Persist enough configuration to support later environment resync.

**Tech Stack:** Python, Typer, InquirerPy, Rich, pytest, subprocess

---

### Task 1: Add Environment Planning Tests

**Files:**
- Create: `tests/test_bootstrap_env.py`
- Modify: `src/b2t/bootstrap.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from b2t.bootstrap import build_uv_sync_command, collect_required_extras, uv_available


def test_collect_required_extras_combines_providers_and_features() -> None:
    assert collect_required_extras(
        providers=["whisper", "volcengine"],
        features=["web", "window"],
    ) == ["whisper", "volcengine", "web"]


def test_build_uv_sync_command_is_stable() -> None:
    command = build_uv_sync_command(
        workspace=Path("D:/repo"),
        extras=["whisper", "web"],
    )
    assert command == ["uv", "sync", "--extra", "whisper", "--extra", "web"]


def test_uv_available_uses_path_lookup() -> None:
    assert uv_available(lambda _name: "C:/bin/uv.exe") is True
    assert uv_available(lambda _name: None) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py -q`
Expected: FAIL with import errors because the helper functions do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
import shutil
from pathlib import Path


def uv_available(which=shutil.which) -> bool:
    return which("uv") is not None


def collect_required_extras(*, providers: list[str], features: list[str]) -> list[str]:
    extras: list[str] = []
    for name in [*providers, *features]:
        mapped = name if name != "window" else ""
        if mapped and mapped not in extras:
            extras.append(mapped)
    return extras


def build_uv_sync_command(*, workspace: Path, extras: list[str]) -> list[str]:
    command = ["uv", "sync"]
    for extra in extras:
        command.extend(["--extra", extra])
    return command
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_bootstrap_env.py src/b2t/bootstrap.py
git commit -m "test: cover bootstrap uv environment planning"
```

### Task 2: Persist Enabled Features

**Files:**
- Modify: `src/b2t/user_config.py`
- Modify: `tests/test_user_config.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_config_round_trip(tmp_path: Path) -> None:
    settings = Settings.from_workspace(tmp_path / ".b2t")
    config = AppConfig(
        default_provider="sensevoice",
        default_model="C:/models/sensevoice-small",
        language="en-US",
    )
    config.enabled_features = ["web", "window"]
    config.save(settings)

    loaded = AppConfig.load(settings)
    assert loaded.enabled_features == ["web", "window"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python -m pytest tests/test_user_config.py::test_app_config_round_trip -q`
Expected: FAIL because `enabled_features` is not defined.

- [ ] **Step 3: Write minimal implementation**

```python
ALL_FEATURES = ("web", "server", "window")


@dataclass(slots=True)
class AppConfig:
    language: str = DEFAULT_LANGUAGE
    enabled_providers: list[str] = field(default_factory=lambda: ["whisper"])
    enabled_features: list[str] = field(default_factory=lambda: ["window"])
```

And load with backward-compatible defaults:

```python
features = data.get("enabled_features", ["window"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python -m pytest tests/test_user_config.py::test_app_config_round_trip -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/b2t/user_config.py tests/test_user_config.py
git commit -m "feat: persist bootstrap feature selections"
```

### Task 3: Wire UV Sync Into Bootstrap

**Files:**
- Modify: `src/b2t/bootstrap.py`
- Modify: `src/b2t/i18n.py`
- Modify: `tests/test_bootstrap_env.py`

- [ ] **Step 1: Write the failing test**

```python
from b2t.bootstrap import BootstrapEnvironmentResult, sync_selected_environment


def test_sync_selected_environment_reports_missing_uv(tmp_path: Path) -> None:
    result = sync_selected_environment(
        workspace=tmp_path,
        extras=["whisper", "web"],
        which=lambda _name: None,
        runner=None,
    )
    assert result.ok is False
    assert result.reason == "missing_uv"


def test_sync_selected_environment_runs_uv_sync(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_runner(command, **kwargs):
        calls.append(command)
        return Completed()

    result = sync_selected_environment(
        workspace=tmp_path,
        extras=["whisper", "web"],
        which=lambda _name: "C:/bin/uv.exe",
        runner=fake_runner,
    )
    assert result.ok is True
    assert calls == [["uv", "sync", "--extra", "whisper", "--extra", "web"]]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py -q`
Expected: FAIL because the sync result type and function do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
import subprocess


@dataclass(slots=True)
class BootstrapEnvironmentResult:
    ok: bool
    reason: str
    command: list[str]
    stdout: str = ""
    stderr: str = ""


def sync_selected_environment(*, workspace: Path, extras: list[str], which=shutil.which, runner=subprocess.run) -> BootstrapEnvironmentResult:
    command = build_uv_sync_command(workspace=workspace, extras=extras)
    if not uv_available(which):
        return BootstrapEnvironmentResult(ok=False, reason="missing_uv", command=command)
    completed = runner(command, cwd=workspace, capture_output=True, text=True, check=False)
    return BootstrapEnvironmentResult(
        ok=completed.returncode == 0,
        reason="ok" if completed.returncode == 0 else "sync_failed",
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/b2t/bootstrap.py src/b2t/i18n.py tests/test_bootstrap_env.py
git commit -m "feat: let bootstrap drive uv sync"
```

### Task 4: Add Feature Selection and Confirmation UI

**Files:**
- Modify: `src/b2t/bootstrap.py`
- Modify: `src/b2t/i18n.py`

- [ ] **Step 1: Write the failing test**

Use a new unit test around the pure helper:

```python
def test_collect_required_extras_excludes_window_extra() -> None:
    assert collect_required_extras(
        providers=["sensevoice"],
        features=["window", "server"],
    ) == ["sensevoice", "server"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py::test_collect_required_extras_excludes_window_extra -q`
Expected: FAIL until feature handling is finalized.

- [ ] **Step 3: Write minimal implementation**

Add Bootstrap prompts for features and a summary panel:

```python
feature_choices = [
    {"name": "web       — ...", "value": "web", "enabled": "web" in config.enabled_features},
    {"name": "server    — ...", "value": "server", "enabled": "server" in config.enabled_features},
    {"name": "window    — ...", "value": "window", "enabled": "window" in config.enabled_features},
]
config.enabled_features = inquirer.checkbox(...).execute()
extras = collect_required_extras(providers=config.enabled_providers, features=config.enabled_features)
command = build_uv_sync_command(workspace=settings.workspace_root.parent, extras=extras)
```

Then show the command and confirm before running.

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python -m pytest tests/test_bootstrap_env.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/b2t/bootstrap.py src/b2t/i18n.py tests/test_bootstrap_env.py
git commit -m "feat: add bootstrap feature selection and sync confirmation"
```

### Task 5: Update Docs and Verify

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/DEVELOPMENT.md`
- Modify: `docs/DEVELOPMENT.en.md`

- [ ] **Step 1: Write the failing test**

Use an assertion-oriented doc check only if useful; otherwise rely on command verification and explicit doc review.

- [ ] **Step 2: Run verification before doc edits**

Run: `.\.venv\Scripts\python -m pytest -q`
Expected: PASS before doc-only changes.

- [ ] **Step 3: Write minimal documentation updates**

Document:

- Bootstrap now manages environment sync
- `uv` is required
- one `uv sync --extra ...` command should include all required extras
- resync / repair workflow

- [ ] **Step 4: Run full verification**

Run: `.\.venv\Scripts\python -m pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md docs/DEVELOPMENT.md docs/DEVELOPMENT.en.md
git commit -m "docs: explain bootstrap-managed uv environments"
```
