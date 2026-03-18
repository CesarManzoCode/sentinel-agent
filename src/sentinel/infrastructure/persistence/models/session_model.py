from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SessionModel:
    session_id: str
    title: str
    summary: str
    created_at: str
    updated_at: str
