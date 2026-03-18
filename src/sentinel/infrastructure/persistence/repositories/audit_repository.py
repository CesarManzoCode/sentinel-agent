from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.domain.audit.entities import Trace, TraceEvent
from sentinel.domain.audit.ports import TraceRepositoryPort
from sentinel.domain.common.ids import SessionId, TraceId
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class SQLiteAuditRepository(TraceRepositoryPort):
    db: DatabaseManager

    def save_trace(self, trace: Trace) -> None:
        with self.db.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO traces (trace_id, session_id, started_at, status) VALUES (?, ?, ?, ?)",
                (trace.trace_id.value, trace.session_id.value, trace.started_at.isoformat(), trace.status),
            )

    def append_event(self, trace_id: str, event_name: str, payload: dict[str, object]) -> None:
        with self.db.connection() as conn:
            conn.execute(
                "INSERT INTO trace_events (trace_id, event_name, payload_json, timestamp) VALUES (?, ?, ?, ?)",
                (
                    trace_id,
                    event_name,
                    json.dumps(payload, ensure_ascii=False, default=str),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_trace(self, trace_id: str) -> Trace | None:
        with self.db.connection() as conn:
            trace_row = conn.execute("SELECT * FROM traces WHERE trace_id = ?", (trace_id,)).fetchone()
            if trace_row is None:
                return None
            event_rows = conn.execute(
                "SELECT event_name, payload_json, timestamp FROM trace_events WHERE trace_id = ? ORDER BY id ASC",
                (trace_id,),
            ).fetchall()
        trace = Trace(
            trace_id=TraceId(trace_row["trace_id"]),
            session_id=SessionId(trace_row["session_id"]),
            started_at=datetime.fromisoformat(trace_row["started_at"]),
            status=trace_row["status"],
            events=[
                TraceEvent(
                    event_name=row["event_name"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    payload=json.loads(row["payload_json"]),
                )
                for row in event_rows
            ],
        )
        return trace

    def get_last_trace(self) -> Trace | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT trace_id FROM traces ORDER BY started_at DESC LIMIT 1").fetchone()
        return self.get_trace(row["trace_id"]) if row is not None else None
