import pytest
from datetime import datetime, timezone

from sentinel.application.safety.approval_service import ApprovalService
from sentinel.application.safety.command_guard import CommandGuard
from sentinel.application.safety.policy_engine import PolicyEngine
from sentinel.application.safety.risk_evaluator import RiskEvaluator
from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.common.errors import ApprovalRequired
from sentinel.domain.common.ids import InvocationId, SessionId
from sentinel.domain.safety.entities import IntentScope
from sentinel.domain.safety.services import SafetyPolicyService
from sentinel.domain.tools.entities import ToolInvocation, ToolSpec
from sentinel.shared.time import Clock


class StubApprovalRepo:
    def __init__(self) -> None:
        self.records = {}

    def save(self, approval):  # type: ignore[no-untyped-def]
        self.records[approval.token] = approval

    def get_latest(self, session_id: str, tool_name: str, parameter_hash: str):  # type: ignore[no-untyped-def]
        return None

    def get_by_token(self, token: str):  # type: ignore[no-untyped-def]
        return self.records.get(token)

    def update_status(self, token: str, status):  # type: ignore[no-untyped-def]
        record = self.records.get(token)
        if record is None:
            return None
        record.status = status
        return record


class AllowAllValidator:
    def validate(self, executable: str, argv: list[str]) -> list[str]:
        return []


def test_policy_engine_approves_low_risk_read_only_action() -> None:
    approval_service = ApprovalService(StubApprovalRepo(), Clock(), ttl_seconds=60)
    engine = PolicyEngine(
        risk_evaluator=RiskEvaluator(),
        safety_service=SafetyPolicyService(),
        approval_service=approval_service,
        command_guard=CommandGuard(AllowAllValidator()),
    )
    spec = ToolSpec(
        name="filesystem.reader",
        description="read",
        category=ToolCategory.FILESYSTEM,
        schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        baseline_risk=RiskLevel.LOW,
        timeout_seconds=5,
        concurrency_safe=True,
        side_effects=("read",),
    )
    invocation = ToolInvocation(
        invocation_id=InvocationId.new(),
        session_id=SessionId.new(),
        tool_name=spec.name,
        arguments={"path": "/tmp/demo.txt"},
        requested_at=datetime.now(timezone.utc),
    )
    decision = engine.evaluate("sess_1", IntentScope(raw_request="read file"), spec, invocation)
    assert decision.allowed is True
    assert decision.requires_approval is False


def test_policy_engine_requests_approval_for_writer() -> None:
    approval_service = ApprovalService(StubApprovalRepo(), Clock(), ttl_seconds=60)
    engine = PolicyEngine(
        risk_evaluator=RiskEvaluator(),
        safety_service=SafetyPolicyService(),
        approval_service=approval_service,
        command_guard=CommandGuard(AllowAllValidator()),
    )
    spec = ToolSpec(
        name="filesystem.writer",
        description="write",
        category=ToolCategory.FILESYSTEM,
        schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
        baseline_risk=RiskLevel.MEDIUM,
        timeout_seconds=5,
        concurrency_safe=False,
        side_effects=("write",),
    )
    invocation = ToolInvocation(
        invocation_id=InvocationId.new(),
        session_id=SessionId.new(),
        tool_name=spec.name,
        arguments={"path": "/tmp/demo.txt", "content": "x"},
        requested_at=datetime.now(timezone.utc),
    )
    with pytest.raises(ApprovalRequired):
        engine.evaluate("sess_1", IntentScope(raw_request="edit file", allowed_paths={"/tmp/demo.txt"}, allowed_tools={spec.name}), spec, invocation)
