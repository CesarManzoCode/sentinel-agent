from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TokenBudgeter:
    max_context_tokens: int = 12_000

    def allocate(self) -> dict[str, int]:
        return {
            "system": int(self.max_context_tokens * 0.15),
            "history": int(self.max_context_tokens * 0.25),
            "memory": int(self.max_context_tokens * 0.20),
            "tools": int(self.max_context_tokens * 0.20),
            "observations": int(self.max_context_tokens * 0.20),
        }

    def trim(self, text: str, max_tokens: int) -> str:
        approximate_chars = max_tokens * 4
        return text if len(text) <= approximate_chars else text[: approximate_chars - 1] + "…"
