from datetime import datetime, timedelta, timezone

from sentinel.domain.common.enums import ApprovalStatus, RiskLevel
from sentinel.domain.safety.entities import ApprovalRecord, RiskAssessment
from sentinel.domain.safety.services import SafetyPolicyService


def test_safety_policy_requires_approval_for_medium_and_high() -> None:
    service = SafetyPolicyService()
    medium = RiskAssessment(tool_name="filesystem.writer", baseline=RiskLevel.MEDIUM, effective=RiskLevel.MEDIUM)
    high = RiskAssessment(tool_name="packages.pacman", baseline=RiskLevel.HIGH, effective=RiskLevel.HIGH)
    low = RiskAssessment(tool_name="filesystem.reader", baseline=RiskLevel.LOW, effective=RiskLevel.LOW)

    assert service.requires_approval(low) is False
    assert service.requires_approval(medium) is True
    assert service.requires_approval(high) is True


def test_safety_policy_validates_approval_hash_and_expiry() -> None:
    now = datetime.now(timezone.utc)
    service = SafetyPolicyService()
    approval = ApprovalRecord(
        token="appr_1",
        session_id="sess_1",
        tool_name="filesystem.writer",
        parameter_hash="abc",
        created_at=now,
        expires_at=now + timedelta(minutes=5),
        status=ApprovalStatus.APPROVED,
        scope_signature="abc",
    )

    assert service.approval_valid(approval, "abc", now) is True
    assert service.approval_valid(approval, "different", now) is False
    assert service.approval_valid(approval, "abc", now + timedelta(minutes=10)) is False
