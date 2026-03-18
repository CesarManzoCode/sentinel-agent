from __future__ import annotations

import re
from dataclasses import dataclass

from sentinel.domain.safety.ports import SecretDetectionPort


_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
]


@dataclass(slots=True)
class SecretDetector(SecretDetectionPort):
    def find_secrets(self, text: str) -> list[str]:
        matches: list[str] = []
        for pattern in _PATTERNS:
            matches.extend(pattern.findall(text))
        return matches
