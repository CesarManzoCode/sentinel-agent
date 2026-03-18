from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import ApprovalStatus
from sentinel.domain.safety.entities import ApprovalRecord, PolicyDecision
from sentinel.domain.safety.ports import ApprovalRepositoryPort
from sentinel.shared.time import Clock
from sentinel.shared.utils import stable_hash


@dataclass(slots=True)
class ApprovalService:
    repository: ApprovalRepositoryPort
    clock: Clock
    ttl_seconds: int

    def parameter_hash(self, tool_name: str, arguments: dict[str, object]) -> str:
        return stable_hash({"tool": tool_name, "arguments": arguments})

    def is_preapproved(self, session_id: str, tool_name: str, arguments: dict[str, object]) -> bool:
        parameter_hash = self.parameter_hash(tool_name, arguments)
        approval = self.repository.get_latest(session_id=session_id, tool_name=tool_name, parameter_hash=parameter_hash)
        return bool(approval and approval.status == ApprovalStatus.APPROVED and approval.expires_at >= self.clock.now())

    def create_pending(self, session_id: str, tool_name: str, arguments: dict[str, object], preview: str) -> ApprovalRecord:
        token = f"appr_{stable_hash({'s': session_id, 't': tool_name, 'a': arguments, 'ts': self.clock.isoformat()})[:20]}"
        parameter_hash = self.parameter_hash(tool_name, arguments)
        approval = ApprovalRecord(
            token=token,
            session_id=session_id,
            tool_name=tool_name,
            parameter_hash=parameter_hash,
            created_at=self.clock.now(),
            expires_at=self.clock.ttl_from_now(self.ttl_seconds),
            status=ApprovalStatus.PENDING,
            scope_signature=parameter_hash,
            reason=preview,
        )
        self.repository.save(approval)
        return approval

    def approve(self, token: str) -> ApprovalRecord | None:
        return self.repository.update_status(token, ApprovalStatus.APPROVED)

    def deny(self, token: str) -> ApprovalRecord | None:
        return self.repository.update_status(token, ApprovalStatus.DENIED)

    def decision_to_preview(self, decision: PolicyDecision, arguments: dict[str, object]) -> str:
        return f"{decision.reason}\narguments={arguments}"
