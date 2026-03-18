from __future__ import annotations

from dataclasses import dataclass, field

from sentinel.domain.common.ids import InvocationId


@dataclass(slots=True, frozen=True)
class ExecutionBudget:
    max_steps: int
    max_tool_calls: int
    max_tokens: int
    wall_clock_seconds: int


@dataclass(slots=True, frozen=True)
class PlanRevision:
    reason: str
    next_revision: int


@dataclass(slots=True, frozen=True)
class ActionDirective:
    action: str
    response: str | None = None
    plan_goal: str | None = None
    plan_steps: tuple[dict[str, object], ...] = ()
    tool_name: str | None = None
    tool_args: dict[str, object] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass(slots=True, frozen=True)
class CompletionSignal:
    done: bool
    reason: str
    invocation_id: InvocationId | None = None
