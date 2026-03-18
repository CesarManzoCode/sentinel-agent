from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.memory.entities import RetrievalBundle
from sentinel.domain.memory.ports import RetrieverPort


@dataclass(slots=True)
class MemoryRetrievalService:
    retriever: RetrieverPort

    async def retrieve(self, query: str, top_k: int) -> RetrievalBundle:
        return self.retriever.retrieve(query, top_k)
