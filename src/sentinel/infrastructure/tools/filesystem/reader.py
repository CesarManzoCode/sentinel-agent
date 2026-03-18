from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy


@dataclass(slots=True)
class FilesystemReaderTool(BaseToolAdapter):
    path_policy: PathPolicy
    max_bytes: int = 64_000

    @classmethod
    def create(cls, path_policy: PathPolicy) -> "FilesystemReaderTool":
        return cls(
            spec=ToolSpec(
                name="filesystem.reader",
                description="Read a UTF-8 text file safely within approved roots.",
                category=ToolCategory.FILESYSTEM,
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
        data = path.read_bytes()[: self.max_bytes]
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=text,
            metadata={"path": str(path), "truncated": path.stat().st_size > self.max_bytes},
        )
