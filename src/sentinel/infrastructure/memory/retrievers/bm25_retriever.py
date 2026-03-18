from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.memory.entities import RetrievalBundle, RetrievalItem
from sentinel.domain.memory.ports import MemoryRepositoryPort, RetrieverPort


@dataclass(slots=True)
class BM25Retriever(RetrieverPort):
    repository: MemoryRepositoryPort

    def retrieve(self, query: str, limit: int) -> RetrievalBundle:
        entries = self.repository.search_lexical(query, limit)
        items = [
            RetrievalItem(memory=entry, lexical_score=1.0 / index, semantic_score=0.0, fused_score=1.0 / index)
            for index, entry in enumerate(entries, start=1)
        ]
        return RetrievalBundle(query=query, items=items)
