from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.application.llm.conversation_compactor import ConversationCompactor
from sentinel.domain.agent.entities import AgentSession, ChatMessage
from sentinel.domain.agent.ports import AgentRepositoryPort
from sentinel.domain.common.ids import SessionId


@dataclass(slots=True)
class SessionManager:
    repository: AgentRepositoryPort
    compactor: ConversationCompactor

    def load_or_create(self, session_id: str | None, title_hint: str) -> AgentSession:
        if session_id:
            existing = self.repository.get(SessionId(session_id))
            if existing is not None:
                return existing
        now = datetime.now(timezone.utc)
        session = AgentSession(
            session_id=SessionId.new(),
            title=title_hint[:80] or "sentinel-session",
            created_at=now,
            updated_at=now,
        )
        self.repository.save(session)
        return session

    def append_user_message(self, session: AgentSession, content: str) -> None:
        session.append_message(ChatMessage(role="user", content=content, created_at=datetime.now(timezone.utc)))

    def append_assistant_message(self, session: AgentSession, content: str) -> None:
        session.append_message(ChatMessage(role="assistant", content=content, created_at=datetime.now(timezone.utc)))

    def compact(self, session: AgentSession) -> AgentSession:
        session.messages, session.summary = self.compactor.compact(session.messages, session.summary)
        self.repository.save(session)
        return session
