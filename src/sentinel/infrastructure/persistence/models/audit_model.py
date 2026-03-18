from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TraceModel:
    trace_id: str
    session_id: str
    started_at: str
    status: str


@dataclass(slots=True)
class AuditEventModel:
    trace_id: str
    event_name: str
    payload_json: str
    timestamp: str
