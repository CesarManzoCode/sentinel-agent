from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryModel:
    memory_id: str
    memory_type: str
    text: str
    created_at: str
    updated_at: str
    salience: float
    scope: str
    tags_json: str
    metadata_json: str
