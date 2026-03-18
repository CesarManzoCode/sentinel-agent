from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.memory.entities import RetrievalBundle, RetrievalItem
from sentinel.domain.memory.ports import RetrieverPort


@dataclass(slots=True)
class FusionRetriever(RetrieverPort):
    lexical: RetrieverPort
    semantic: RetrieverPort
    rrk_constant: int = 60

    def retrieve(self, query: str, limit: int) -> RetrievalBundle:
        lexical_bundle = self.lexical.retrieve(query, limit)
        semantic_bundle = self.semantic.retrieve(query, limit)
        merged: dict[str, RetrievalItem] = {}

        for rank, item in enumerate(lexical_bundle.items, start=1):
            key = item.memory.memory_id.value
            existing = merged.setdefault(key, item)
            existing.fused_score += 1.0 / (self.rrk_constant + rank)
            existing.lexical_score = item.lexical_score
            existing.memory.salience = max(existing.memory.salience, item.memory.salience)

        for rank, item in enumerate(semantic_bundle.items, start=1):
            key = item.memory.memory_id.value
            existing = merged.get(key)
            contribution = 1.0 / (self.rrk_constant + rank)
            if existing is None:
                item.fused_score += contribution
                merged[key] = item
            else:
                existing.semantic_score = item.semantic_score
                existing.fused_score += contribution

        items = sorted(
            merged.values(),
            key=lambda item: (item.fused_score * 0.7) + (item.memory.salience * 0.3),
            reverse=True,
        )[:limit]
        return RetrievalBundle(query=query, items=items)
