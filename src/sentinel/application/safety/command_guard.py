from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.errors import PolicyViolation
from sentinel.domain.safety.ports import CommandValidationPort


@dataclass(slots=True)
class CommandGuard:
    validator: CommandValidationPort

    def guard(self, executable: str, argv: list[str]) -> None:
        violations = self.validator.validate(executable, argv)
        if violations:
            raise PolicyViolation("; ".join(violations))
