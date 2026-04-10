from pathlib import Path

from b2t.bootstrap import (
    build_uv_sync_command,
    collect_required_extras,
    sync_environment_for_config,
    sync_selected_environment,
    uv_available,
)
from b2t.user_config import AppConfig


def test_collect_required_extras_combines_providers_and_features() -> None:
    assert collect_required_extras(
        providers=["whisper", "volcengine"],
        features=["web", "window"],
    ) == ["whisper", "volcengine", "web"]


def test_collect_required_extras_excludes_window_extra() -> None:
    assert collect_required_extras(
        providers=["sensevoice"],
        features=["window", "server"],
    ) == ["sensevoice", "server"]


def test_build_uv_sync_command_is_stable() -> None:
    command = build_uv_sync_command(
        workspace=Path("D:/repo"),
        extras=["whisper", "web"],
    )
    assert command == ["uv", "sync", "--extra", "whisper", "--extra", "web"]


def test_uv_available_uses_path_lookup() -> None:
    assert uv_available(lambda _name: "C:/bin/uv.exe") is True
    assert uv_available(lambda _name: None) is False


def test_sync_selected_environment_reports_missing_uv(tmp_path: Path) -> None:
    result = sync_selected_environment(
        workspace=tmp_path,
        extras=["whisper", "web"],
        which=lambda _name: None,
        runner=None,
    )
    assert result.ok is False
    assert result.reason == "missing_uv"
    assert result.command == ["uv", "sync", "--extra", "whisper", "--extra", "web"]


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
    assert result.reason == "ok"
    assert calls == [["uv", "sync", "--extra", "whisper", "--extra", "web"]]


def test_sync_environment_for_config_uses_saved_provider_and_feature_selection(tmp_path: Path) -> None:
    config = AppConfig()
    config.enabled_providers = ["sensevoice", "volcengine"]
    config.enabled_features = ["window", "server"]

    calls: list[list[str]] = []

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_runner(command, **kwargs):
        calls.append(command)
        return Completed()

    result = sync_environment_for_config(
        project_root=tmp_path,
        config=config,
        which=lambda _name: "C:/bin/uv.exe",
        runner=fake_runner,
    )
    assert result.ok is True
    assert calls == [["uv", "sync", "--extra", "sensevoice", "--extra", "volcengine", "--extra", "server"]]
