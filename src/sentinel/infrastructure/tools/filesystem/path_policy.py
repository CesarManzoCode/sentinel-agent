from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sentinel.domain.common.errors import PolicyViolation
from sentinel.shared.utils import is_subpath


@dataclass(slots=True)
class PathPolicy:
    allowed_roots: list[Path]
    denied_prefixes: tuple[str, ...] = ("/etc", "/usr", "/bin", "/sbin", "/boot", "/root", "/proc", "/sys")

    def normalize(self, value: str) -> Path:
        return Path(value).expanduser().resolve()

    def assert_read_allowed(self, value: str) -> Path:
        path = self.normalize(value)
        if any(str(path).startswith(prefix) for prefix in self.denied_prefixes):
            raise PolicyViolation(f"path is denied by policy: {path}")
        if self.allowed_roots and not any(is_subpath(path, root) or path == root for root in self.allowed_roots):
            raise PolicyViolation(f"path is outside allowed roots: {path}")
        return path

    def assert_write_allowed(self, value: str) -> Path:
        path = self.assert_read_allowed(value)
        if not self.allowed_roots:
            raise PolicyViolation("write policy requires at least one allowed root")
        return path
