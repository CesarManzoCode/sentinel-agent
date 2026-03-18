from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.agent_runtime.dto import HandleTurnRequest, HandleTurnResponse
from sentinel.application.use_cases.approve_action import ApproveAction
from sentinel.application.use_cases.handle_user_turn import HandleUserTurn
from sentinel.application.use_cases.inspect_trace import InspectTrace
from sentinel.application.use_cases.list_tools import ListTools
from sentinel.application.use_cases.manage_memory import ManageMemory
from sentinel.domain.audit.entities import Trace
from sentinel.domain.safety.entities import ApprovalRecord
from sentinel.domain.tools.entities import ToolSpec
from sentinel.domain.memory.entities import MemoryEntry


@dataclass(slots=True)
class ChatController:
    handle_turn: HandleUserTurn

    async def submit(self, session_id: str | None, message: str, debug: bool) -> HandleTurnResponse:
        request = HandleTurnRequest(session_id=session_id, user_message=message, debug=debug, streaming=True)
        return await self.handle_turn.execute(request)


@dataclass(slots=True)
class ApprovalController:
    approve_action: ApproveAction

    def approve(self, token: str) -> ApprovalRecord | None:
        return self.approve_action.approve(token)

    def deny(self, token: str) -> ApprovalRecord | None:
        return self.approve_action.deny(token)


@dataclass(slots=True)
class TraceController:
    inspect_trace: InspectTrace

    def last(self) -> Trace | None:
        return self.inspect_trace.last()


@dataclass(slots=True)
class ToolController:
    list_tools: ListTools

    def list(self) -> list[ToolSpec]:
        return self.list_tools.execute()


@dataclass(slots=True)
class MemoryController:
    manage_memory: ManageMemory

    def search(self, query: str) -> list[MemoryEntry]:
        return self.manage_memory.search(query)

    def recent(self) -> list[MemoryEntry]:
        return self.manage_memory.recent()
