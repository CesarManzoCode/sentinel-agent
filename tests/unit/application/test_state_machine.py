import pytest

from sentinel.application.agent_runtime.state_machine import TurnStateMachine
from sentinel.domain.common.enums import TurnState
from sentinel.domain.common.errors import SentinelError


def test_valid_state_transitions() -> None:
    machine = TurnStateMachine()
    machine.transition(TurnState.PLANNING)
    machine.transition(TurnState.RESPONDING)
    machine.transition(TurnState.FINALIZED)
    assert machine.state == TurnState.FINALIZED


def test_invalid_state_transition_raises() -> None:
    machine = TurnStateMachine()
    with pytest.raises(SentinelError):
        machine.transition(TurnState.EXECUTING)
