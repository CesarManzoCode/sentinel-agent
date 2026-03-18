from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sentinel.domain.common.enums import TurnState
from sentinel.domain.common.ids import InvocationId, SessionId, TraceId


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str
    created_at: datetime


@dataclass(slots=True)
class PlanStep:
    step_id: str
    title: str
    description: str
    status: str = "pending"
    tool_name: str | None = None
    tool_args: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class Plan:
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    revision: int = 1

    def active_step(self) -> PlanStep | None:
        for step in self.steps:
            if step.status == "pending":
                return step
        return None

    def mark_step(self, step_id: str, status: str) -> None:
        for step in self.steps:
            if step.step_id == step_id:
                step.status = status
                break


@dataclass(slots=True)
class ToolObservation:
    invocation_id: InvocationId
    tool_name: str
    output_summary: str
    success: bool
    created_at: datetime


@dataclass(slots=True)
class TurnRecord:
    trace_id: TraceId
    user_message: str
    assistant_message: str = ""
    state: TurnState = TurnState.IDLE
    tool_observations: list[ToolObservation] = field(default_factory=list)
    plan: Plan | None = None


@dataclass(slots=True)
class AgentSession:
    session_id: SessionId
    title: str
    created_at: datetime
    updated_at: datetime
    summary: str = ""
    messages: list[ChatMessage] = field(default_factory=list)
    turns: list[TurnRecord] = field(default_factory=list)

    def append_message(self, message: ChatMessage) -> None:
        self.messages.append(message)
        self.updated_at = message.created_at

    def append_turn(self, turn: TurnRecord) -> None:
        self.turns.append(turn)
        self.updated_at = datetime.now(timezone.utc)
