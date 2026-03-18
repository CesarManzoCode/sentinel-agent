from __future__ import annotations

import json
import os
import platform
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter


@dataclass(slots=True)
class EnvironmentInspectorTool(BaseToolAdapter):
    @classmethod
    def create(cls) -> "EnvironmentInspectorTool":
        return cls(
            spec=ToolSpec(
                name="system.env",
                description="Inspect local runtime, distro, kernel, shell, and selected environment information.",
                category=ToolCategory.SYSTEM,
                schema={"type": "object", "properties": {}, "required": []},
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=5,
                concurrency_safe=True,
                side_effects=("read",),
            )
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        payload = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "shell": os.getenv("SHELL", ""),
            "cwd": os.getcwd(),
        }
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=json.dumps(payload, ensure_ascii=False, indent=2),
        )
