from __future__ import annotations

from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DENY = "deny"


class ActionState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETED = "completed"
    FAILED = "failed"


class MemoryType(str, Enum):
    PROFILE = "profile"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    SESSION_SUMMARY = "session_summary"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ToolCategory(str, Enum):
    TERMINAL = "terminal"
    FILESYSTEM = "filesystem"
    SYSTEM = "system"
    INTERNET = "internet"
    PACKAGES = "packages"


class TurnState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    RESPONDING = "responding"
    FINALIZED = "finalized"
    FAILED = "failed"


class SideEffectLevel(str, Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    SYSTEM = "system"
