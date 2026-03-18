from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemorySnapshot
from sentinel.domain.memory.ports import SummarizerPort
from sentinel.shared.utils import compact_text


@dataclass(slots=True)
class EpisodicMemorySummarizer(SummarizerPort):
    async def summarize(self, text: str) -> str:
        return compact_text(text, 500)

    async def summarize_many(self, items: Sequence[str]) -> MemorySnapshot:
        joined = " ".join(items)
        return MemorySnapshot(
            summary=compact_text(joined, 900),
            covered_memory_ids=[],
            created_at=datetime.now(timezone.utc),
        )
