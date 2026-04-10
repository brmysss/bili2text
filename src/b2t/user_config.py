from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from b2t.config import Settings


@dataclass(slots=True)
class SenseVoiceConfig:
    model_dir: str = ""
    language: str = "auto"
    use_itn: bool = True


@dataclass(slots=True)
class VolcengineConfig:
    api_key: str = ""
    app_key: str = ""
    access_key: str = ""
    resource_id: str = "volc.bigasr.auc_turbo"
    model_name: str = "bigmodel"
    use_itn: bool = True


@dataclass(slots=True)
class AppConfig:
    default_provider: str = "whisper"
    default_model: str = "small"
    sensevoice: SenseVoiceConfig = field(default_factory=SenseVoiceConfig)
    volcengine: VolcengineConfig = field(default_factory=VolcengineConfig)

    @classmethod
    def load(cls, settings: Settings) -> "AppConfig":
        if not settings.config_path.exists():
            return cls()

        data = json.loads(settings.config_path.read_text(encoding="utf-8"))
        return cls(
            default_provider=data.get("default_provider", "whisper"),
            default_model=data.get("default_model", "small"),
            sensevoice=SenseVoiceConfig(**data.get("sensevoice", {})),
            volcengine=VolcengineConfig(**data.get("volcengine", {})),
        )

    def save(self, settings: Settings) -> None:
        settings.ensure_directories()
        settings.config_path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
