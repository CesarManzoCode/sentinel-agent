from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from sentinel.config.settings import Settings
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class HealthChecker:
    settings: Settings
    db: DatabaseManager

    def check(self) -> dict[str, object]:
        status: dict[str, object] = {
            "db": False,
            "groq_api_key_present": bool(self.settings.llm.api_key),
            "vector_dir": str(self.settings.paths.vector_dir),
        }
        try:
            with self.db.connection() as conn:
                conn.execute("SELECT 1")
            status["db"] = True
        except sqlite3.Error:
            status["db"] = False
        return status
