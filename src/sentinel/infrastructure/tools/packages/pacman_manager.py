from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.packages.transaction_parser import PackageTransactionParser


@dataclass(slots=True)
class PacmanManager(BaseToolAdapter):
    parser: PackageTransactionParser
    allow_privileged: bool = False

    @classmethod
    def create(cls, parser: PackageTransactionParser, allow_privileged: bool) -> "PacmanManager":
        return cls(
            spec=ToolSpec(
                name="packages.pacman",
                description="Inspect and preview pacman operations with high-risk treatment for mutations.",
                category=ToolCategory.PACKAGES,
                schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string"},
                        "packages": {"type": "array"},
                        "apply": {"type": "boolean"},
                    },
                    "required": ["operation"],
                },
                baseline_risk=RiskLevel.HIGH,
                timeout_seconds=30,
                concurrency_safe=False,
                side_effects=("system", "packages"),
            ),
            parser=parser,
            allow_privileged=allow_privileged,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        operation = str(invocation.arguments["operation"])
        packages = [str(item) for item in invocation.arguments.get("packages", [])]  # type: ignore[arg-type]
        apply = bool(invocation.arguments.get("apply", False))
        preview = self.parser.preview(operation, packages)
        if operation in {"search", "info", "query"}:
            stdout, stderr, returncode = await self._run_read_only(operation, packages)
            return ToolResult(
                invocation_id=invocation.invocation_id,
                tool_name=self.spec.name,
                success=returncode == 0,
                stdout=stdout,
                stderr=stderr,
                metadata={"preview": preview, "operation": operation},
            )
        if not apply or not self.allow_privileged:
            message = "privileged execution disabled; preview only"
            return ToolResult(
                invocation_id=invocation.invocation_id,
                tool_name=self.spec.name,
                success=False,
                stdout="",
                stderr=message,
                metadata={"preview": preview, "operation": operation},
            )
        stdout, stderr, returncode = await self._run_apply(operation, packages)
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=returncode == 0,
            stdout=stdout,
            stderr=stderr,
            metadata={"preview": preview, "operation": operation},
        )

    async def _run_read_only(self, operation: str, packages: list[str]) -> tuple[str, str, int]:
        command = {
            "search": ["pacman", "-Ss", *packages],
            "info": ["pacman", "-Si", *packages],
            "query": ["pacman", "-Qi", *packages] if packages else ["pacman", "-Q"],
        }[operation]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            int(process.returncode),
        )

    async def _run_apply(self, operation: str, packages: list[str]) -> tuple[str, str, int]:
        command = {
            "install": ["sudo", "pacman", "-S", *packages],
            "remove": ["sudo", "pacman", "-R", *packages],
            "upgrade": ["sudo", "pacman", "-Syu"],
        }[operation]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            int(process.returncode),
        )
