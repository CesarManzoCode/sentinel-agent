from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ExecutionProfile:
    name: str
    auto_approve_low_risk: bool
    auto_approve_medium_risk: bool
    enable_shell_mode: bool
    debug: bool
    max_steps_per_turn: int
    max_tool_calls_per_turn: int


PROFILES: dict[str, ExecutionProfile] = {
    "safe": ExecutionProfile(
        name="safe",
        auto_approve_low_risk=True,
        auto_approve_medium_risk=False,
        enable_shell_mode=False,
        debug=False,
        max_steps_per_turn=4,
        max_tool_calls_per_turn=2,
    ),
    "balanced": ExecutionProfile(
        name="balanced",
        auto_approve_low_risk=True,
        auto_approve_medium_risk=False,
        enable_shell_mode=False,
        debug=False,
        max_steps_per_turn=6,
        max_tool_calls_per_turn=4,
    ),
    "debug": ExecutionProfile(
        name="debug",
        auto_approve_low_risk=True,
        auto_approve_medium_risk=False,
        enable_shell_mode=False,
        debug=True,
        max_steps_per_turn=8,
        max_tool_calls_per_turn=6,
    ),
    "minimal": ExecutionProfile(
        name="minimal",
        auto_approve_low_risk=True,
        auto_approve_medium_risk=False,
        enable_shell_mode=False,
        debug=False,
        max_steps_per_turn=3,
        max_tool_calls_per_turn=1,
    ),
}
