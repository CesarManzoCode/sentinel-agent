from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.tools.entities import ToolSpec
from sentinel.domain.tools.ports import ToolRegistryPort


@dataclass(slots=True)
class ToolRegistryService:
    registry: ToolRegistryPort

    def list_enabled(self) -> list[ToolSpec]:
        return [tool for tool in self.registry.list_tools() if tool.enabled and not tool.hidden]

    def get(self, name: str) -> ToolSpec | None:
        tool = self.registry.get_tool(name)
        if tool is None or not tool.enabled:
            return None
        return tool
