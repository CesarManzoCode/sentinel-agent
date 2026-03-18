from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel
from sentinel.domain.tools.entities import ToolInvocation, ToolSpec


@dataclass(slots=True)
class ToolPolicy:
    def can_run(self, spec: ToolSpec, risk: RiskLevel) -> bool:
        if not spec.enabled:
            return False
        return risk != RiskLevel.DENY


@dataclass(slots=True)
class CapabilityPolicy:
    def within_scope(self, invocation: ToolInvocation, allowed_resources: set[str]) -> bool:
        if not allowed_resources:
            return True
        values = {str(value) for value in invocation.arguments.values()}
        return any(any(resource in value for resource in allowed_resources) for value in values) or not values
