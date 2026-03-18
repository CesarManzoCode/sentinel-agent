from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sentinel.domain.agent.entities import AgentSession, ChatMessage
from sentinel.domain.agent.ports import AgentRepositoryPort
from sentinel.domain.common.ids import SessionId
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class SQLiteSessionRepository(AgentRepositoryPort):
    db: DatabaseManager

    def get(self, session_id: SessionId) -> AgentSession | None:
        with self.db.connection() as conn:
            session_row = conn.execute(
                "SELECT session_id, title, summary, created_at, updated_at FROM sessions WHERE session_id = ?",
                (session_id.value,),
            ).fetchone()
            if session_row is None:
                return None
            messages = conn.execute(
                "SELECT role, content, created_at FROM session_messages WHERE session_id = ? ORDER BY id ASC",
                (session_id.value,),
            ).fetchall()
        session = AgentSession(
            session_id=SessionId(session_row["session_id"]),
            title=session_row["title"],
            summary=session_row["summary"],
            created_at=datetime.fromisoformat(session_row["created_at"]),
            updated_at=datetime.fromisoformat(session_row["updated_at"]),
            messages=[
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in messages
            ],
        )
        return session

    def save(self, session: AgentSession) -> None:
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, title, summary, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    title = excluded.title,
                    summary = excluded.summary,
                    updated_at = excluded.updated_at
                """,
                (
                    session.session_id.value,
                    session.title,
                    session.summary,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                ),
            )
            conn.execute("DELETE FROM session_messages WHERE session_id = ?", (session.session_id.value,))
            conn.executemany(
                "INSERT INTO session_messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                [
                    (
                        session.session_id.value,
                        message.role,
                        message.content,
                        message.created_at.isoformat(),
                    )
                    for message in session.messages
                ],
            )
