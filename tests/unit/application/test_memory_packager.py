from datetime import datetime, timezone

from sentinel.application.memory.memory_packager import MemoryPackager
from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry, RetrievalBundle, RetrievalItem


def test_memory_packager_selects_top_k() -> None:
    now = datetime.now(timezone.utc)
    bundle = RetrievalBundle(
        query="python error",
        items=[
            RetrievalItem(
                memory=MemoryEntry(
                    memory_id=MemoryId.new(),
                    memory_type=MemoryType.EPISODIC,
                    text=f"memory {index}",
                    created_at=now,
                    updated_at=now,
                    salience=0.5,
                ),
                fused_score=score,
            )
            for index, score in enumerate([0.1, 0.9, 0.6], start=1)
        ],
    )
    packaged = MemoryPackager(max_items=2).package(bundle)

    assert packaged == ["memory 2", "memory 3"]
