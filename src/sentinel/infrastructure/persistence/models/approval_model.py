from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ApprovalModel:
    token: str
    session_id: str
    tool_name: str
    parameter_hash: str
    created_at: str
    expires_at: str
    status: str
    scope_signature: str
    reason: str
