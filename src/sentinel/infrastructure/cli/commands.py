from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParsedCommand:
    name: str
    args: list[str]


@dataclass(slots=True)
class CommandRouter:
    def parse(self, raw: str) -> ParsedCommand | None:
        if not raw.startswith("/"):
            return None
        parts = raw[1:].strip().split()
        if not parts:
            return None
        return ParsedCommand(name=parts[0], args=parts[1:])
