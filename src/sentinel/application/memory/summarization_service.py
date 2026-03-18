from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sentinel.domain.memory.ports import SummarizerPort


@dataclass(slots=True)
class SummarizationService:
    summarizer: SummarizerPort

    async def summarize_text(self, text: str) -> str:
        return await self.summarizer.summarize(text)

    async def summarize_many(self, items: Sequence[str]) -> str:
        snapshot = await self.summarizer.summarize_many(items)
        return snapshot.summary
