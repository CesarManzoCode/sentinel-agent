from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class EmbeddingCache:
    db: DatabaseManager

    def get(self, cache_key: str) -> list[float] | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT vector_json FROM embedding_cache WHERE cache_key = ?", (cache_key,)).fetchone()
        if row is None:
            return None
        return list(json.loads(row["vector_json"]))

    def save(self, cache_key: str, text_hash: str, vector: list[float]) -> None:
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO embedding_cache (cache_key, text_hash, vector_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (cache_key, text_hash, json.dumps(vector), datetime.now(timezone.utc).isoformat()),
            )
