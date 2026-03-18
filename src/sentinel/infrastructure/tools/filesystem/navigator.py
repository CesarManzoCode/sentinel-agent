from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sentinel.domain.common.enums import RiskLevel, ToolCategory
from sentinel.domain.tools.entities import ToolInvocation, ToolResult, ToolSpec
from sentinel.domain.tools.value_objects import SideEffectProfile
from sentinel.infrastructure.tools.base import BaseToolAdapter
from sentinel.infrastructure.tools.filesystem.path_policy import PathPolicy


@dataclass(slots=True)
class FilesystemNavigatorTool(BaseToolAdapter):
    path_policy: PathPolicy

    @classmethod
    def create(cls, path_policy: PathPolicy):
        spec = ToolSpec(
            name="filesystem.navigator",
            description="Navigate filesystem: list files, directories, and inspect paths",
            category=ToolCategory.FILESYSTEM,
            baseline_risk=RiskLevel.LOW,
            schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list_files", "list_dirs", "stat"],
                    },
                    "path": {"type": "string"},
                    "pattern": {"type": "string"},
                    "recursive": {"type": "boolean"},
                },
                "required": ["path"],
            },
            timeout_seconds=5,
            concurrency_safe=True,
            side_effects=SideEffectProfile(
                "low",                 # 👈 level
                False,                 # requires_approval
                True,                  # touches_filesystem
                False                  # touches_network
            )
        )

        return cls(spec=spec, path_policy=path_policy)

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        args = invocation.arguments or {}

        # -------- NORMALIZACIÓN --------
        args = invocation.arguments or {}

        # soportar múltiples variantes del modelo
        operation = (
            args.get("operation")
            or args.get("action")
            or "list_files"
        )

        # normalizar valores
        if operation == "list":
            operation = "list_files"

        operation = str(operation)

        path_input = str(args.get("path", "."))
        path = self.path_policy.assert_read_allowed(path_input)

        pattern = str(args.get("pattern", "*"))
        recursive = bool(args.get("recursive", False))

        # -------- OPERACIONES --------

        if operation == "list_files":
            if path.is_file():
                payload = {
                    "type": "file",
                    "path": str(path),
                    "size": path.stat().st_size,
                }
            else:
                iterator = path.rglob(pattern) if recursive else path.glob(pattern)
                payload = {
                    "type": "directory",
                    "path": str(path),
                    "entries": sorted(str(item) for item in iterator)[:200],
                }

        elif operation == "list_dirs":
            iterator = (
                (p for p in path.rglob("*") if p.is_dir())
                if recursive
                else (p for p in path.iterdir() if p.is_dir())
            )
            payload = {
                "type": "directories",
                "path": str(path),
                "entries": sorted(str(item) for item in iterator)[:200],
            }

        elif operation == "stat":
            payload = {
                "type": "stat",
                "path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": path.stat().st_size if path.exists() and path.is_file() else None,
            }

        else:
            payload = {
                "error": f"Unsupported operation: {operation}",
                "supported_operations": ["list_files", "list_dirs", "stat"],
            }

        # -------- RESULT --------
        return ToolResult(
            invocation_id=invocation.invocation_id,
            tool_name=self.spec.name,
            success=True,
            stdout=json.dumps(payload, ensure_ascii=False, indent=2),
        )