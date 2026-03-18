from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.common.ids import InvocationId, SessionId


@dataclass(slots=True)
class ToolCapability:
    verbs: tuple[str, ...]
    resources: tuple[str, ...]


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    category: ToolCategory
    schema: dict[str, object]
    baseline_risk: RiskLevel
    timeout_seconds: int
    concurrency_safe: bool
    side_effects: tuple[str, ...]
    enabled: bool = True
    hidden: bool = False


@dataclass(slots=True)
class ToolInvocation:
    invocation_id: InvocationId
    session_id: SessionId
    tool_name: str
    arguments: dict[str, object]
    requested_at: datetime
    trace_id: str | None = None


@dataclass(slots=True)
class ToolResult:
    invocation_id: InvocationId
    tool_name: str
    success: bool
    stdout: str = ""
    stderr: str = ""
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    duration_ms: int = 0

    def summary(self) -> str:
        if self.success and self.stdout:
            return self.stdout[:240]
        if self.stderr:
            return self.stderr[:240]
        return "tool completed without textual output"
