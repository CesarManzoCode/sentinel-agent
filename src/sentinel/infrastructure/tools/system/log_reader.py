from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy


@dataclass(slots=True)
class LogReaderTool(BaseToolAdapter):
    path_policy: PathPolicy
    max_bytes: int = 64_000

    @classmethod
    def create(cls, path_policy: PathPolicy) -> "LogReaderTool":
        return cls(
            spec=ToolSpec(
                name="system.logs",
                description="Read log files safely in a bounded, read-only way.",
                category=ToolCategory.SYSTEM,
                schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=10,
                concurrency_safe=True,
                side_effects=("read",),
            ),
            path_policy=path_policy,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        path = self.path_policy.assert_read_allowed(str(invocation.arguments["path"]))
        data = path.read_bytes()[-self.max_bytes :]
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=data.decode("utf-8", errors="replace"),
            metadata={"path": str(path)},
        )
