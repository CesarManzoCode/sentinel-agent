from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import ApprovalStatus
from sentinel.infrastructure.persistence.repositories.approval_repository import SQLiteApprovalRepository


@dataclass(slots=True)
class ApprovalStoreAdapter:
    repository: SQLiteApprovalRepository

    def get(self, token: str):
        return self.repository.get_by_token(token)

    def approve(self, token: str):
        return self.repository.update_status(token, ApprovalStatus.APPROVED)

    def deny(self, token: str):
        return self.repository.update_status(token, ApprovalStatus.DENIED)
