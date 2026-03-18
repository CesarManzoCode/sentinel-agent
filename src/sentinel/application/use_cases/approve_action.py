from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.safety.approval_service import ApprovalService
from sentinel.domain.safety.entities import ApprovalRecord


@dataclass(slots=True)
class ApproveAction:
    approvals: ApprovalService

    def approve(self, token: str) -> ApprovalRecord | None:
        return self.approvals.approve(token)

    def deny(self, token: str) -> ApprovalRecord | None:
        return self.approvals.deny(token)
