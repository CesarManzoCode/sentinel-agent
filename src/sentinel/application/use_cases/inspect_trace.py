from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.audit.trace_service import TraceService
from sentinel.domain.audit.entities import Trace


@dataclass(slots=True)
class InspectTrace:
    traces: TraceService

    def last(self) -> Trace | None:
        return self.traces.get_last()
