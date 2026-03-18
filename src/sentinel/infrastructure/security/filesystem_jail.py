from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy


@dataclass(slots=True)
class FilesystemJail:
    policy: PathPolicy

    def allow_read(self, path: str) -> Path:
        return self.policy.assert_read_allowed(path)

    def allow_write(self, path: str) -> Path:
        return self.policy.assert_write_allowed(path)
