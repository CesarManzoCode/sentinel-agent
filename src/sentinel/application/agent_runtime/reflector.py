from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.agent.value_objects import CompletionSignal
from sentinel.domain.tools.entities import ToolResult


@dataclass(slots=True)
class ReflectionService:
    def reflect(self, result: ToolResult) -> CompletionSignal:
        if result.success:
            return CompletionSignal(done=False, reason="tool_succeeded", invocation_id=result.invocation_id)
        return CompletionSignal(done=False, reason="tool_failed", invocation_id=result.invocation_id)
