from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel
from sentinel.domain.safety.entities import IntentScope, RiskAssessment
from sentinel.domain.tools.entities import ToolInvocation, ToolSpec


@dataclass(slots=True)
class RiskEvaluator:
    def assess(self, spec: ToolSpec, invocation: ToolInvocation, scope: IntentScope) -> RiskAssessment:
        factors = [f"baseline={spec.baseline_risk.value}"]
        effective = spec.baseline_risk
        if spec.name.endswith("writer"):
            effective = RiskLevel.HIGH if not scope.allowed_paths else RiskLevel.MEDIUM
            factors.append("filesystem_write")
        if spec.category.value == "packages":
            effective = RiskLevel.HIGH
            factors.append("package_operation")
        if spec.name == "terminal.exec":
            argv = invocation.arguments.get("argv", [])
            if isinstance(argv, list) and any(str(arg) in {"rm", "dd"} for arg in argv):
                effective = RiskLevel.HIGH
                factors.append("destructive_binary")
            if isinstance(argv, list) and any(str(arg) in {"cat", "ls", "find"} for arg in argv):
                effective = max(effective, RiskLevel.LOW, key=lambda value: ["low","medium","high","deny"].index(value.value))
        for value in invocation.arguments.values():
            if isinstance(value, str) and value.startswith("/etc"):
                effective = RiskLevel.HIGH
                factors.append("system_path")
        if scope.allowed_tools and spec.name not in scope.allowed_tools:
            effective = RiskLevel.DENY
            factors.append("tool_out_of_scope")
        return RiskAssessment(tool_name=spec.name, baseline=spec.baseline_risk, effective=effective, factors=factors)
