from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.safety.approval_service import ApprovalService
from sentinel.application.safety.command_guard import CommandGuard
from sentinel.application.safety.risk_evaluator import RiskEvaluator
from sentinel.domain.common.enums import RiskLevel
from sentinel.domain.common.errors import ApprovalRequired
from sentinel.domain.safety.entities import IntentScope, PolicyDecision
from sentinel.domain.safety.services import SafetyPolicyService
from sentinel.domain.tools.entities import ToolInvocation, ToolSpec
from sentinel.shared.utils import stable_hash


@dataclass(slots=True)
class PolicyEngine:
    risk_evaluator: RiskEvaluator
    safety_service: SafetyPolicyService
    approval_service: ApprovalService
    command_guard: CommandGuard
    auto_approve_low_risk: bool = True
    auto_approve_medium_risk: bool = False

    def evaluate(self, session_id: str, scope: IntentScope, spec: ToolSpec, invocation: ToolInvocation) -> PolicyDecision:
        assessment = self.risk_evaluator.assess(spec, invocation, scope)
        if assessment.effective == RiskLevel.DENY:
            return self.safety_service.build_decision(assessment, allowed=False, reason="tool or target is outside scope")
        if spec.name == "terminal.exec":
            executable = str(invocation.arguments.get("executable", ""))
            argv = [str(item) for item in invocation.arguments.get("argv", [])]  # type: ignore[arg-type]
            self.command_guard.guard(executable, argv)
        decision = self.safety_service.build_decision(assessment, allowed=True, reason="policy permits invocation")
        if assessment.effective == RiskLevel.LOW and self.auto_approve_low_risk:
            return decision
        if assessment.effective == RiskLevel.MEDIUM and self.auto_approve_medium_risk:
            return decision
        if decision.requires_approval:
            if self.approval_service.is_preapproved(session_id, spec.name, invocation.arguments):
                return decision
            preview = self.approval_service.decision_to_preview(decision, invocation.arguments)
            pending = self.approval_service.create_pending(session_id, spec.name, invocation.arguments, preview)
            raise ApprovalRequired(pending.token)
        return decision

    @staticmethod
    def approval_signature(tool_name: str, arguments: dict[str, object]) -> str:
        return stable_hash({"tool_name": tool_name, "arguments": arguments})
