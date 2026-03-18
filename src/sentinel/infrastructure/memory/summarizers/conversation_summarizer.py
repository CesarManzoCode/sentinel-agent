from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from sentinel.domain.memory.entities import MemorySnapshot
from sentinel.domain.memory.ports import SummarizerPort
from sentinel.shared.utils import compact_text


@dataclass(slots=True)
class ConversationSummarizer(SummarizerPort):
    async def summarize(self, text: str) -> str:
        return compact_text(text, 800)

    async def summarize_many(self, items: Sequence[str]) -> MemorySnapshot:
        return MemorySnapshot(
            summary=compact_text(" ".join(items), 1200),
            covered_memory_ids=[],
            created_at=datetime.now(timezone.utc),
        )
