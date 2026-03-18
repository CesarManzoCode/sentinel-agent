from __future__ import annotations

import re
from dataclasses import dataclass, field


_METACHAR_RE = re.compile(r"[|&;><`$(){}]")


@dataclass(slots=True)
class TerminalCommandValidator:
    denied_binaries: set[str]
    denied_flags: set[str] = field(default_factory=lambda: {"--interactive", "-i"})
    denied_patterns: tuple[str, ...] = ("..",)

    def validate(self, executable: str, argv: list[str]) -> list[str]:
        violations: list[str] = []
        if executable in self.denied_binaries:
            violations.append(f"binary denied by policy: {executable}")
        if _METACHAR_RE.search(executable):
            violations.append("shell metacharacters are not allowed in executable")
        for arg in argv:
            if _METACHAR_RE.search(arg):
                violations.append(f"shell metacharacters are not allowed in argument: {arg}")
            if arg in self.denied_flags:
                violations.append(f"interactive flag denied: {arg}")
        if executable in {"bash", "sh", "zsh", "fish"}:
            violations.append("raw shell interpreters are disabled by default")
        if any(pattern in executable for pattern in self.denied_patterns):
            violations.append("path traversal pattern detected in executable")
        return violations
