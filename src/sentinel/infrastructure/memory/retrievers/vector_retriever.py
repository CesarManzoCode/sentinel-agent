from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import RetrievalBundle, RetrievalItem
from sentinel.domain.memory.ports import EmbeddingPort, MemoryRepositoryPort, RetrieverPort
from sentinel.infrastructure.persistence.vector.hnsw_index import HNSWIndexStore


@dataclass(slots=True)
class VectorRetriever(RetrieverPort):
    repository: MemoryRepositoryPort
    embeddings: EmbeddingPort
    index: HNSWIndexStore

    def retrieve(self, query: str, limit: int) -> RetrievalBundle:
        vector = self.embeddings.embed(query)
        candidates = self.index.query(vector, limit)
        items: list[RetrievalItem] = []
        for memory_id, score in candidates:
            memory = self.repository.get(MemoryId(memory_id))
            if memory is None:
                continue
            items.append(RetrievalItem(memory=memory, lexical_score=0.0, semantic_score=score, fused_score=score))
        return RetrievalBundle(query=query, items=items)
