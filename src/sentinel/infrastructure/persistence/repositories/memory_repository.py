from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.domain.memory.ports import MemoryRepositoryPort
from sentinel.infrastructure.persistence.db import DatabaseManager


@dataclass(slots=True)
class SQLiteMemoryRepository(MemoryRepositoryPort):
    db: DatabaseManager

    def save(self, memory: MemoryEntry) -> None:
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO memories (
                    memory_id, memory_type, text, created_at, updated_at, salience, scope, tags_json, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    memory_type = excluded.memory_type,
                    text = excluded.text,
                    updated_at = excluded.updated_at,
                    salience = excluded.salience,
                    scope = excluded.scope,
                    tags_json = excluded.tags_json,
                    metadata_json = excluded.metadata_json
                """,
                (
                    memory.memory_id.value,
                    memory.memory_type.value,
                    memory.text,
                    memory.created_at.isoformat(),
                    memory.updated_at.isoformat(),
                    memory.salience,
                    memory.scope,
                    json.dumps(memory.tags, ensure_ascii=False),
                    json.dumps(memory.metadata, ensure_ascii=False),
                ),
            )
            try:
                conn.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory.memory_id.value,))
                conn.execute(
                    "INSERT INTO memory_fts (memory_id, text) VALUES (?, ?)",
                    (memory.memory_id.value, memory.text),
                )
            except sqlite3.OperationalError:
                pass

    def get(self, memory_id: MemoryId) -> MemoryEntry | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id.value,)).fetchone()
        return self._row_to_memory(row) if row is not None else None

    def search_lexical(self, query: str, limit: int) -> list[MemoryEntry]:
        with self.db.connection() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT m.*
                    FROM memory_fts f
                    JOIN memories m ON m.memory_id = f.memory_id
                    WHERE memory_fts MATCH ?
                    ORDER BY bm25(memory_fts)
                    LIMIT ?
                    """,
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE text LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"%{query}%", limit),
                ).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def list_recent(self, limit: int) -> list[MemoryEntry]:
        with self.db.connection() as conn:
            rows = conn.execute("SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def delete(self, memory_id: MemoryId) -> None:
        with self.db.connection() as conn:
            conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id.value,))
            try:
                conn.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory_id.value,))
            except sqlite3.OperationalError:
                pass

    @staticmethod
    def _row_to_memory(row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            memory_id=MemoryId(row["memory_id"]),
            memory_type=MemoryType(row["memory_type"]),
            text=row["text"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            salience=float(row["salience"]),
            scope=row["scope"],
            tags=list(json.loads(row["tags_json"])),
            metadata=dict(json.loads(row["metadata_json"])),
        )
