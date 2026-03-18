from datetime import datetime, timezone
from pathlib import Path

from sentinel.domain.agent.entities import AgentSession, ChatMessage
from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId, SessionId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.infrastructure.persistence.db import DatabaseManager
from sentinel.infrastructure.persistence.repositories.memory_repository import SQLiteMemoryRepository
from sentinel.infrastructure.persistence.repositories.session_repository import SQLiteSessionRepository


def test_sqlite_repositories_roundtrip_contract(tmp_path: Path) -> None:
    db = DatabaseManager(tmp_path / "sentinel.db")
    db.initialize()

    session_repo = SQLiteSessionRepository(db)
    memory_repo = SQLiteMemoryRepository(db)
    now = datetime.now(timezone.utc)

    session = AgentSession(
        session_id=SessionId.new(),
        title="contract session",
        created_at=now,
        updated_at=now,
        messages=[ChatMessage(role="user", content="hello", created_at=now)],
    )
    session_repo.save(session)
    loaded_session = session_repo.get(session.session_id)
    assert loaded_session is not None
    assert loaded_session.messages[0].content == "hello"

    memory = MemoryEntry(
        memory_id=MemoryId.new(),
        memory_type=MemoryType.EPISODIC,
        text="contract memory",
        created_at=now,
        updated_at=now,
        salience=0.5,
    )
    memory_repo.save(memory)
    loaded_memory = memory_repo.get(memory.memory_id)
    assert loaded_memory is not None
    assert loaded_memory.text == "contract memory"
