from __future__ import annotations

import difflib
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy


@dataclass(slots=True)
class FilesystemWriterTool(BaseToolAdapter):
    path_policy: PathPolicy
    backup_extension: str = ".bak"

    @classmethod
    def create(cls, path_policy: PathPolicy) -> "FilesystemWriterTool":
        return cls(
            spec=ToolSpec(
                name="filesystem.writer",
                description="Write a text file safely inside approved roots with diff preview metadata.",
                category=ToolCategory.FILESYSTEM,
                schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "create_backup": {"type": "boolean"},
                    },
                    "required": ["path", "content"],
                },
                baseline_risk=RiskLevel.MEDIUM,
                timeout_seconds=10,
                concurrency_safe=False,
                side_effects=("write",),
            ),
            path_policy=path_policy,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        path = self.path_policy.assert_write_allowed(str(invocation.arguments["path"]))
        content = str(invocation.arguments["content"])
        create_backup = bool(invocation.arguments.get("create_backup", True))
        before = path.read_text(encoding="utf-8") if path.exists() else ""
        if create_backup and path.exists():
            path.with_suffix(path.suffix + self.backup_extension).write_text(before, encoding="utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        diff = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"{path}.before",
                tofile=f"{path}.after",
            )
        )
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=f"wrote {path}",
            metadata={"path": str(path), "diff": diff[:8000]},
        )
