from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sentinel.domain.common.ids import SessionId, TraceId


@dataclass(slots=True)
class TraceEvent:
    event_name: str
    timestamp: datetime
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class Trace:
    trace_id: TraceId
    session_id: SessionId
    started_at: datetime
    status: str = "started"
    events: list[TraceEvent] = field(default_factory=list)

    def append(self, event: TraceEvent) -> None:
        self.events.append(event)


@dataclass(slots=True)
class AuditEvent:
    event_name: str
    timestamp: datetime
    payload: dict[str, object]
