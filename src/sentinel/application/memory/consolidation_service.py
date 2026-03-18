from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.application.memory.indexing_service import MemoryIndexingService
from sentinel.application.memory.summarization_service import SummarizationService
from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.memory.ports import MemoryRepositoryPort


@dataclass(slots=True)
class MemoryConsolidationService:
    repository: MemoryRepositoryPort
    summarization: SummarizationService
    indexing: MemoryIndexingService | None = None

    async def consolidate_session(self, session_id: str, transcript: list[str]) -> MemoryEntry | None:
        if not transcript:
            return None
        summary = await self.summarization.summarize_many(transcript)
        now = datetime.now(timezone.utc)
        memory = MemoryEntry(
            memory_id=MemoryId.new(),
            memory_type=MemoryType.EPISODIC,
            text=f"Session {session_id}: {summary}",
            created_at=now,
            updated_at=now,
            salience=0.6,
            tags=["session", "episodic"],
            metadata={"session_id": session_id},
        )
        self.repository.save(memory)
        if self.indexing is not None:
            self.indexing.index(memory)
        return memory
