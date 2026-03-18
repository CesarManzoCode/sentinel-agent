from datetime import datetime, timedelta, timezone

from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.memory.services import MemoryPolicyService


def _memory(text: str, salience: float = 0.5) -> MemoryEntry:
    now = datetime.now(timezone.utc)
    return MemoryEntry(
        memory_id=MemoryId.new(),
        memory_type=MemoryType.EPISODIC,
        text=text,
        created_at=now,
        updated_at=now,
        salience=salience,
    )


def test_memory_policy_merges_duplicates_and_updates_salience() -> None:
    service = MemoryPolicyService()
    existing = _memory("Repeated command fixed the issue", salience=0.5)
    candidate = _memory("Repeated command fixed the issue", salience=0.8)

    merged = service.merge_or_keep(existing, candidate)

    assert merged is existing
    assert merged.salience > 0.5


def test_memory_policy_prunes_low_salience_stale_memory() -> None:
    service = MemoryPolicyService(stale_after_days=30)
    memory = _memory("temporary note", salience=0.1)
    memory.updated_at = datetime.now(timezone.utc) - timedelta(days=31)

    assert service.should_prune(memory, datetime.now(timezone.utc)) is True
