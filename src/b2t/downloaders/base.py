from __future__ import annotations

from abc import ABC, abstractmethod

from b2t.config import Settings
from b2t.models import DownloadResult, SourceRef


class Downloader(ABC):
    name = "downloader"

    @abstractmethod
    def download(self, source: SourceRef, settings: Settings) -> DownloadResult:
        raise NotImplementedError
