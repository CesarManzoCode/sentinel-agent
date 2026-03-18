from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ExternalTurnRequest:
    session_id: str | None
    message: str
    debug: bool = False


@dataclass(slots=True)
class ExternalTurnResponse:
    session_id: str
    trace_id: str
    message: str
    metadata: dict[str, object] = field(default_factory=dict)
