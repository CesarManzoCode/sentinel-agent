from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sentinel.domain.memory.entities import MemoryEntry


@dataclass(slots=True)
class MemoryPolicyService:
    stale_after_days: int = 180

    def merge_or_keep(self, existing: MemoryEntry | None, candidate: MemoryEntry) -> MemoryEntry:
        if existing is None:
            return candidate
        if existing.text.strip().lower() == candidate.text.strip().lower():
            existing.updated_at = candidate.updated_at
            existing.salience = min(1.0, max(existing.salience, candidate.salience) + 0.1)
            existing.tags = sorted(set(existing.tags).union(candidate.tags))
            existing.metadata.update(candidate.metadata)
            return existing
        return candidate

    def should_prune(self, memory: MemoryEntry, now: datetime) -> bool:
        if memory.salience >= 0.4:
            return False
        return now - memory.updated_at > timedelta(days=self.stale_after_days)

    def update_salience(self, memory: MemoryEntry, relevant: bool) -> MemoryEntry:
        delta = 0.1 if relevant else -0.05
        memory.salience = max(0.0, min(1.0, memory.salience + delta))
        return memory
