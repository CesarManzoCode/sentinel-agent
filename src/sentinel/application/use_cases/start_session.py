from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.agent_runtime.session_manager import SessionManager
from sentinel.domain.agent.entities import AgentSession


@dataclass(slots=True)
class StartSession:
    session_manager: SessionManager

    def execute(self, title_hint: str = "interactive-chat") -> AgentSession:
        return self.session_manager.load_or_create(None, title_hint)
