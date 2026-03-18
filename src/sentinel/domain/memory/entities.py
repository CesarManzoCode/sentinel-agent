from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId


@dataclass(slots=True)
class MemoryEntry:
    memory_id: MemoryId
    memory_type: MemoryType
    text: str
    created_at: datetime
    updated_at: datetime
    salience: float = 0.5
    scope: str = "global"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class MemorySnapshot:
    summary: str
    covered_memory_ids: list[str]
    created_at: datetime


@dataclass(slots=True)
class RetrievalItem:
    memory: MemoryEntry
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    fused_score: float = 0.0


@dataclass(slots=True)
class RetrievalBundle:
    query: str
    items: list[RetrievalItem] = field(default_factory=list)

    def top_texts(self, limit: int) -> list[str]:
        return [item.memory.text for item in sorted(self.items, key=lambda item: item.fused_score, reverse=True)[:limit]]
