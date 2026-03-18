from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(slots=True)
class Clock:
    """Clock abstraction for deterministic testing."""

    def now(self) -> datetime:
        return datetime.now(tz=UTC)

    def ttl_from_now(self, seconds: int) -> datetime:
        return self.now() + timedelta(seconds=seconds)

    def isoformat(self) -> str:
        return self.now().isoformat()
