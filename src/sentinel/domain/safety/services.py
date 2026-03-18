from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sentinel.domain.common.enums import ApprovalStatus, RiskLevel
from sentinel.domain.safety.entities import ApprovalRecord, PolicyDecision, RiskAssessment


@dataclass(slots=True)
class SafetyPolicyService:
    def requires_approval(self, assessment: RiskAssessment) -> bool:
        return assessment.effective in {RiskLevel.MEDIUM, RiskLevel.HIGH}

    def build_decision(self, assessment: RiskAssessment, allowed: bool, reason: str) -> PolicyDecision:
        return PolicyDecision(
            allowed=allowed,
            risk_level=assessment.effective,
            requires_approval=self.requires_approval(assessment),
            reason=reason,
        )

    def approval_valid(self, approval: ApprovalRecord | None, parameter_hash: str, now: datetime) -> bool:
        if approval is None:
            return False
        if approval.status != ApprovalStatus.APPROVED:
            return False
        if approval.parameter_hash != parameter_hash:
            return False
        return approval.expires_at >= now
