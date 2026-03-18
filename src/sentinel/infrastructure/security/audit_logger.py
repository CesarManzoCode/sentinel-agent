from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sentinel.domain.safety.ports import AuditPort


@dataclass(slots=True)
class AuditLogger(AuditPort):
    file_path: Path

    def __post_init__(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event_name: str, payload: dict[str, object]) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_name": event_name,
            "payload": payload,
        }
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
