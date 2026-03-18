from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.memory.ports import EmbeddingPort, MemoryRepositoryPort


@dataclass(slots=True)
class MemoryIndexingService:
    repository: MemoryRepositoryPort
    embeddings: EmbeddingPort

    def index(self, memory: MemoryEntry) -> list[float]:
        vector = self.embeddings.embed(memory.text)
        self.repository.save(memory)
        return vector
