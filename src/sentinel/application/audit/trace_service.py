from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.domain.audit.entities import Trace, TraceEvent
from sentinel.domain.audit.ports import TraceRepositoryPort
from sentinel.domain.common.ids import SessionId, TraceId


@dataclass(slots=True)
class TraceService:
    repository: TraceRepositoryPort

    def start(self, session_id: SessionId) -> Trace:
        trace = Trace(trace_id=TraceId.new(), session_id=session_id, started_at=datetime.now(timezone.utc))
        self.repository.save_trace(trace)
        return trace

    def append(self, trace_id: str, event_name: str, payload: dict[str, object]) -> None:
        self.repository.append_event(trace_id, event_name, payload)

    def get_last(self) -> Trace | None:
        return self.repository.get_last_trace()
