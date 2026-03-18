from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.common.enums import TurnState
from sentinel.domain.common.errors import SentinelError


@dataclass(slots=True)
class TurnStateMachine:
    state: TurnState = TurnState.IDLE

    _valid_transitions: dict[TurnState, set[TurnState]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._valid_transitions = {
            TurnState.IDLE: {TurnState.PLANNING},
            TurnState.PLANNING: {TurnState.EXECUTING, TurnState.WAITING_APPROVAL, TurnState.RESPONDING, TurnState.FAILED},
            TurnState.WAITING_APPROVAL: {TurnState.EXECUTING, TurnState.RESPONDING, TurnState.FAILED},
            TurnState.EXECUTING: {TurnState.REFLECTING, TurnState.FAILED},
            TurnState.REFLECTING: {TurnState.PLANNING, TurnState.RESPONDING, TurnState.FAILED},
            TurnState.RESPONDING: {TurnState.FINALIZED, TurnState.FAILED},
            TurnState.FINALIZED: set(),
            TurnState.FAILED: set(),
        }

    def transition(self, target: TurnState) -> None:
        allowed = self._valid_transitions[self.state]
        if target not in allowed:
            raise SentinelError(f"invalid turn state transition: {self.state} -> {target}")
        self.state = target
