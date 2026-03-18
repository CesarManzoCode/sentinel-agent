from __future__ import annotations

from dataclasses import dataclass, field

from sentinel.domain.common.enums import ApprovalStatus


@dataclass(slots=True)
class ApprovalPrompt:
    token: str
    tool_name: str
    risk: str
    preview: str
    status: ApprovalStatus = ApprovalStatus.PENDING


@dataclass(slots=True)
class HandleTurnRequest:
    session_id: str | None
    user_message: str
    streaming: bool = True
    debug: bool = False


@dataclass(slots=True)
class HandleTurnResponse:
    session_id: str
    trace_id: str
    message: str
    approvals: list[ApprovalPrompt] = field(default_factory=list)
    debug_events: list[str] = field(default_factory=list)
    tool_events: list[str] = field(default_factory=list)
