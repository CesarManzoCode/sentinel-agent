from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter


@dataclass(slots=True)
class ProcessInspectorTool(BaseToolAdapter):
    @classmethod
    def create(cls) -> "ProcessInspectorTool":
        return cls(
            spec=ToolSpec(
                name="system.processes",
                description="Inspect running processes using ps in read-only mode.",
                category=ToolCategory.SYSTEM,
                schema={"type": "object", "properties": {}, "required": []},
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=5,
                concurrency_safe=True,
                side_effects=("read",),
            )
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        process = await asyncio.create_subprocess_exec(
            "ps",
            "-eo",
            "pid,ppid,comm,%cpu,%mem,args",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=process.returncode == 0,
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
        )
