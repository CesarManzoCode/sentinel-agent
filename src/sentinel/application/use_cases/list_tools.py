from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.tools.registry import ToolRegistryService
from sentinel.domain.tools.entities import ToolSpec


@dataclass(slots=True)
class ListTools:
    registry: ToolRegistryService

    def execute(self) -> list[ToolSpec]:
        return self.registry.list_enabled()
