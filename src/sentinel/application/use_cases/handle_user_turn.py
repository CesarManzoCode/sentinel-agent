from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.agent_runtime.dto import HandleTurnRequest, HandleTurnResponse
from sentinel.application.agent_runtime.orchestrator import AgentOrchestrator


@dataclass(slots=True)
class HandleUserTurn:
    orchestrator: AgentOrchestrator

    async def execute(self, request: HandleTurnRequest) -> HandleTurnResponse:
        return await self.orchestrator.handle_turn(request)
