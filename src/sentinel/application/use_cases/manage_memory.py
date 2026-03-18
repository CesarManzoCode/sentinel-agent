from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.memory.ports import MemoryRepositoryPort


@dataclass(slots=True)
class ManageMemory:
    repository: MemoryRepositoryPort

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        return self.repository.search_lexical(query, limit)

    def forget(self, memory_id: str) -> None:
        self.repository.delete(MemoryId(memory_id))

    def recent(self, limit: int = 10) -> list[MemoryEntry]:
        return self.repository.list_recent(limit)
