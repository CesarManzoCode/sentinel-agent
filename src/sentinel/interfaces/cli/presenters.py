from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.agent_runtime.dto import HandleTurnResponse
from sentinel.domain.audit.entities import Trace
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.safety.entities import ApprovalRecord
from sentinel.domain.tools.entities import ToolSpec


@dataclass(slots=True)
class ChatPresenter:
    def present(self, response: HandleTurnResponse) -> str:
        parts = [response.message]
        if response.tool_events:
            parts.append("\nTool events:")
            parts.extend(f"- {event}" for event in response.tool_events)
        if response.debug_events:
            parts.append("\nDebug:")
            parts.extend(f"- {event}" for event in response.debug_events)
        if response.approvals:
            parts.append("\nApprovals:")
            parts.extend(f"- {approval.token}: {approval.preview}" for approval in response.approvals)
        return "\n".join(parts)


@dataclass(slots=True)
class ApprovalPresenter:
    def present(self, approval: ApprovalRecord | None, action: str) -> str:
        if approval is None:
            return f"{action} failed: approval token not found"
        return f"{action} {approval.token}: {approval.status.value}"


@dataclass(slots=True)
class TracePresenter:
    def present(self, trace: Trace | None) -> str:
        if trace is None:
            return "No trace found."
        lines = [f"Trace {trace.trace_id.value} session={trace.session_id.value} status={trace.status}"]
        for event in trace.events[-25:]:
            lines.append(f"- {event.timestamp.isoformat()} {event.event_name} {event.payload}")
        return "\n".join(lines)


@dataclass(slots=True)
class ToolPresenter:
    def present(self, tools: list[ToolSpec]) -> str:
        lines = []
        for tool in tools:
            lines.append(
                f"{tool.name} [{tool.category.value}] risk={tool.baseline_risk.value} timeout={tool.timeout_seconds}s"
            )
            lines.append(f"  {tool.description}")
        return "\n".join(lines)


@dataclass(slots=True)
class MemoryPresenter:
    def present(self, entries: list[MemoryEntry]) -> str:
        if not entries:
            return "No memories found."
        return "\n".join(
            f"- {entry.memory_id.value} [{entry.memory_type.value}] salience={entry.salience:.2f} {entry.text}"
            for entry in entries
        )
