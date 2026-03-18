from datetime import datetime, timezone

from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry, RetrievalBundle, RetrievalItem
from sentinel.infrastructure.memory.retrievers.fusion_retriever import FusionRetriever


class StaticRetriever:
    def __init__(self, bundle: RetrievalBundle) -> None:
        self.bundle = bundle

    def retrieve(self, query: str, limit: int) -> RetrievalBundle:
        return self.bundle


def _item(text: str, score: float) -> RetrievalItem:
    now = datetime.now(timezone.utc)
    return RetrievalItem(
        memory=MemoryEntry(
            memory_id=MemoryId.new(),
            memory_type=MemoryType.EPISODIC,
            text=text,
            created_at=now,
            updated_at=now,
            salience=0.5,
        ),
        fused_score=score,
        lexical_score=score,
        semantic_score=score,
    )


def test_fusion_retriever_combines_sources() -> None:
    lexical = StaticRetriever(RetrievalBundle(query="q", items=[_item("alpha", 0.9), _item("beta", 0.2)]))
    semantic = StaticRetriever(RetrievalBundle(query="q", items=[_item("beta", 0.9), _item("gamma", 0.3)]))

    fusion = FusionRetriever(lexical=lexical, semantic=semantic)
    result = fusion.retrieve("q", 3)

    texts = [item.memory.text for item in result.items]
    assert "alpha" in texts
    assert "beta" in texts
    assert len(texts) == 3
