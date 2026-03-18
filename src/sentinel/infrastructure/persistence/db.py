from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from sentinel.domain.common.errors import PersistenceError


DDL = [
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS session_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS memories (
        memory_id TEXT PRIMARY KEY,
        memory_type TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        salience REAL NOT NULL,
        scope TEXT NOT NULL,
        tags_json TEXT NOT NULL,
        metadata_json TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS traces (
        trace_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trace_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trace_id TEXT NOT NULL REFERENCES traces(trace_id) ON DELETE CASCADE,
        event_name TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS approvals (
        token TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        tool_name TEXT NOT NULL,
        parameter_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        status TEXT NOT NULL,
        scope_signature TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT ''
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tool_catalog (
        name TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        schema_json TEXT NOT NULL,
        baseline_risk TEXT NOT NULL,
        timeout_seconds INTEGER NOT NULL,
        concurrency_safe INTEGER NOT NULL,
        side_effects_json TEXT NOT NULL,
        enabled INTEGER NOT NULL,
        hidden INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS embedding_cache (
        cache_key TEXT PRIMARY KEY,
        text_hash TEXT NOT NULL,
        vector_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
]


@dataclass(slots=True)
class DatabaseManager:
    db_file: Path

    def initialize(self) -> None:
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.connection() as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA synchronous=NORMAL")
                for statement in DDL:
                    conn.execute(statement)
                try:
                    conn.execute(
                        "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(memory_id UNINDEXED, text)"
                    )
                except sqlite3.OperationalError:
                    # FTS5 may not be available. Lexical retrieval will fall back to LIKE queries.
                    pass
        except sqlite3.Error as exc:
            raise PersistenceError(f"database initialization failed: {exc}") from exc

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
