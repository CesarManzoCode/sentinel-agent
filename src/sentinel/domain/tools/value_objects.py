from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import SideEffectLevel


@dataclass(slots=True, frozen=True)
class ToolSchema:
    payload: dict[str, object]


@dataclass(slots=True, frozen=True)
class ExecutionConstraints:
    timeout_seconds: int
    concurrency_safe: bool
    shell_mode_allowed: bool = False


@dataclass(slots=True, frozen=True)
class SideEffectProfile:
    level: SideEffectLevel
    requires_approval: bool
    touches_filesystem: bool
    touches_network: bool
