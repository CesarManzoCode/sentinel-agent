from __future__ import annotations

import re
from dataclasses import dataclass

from sentinel.domain.safety.ports import SecretDetectionPort


@dataclass(slots=True)
class RedactionService:
    detector: SecretDetectionPort

    def redact(self, text: str) -> str:
        redacted = text
        for secret in self.detector.find_secrets(text):
            redacted = redacted.replace(secret, "***REDACTED***")
        redacted = re.sub(r"(Authorization: Bearer )([A-Za-z0-9._-]+)", r"\1***REDACTED***", redacted)
        return redacted
