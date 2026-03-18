from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PromptFactory:
    prompt_text: str = "sentinel> "

    def read(self) -> str:
        return input(self.prompt_text)
