from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.domain.tools.ports import ToolAdapterPort, ToolRegistryPort


@dataclass(slots=True)
class FakeToolAdapter(ToolAdapterPort):
    spec: ToolSpec
    responses: list[ToolResult] = field(default_factory=list)
    calls: list[ToolInvocation] = field(default_factory=list)

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        self.calls.append(invocation)
        if self.responses:
            result = self.responses.pop(0)
            return result
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=f"fake result from {self.spec.name}",
        )


@dataclass(slots=True)
class FakeToolRegistry(ToolRegistryPort):
    adapters: dict[str, FakeToolAdapter]

    def list_tools(self) -> list[ToolSpec]:
        return [adapter.spec for adapter in self.adapters.values()]

    def get_tool(self, name: str) -> FakeToolAdapter | None:
        return self.adapters.get(name)


def make_fake_tool(name: str, category: ToolCategory = ToolCategory.SYSTEM) -> FakeToolAdapter:
    spec = ToolSpec(
        name=name,
        description=f"fake tool {name}",
        category=category,
        schema={"type": "object", "properties": {}, "required": []},
        baseline_risk=RiskLevel.LOW,
        timeout_seconds=5,
        concurrency_safe=True,
        side_effects=("read",),
    )
    return FakeToolAdapter(spec=spec)
