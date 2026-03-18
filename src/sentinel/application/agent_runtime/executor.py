from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.application.tools.dispatcher import ToolDispatcher
from sentinel.domain.common.ids import InvocationId, SessionId
from sentinel.domain.safety.entities import IntentScope
from sentinel.domain.tools.entities import ToolInvocation, ToolResult


@dataclass(slots=True)
class ExecutionService:
    dispatcher: ToolDispatcher

    async def execute(
        self,
        session_id: SessionId,
        trace_id: str,
        scope: IntentScope,
        tool_name: str,
        tool_args: dict[str, object],
    ) -> ToolResult:
        invocation = ToolInvocation(
            invocation_id=InvocationId.new(),
            session_id=session_id,
            tool_name=tool_name,
            arguments=tool_args,
            requested_at=datetime.now(timezone.utc),
            trace_id=trace_id,
        )
        return await self.dispatcher.dispatch(session_id=str(session_id), scope=scope, invocation=invocation)
