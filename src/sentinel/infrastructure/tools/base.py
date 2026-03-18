from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.tools.entities import ToolSpec


@dataclass(slots=True)
class BaseToolAdapter:
    spec: ToolSpec
