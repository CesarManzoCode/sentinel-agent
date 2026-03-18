from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sentinel.domain.common.enums import ApprovalStatus, RiskLevel


@dataclass(slots=True)
class ApprovalRecord:
    token: str
    session_id: str
    tool_name: str
    parameter_hash: str
    created_at: datetime
    expires_at: datetime
    status: ApprovalStatus
    scope_signature: str
    reason: str = ""


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    risk_level: RiskLevel
    requires_approval: bool
    reason: str
    preview: str = ""


@dataclass(slots=True)
class RiskAssessment:
    tool_name: str
    baseline: RiskLevel
    effective: RiskLevel
    factors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class IntentScope:
    raw_request: str
    allowed_paths: set[str] = field(default_factory=set)
    allowed_verbs: set[str] = field(default_factory=set)
    allowed_tools: set[str] = field(default_factory=set)

    def describe(self) -> str:
        return (
            f"verbs={sorted(self.allowed_verbs)} "
            f"paths={sorted(self.allowed_paths)} "
            f"tools={sorted(self.allowed_tools)}"
        )
