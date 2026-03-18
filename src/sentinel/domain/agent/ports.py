from __future__ import annotations

from typing import Protocol

from sentinel.domain.agent.entities import AgentSession
from sentinel.domain.agent.value_objects import ActionDirective
from sentinel.domain.audit.entities import Trace
from sentinel.domain.common.ids import SessionId
from sentinel.domain.memory.entities import MemoryEntry, RetrievalBundle
from sentinel.domain.tools.entities import ToolInvocation, ToolResult


class AgentRepositoryPort(Protocol):
    def get(self, session_id: SessionId) -> AgentSession | None: ...
    def save(self, session: AgentSession) -> None: ...


class PlannerPort(Protocol):
    async def plan(self, prompt: str, schema: dict[str, object]) -> ActionDirective: ...


class ToolExecutionPort(Protocol):
    async def execute(self, invocation: ToolInvocation) -> ToolResult: ...


class MemoryPort(Protocol):
    async def retrieve(self, query: str, top_k: int) -> RetrievalBundle: ...
    async def save(self, memory: MemoryEntry) -> None: ...


class AuditStoragePort(Protocol):
    def start_trace(self, trace: Trace) -> None: ...
    def append_event(self, trace_id: str, event_name: str, payload: dict[str, object]) -> None: ...
    def finalize_trace(self, trace_id: str, status: str) -> None: ...
