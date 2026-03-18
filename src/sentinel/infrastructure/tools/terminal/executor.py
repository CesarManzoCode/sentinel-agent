from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy
from sentinel.infrastructure.tools.terminal.parser import CommandParser
from sentinel.infrastructure.tools.terminal.sandbox import CommandSandbox


@dataclass(slots=True)
class TerminalExecutor(BaseToolAdapter):
    parser: CommandParser
    sandbox: CommandSandbox
    path_policy: PathPolicy
    output_limit: int = 32_000

    @classmethod
    def create(
        cls,
        parser: CommandParser,
        sandbox: CommandSandbox,
        path_policy: PathPolicy,
    ) -> "TerminalExecutor":
        return cls(
            spec=ToolSpec(
                name="terminal.exec",
                description="Execute a structured command safely without invoking a raw shell.",
                category=ToolCategory.TERMINAL,
                schema={
                    "type": "object",
                    "properties": {
                        "executable": {"type": "string"},
                        "argv": {"type": "array"},
                        "cwd": {"type": "string"},
                        "env": {"type": "object"},
                    },
                    "required": ["executable"],
                },
                baseline_risk=RiskLevel.LOW,
                timeout_seconds=20,
                concurrency_safe=True,
                side_effects=("process",),
            ),
            parser=parser,
            sandbox=sandbox,
            path_policy=path_policy,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        executable, argv, cwd, env = self.parser.parse(invocation.arguments)
        safe_cwd = None
        if cwd:
            safe_cwd = str(self.path_policy.assert_read_allowed(cwd))
        final_argv, final_cwd, final_env, boundary = self.sandbox.prepare(executable, argv, safe_cwd, env)
        started = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                *final_argv,
                cwd=final_cwd,
                env=final_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=self.sandbox.preexec,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=self.spec.timeout_seconds,
            )
            duration_ms = int((time.perf_counter() - started) * 1000)
            stdout = stdout_bytes.decode("utf-8", errors="replace")[: self.output_limit]
            stderr = stderr_bytes.decode("utf-8", errors="replace")[: self.output_limit]
            return ToolResult(
                invocation_id=invocation.invocation_id,
                tool_name=self.spec.name,
                success=process.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms,
                metadata={"returncode": process.returncode, "boundary": boundary, "cwd": final_cwd},
            )
        except TimeoutError:
            duration_ms = int((time.perf_counter() - started) * 1000)
            return ToolResult(
                invocation_id=invocation.invocation_id,
                tool_name=self.spec.name,
                success=False,
                stderr="command timed out",
                duration_ms=duration_ms,
            )
