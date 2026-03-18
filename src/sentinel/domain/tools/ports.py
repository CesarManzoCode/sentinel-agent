from __future__ import annotations

from typing import Protocol

from sentinel.domain.tools.entities import ToolResult, ToolSpec, ToolInvocation


class ToolAdapterPort(Protocol):
    @property
    def spec(self) -> ToolSpec: ...

    async def execute(self, invocation: ToolInvocation) -> ToolResult: ...


class ToolRegistryPort(Protocol):
    def list_tools(self) -> list[ToolSpec]: ...
    def get_tool(self, name: str) -> ToolAdapterPort | None: ...


class ToolCatalogPort(Protocol):
    def save_tool(self, spec: ToolSpec) -> None: ...
    def list_enabled(self) -> list[ToolSpec]: ...
