from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sentinel.domain.common.enums import ApprovalStatus
from sentinel.domain.safety.entities import ApprovalRecord
from sentinel.domain.safety.ports import ApprovalRepositoryPort
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class SQLiteApprovalRepository(ApprovalRepositoryPort):
    db: DatabaseManager

    def save(self, approval: ApprovalRecord) -> None:
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO approvals (
                    token, session_id, tool_name, parameter_hash, created_at,
                    expires_at, status, scope_signature, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval.token,
                    approval.session_id,
                    approval.tool_name,
                    approval.parameter_hash,
                    approval.created_at.isoformat(),
                    approval.expires_at.isoformat(),
                    approval.status.value,
                    approval.scope_signature,
                    approval.reason,
                ),
            )

    def get_latest(self, session_id: str, tool_name: str, parameter_hash: str) -> ApprovalRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM approvals
                WHERE session_id = ? AND tool_name = ? AND parameter_hash = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session_id, tool_name, parameter_hash),
            ).fetchone()
        return self._row(row) if row is not None else None

    def get_by_token(self, token: str) -> ApprovalRecord | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE token = ?", (token,)).fetchone()
        return self._row(row) if row is not None else None

    def update_status(self, token: str, status: ApprovalStatus) -> ApprovalRecord | None:
        with self.db.connection() as conn:
            conn.execute("UPDATE approvals SET status = ? WHERE token = ?", (status.value, token))
        return self.get_by_token(token)

    @staticmethod
    def _row(row: object) -> ApprovalRecord:
        import sqlite3
        assert isinstance(row, sqlite3.Row)
        return ApprovalRecord(
            token=row["token"],
            session_id=row["session_id"],
            tool_name=row["tool_name"],
            parameter_hash=row["parameter_hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            status=ApprovalStatus(row["status"]),
            scope_signature=row["scope_signature"],
            reason=row["reason"],
        )
