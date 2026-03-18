from __future__ import annotations

from typing import Protocol

from sentinel.domain.common.enums import ApprovalStatus
from sentinel.domain.safety.entities import ApprovalRecord


class ApprovalRepositoryPort(Protocol):
    def save(self, approval: ApprovalRecord) -> None: ...
    def get_latest(self, session_id: str, tool_name: str, parameter_hash: str) -> ApprovalRecord | None: ...
    def get_by_token(self, token: str) -> ApprovalRecord | None: ...
    def update_status(self, token: str, status: ApprovalStatus) -> ApprovalRecord | None: ...


class AuditPort(Protocol):
    def record(self, event_name: str, payload: dict[str, object]) -> None: ...


class SecretDetectionPort(Protocol):
    def find_secrets(self, text: str) -> list[str]: ...


class CommandValidationPort(Protocol):
    def validate(self, executable: str, argv: list[str]) -> list[str]: ...
