from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.audit.trace_service import TraceService


@dataclass(slots=True)
class TraceRecorder:
    service: TraceService

    def record(self, trace_id: str, event_name: str, payload: dict[str, object]) -> None:
        self.service.append(trace_id, event_name, payload)
