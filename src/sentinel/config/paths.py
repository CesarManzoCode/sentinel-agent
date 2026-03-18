from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sentinel.shared.constants import (
    DEFAULT_AUDIT_DIRNAME,
    DEFAULT_CACHE_DIRNAME,
    DEFAULT_DB_FILENAME,
    DEFAULT_LOG_DIRNAME,
    DEFAULT_RUNTIME_DIRNAME,
    DEFAULT_VECTOR_DIRNAME,
)
from sentinel.shared.utils import ensure_directory


@dataclass(slots=True, frozen=True)
class PathResolver:
    data_dir: Path

    @property
    def db_file(self) -> Path:
        return self.data_dir / DEFAULT_DB_FILENAME

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / DEFAULT_LOG_DIRNAME

    @property
    def audit_dir(self) -> Path:
        return self.data_dir / DEFAULT_AUDIT_DIRNAME

    @property
    def vector_dir(self) -> Path:
        return self.data_dir / DEFAULT_VECTOR_DIRNAME

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / DEFAULT_CACHE_DIRNAME

    @property
    def runtime_dir(self) -> Path:
        return self.data_dir / DEFAULT_RUNTIME_DIRNAME

    def ensure(self) -> None:
        ensure_directory(self.data_dir)
        ensure_directory(self.logs_dir)
        ensure_directory(self.audit_dir)
        ensure_directory(self.vector_dir)
        ensure_directory(self.cache_dir)
        ensure_directory(self.runtime_dir)
