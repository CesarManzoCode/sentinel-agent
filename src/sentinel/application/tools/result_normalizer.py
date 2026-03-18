from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.tools.entities import ToolResult
from sentinel.shared.utils import compact_text


@dataclass(slots=True)
class ToolResultNormalizer:
    output_limit: int = 12_000

    def normalize(self, result: ToolResult) -> ToolResult:
        result.stdout = compact_text(result.stdout, self.output_limit)
        result.stderr = compact_text(result.stderr, self.output_limit)
        return result
