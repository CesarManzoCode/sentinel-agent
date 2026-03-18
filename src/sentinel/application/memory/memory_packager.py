from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.memory.entities import RetrievalBundle


@dataclass(slots=True)
class MemoryPackager:
    max_items: int = 6
    max_chars_per_item: int = 400

    def package(self, bundle: RetrievalBundle) -> list[str]:
        packaged: list[str] = []
        for item in sorted(bundle.items, key=lambda entry: entry.fused_score, reverse=True)[: self.max_items]:
            snippet = item.memory.text.strip()
            if len(snippet) > self.max_chars_per_item:
                snippet = snippet[: self.max_chars_per_item - 1] + "…"
            packaged.append(snippet)
        return packaged
