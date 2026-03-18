from sentinel.domain.agent.policies import AgentPolicySet
from sentinel.domain.agent.value_objects import ExecutionBudget
from sentinel.domain.common.errors import BudgetExceeded


def test_agent_policy_stops_on_budget() -> None:
    budget = ExecutionBudget(max_steps=2, max_tool_calls=1, max_tokens=1000, wall_clock_seconds=30)
    policy = AgentPolicySet(budget)

    signal = policy.should_stop(step_count=1, tool_calls=0, done=False)
    assert signal.done is False

    signal = policy.should_stop(step_count=2, tool_calls=0, done=False)
    assert signal.done is True
    assert signal.reason == "max_steps_reached"


def test_agent_policy_raises_when_over_limit() -> None:
    budget = ExecutionBudget(max_steps=1, max_tool_calls=1, max_tokens=1000, wall_clock_seconds=30)
    policy = AgentPolicySet(budget)

    try:
        policy.assert_within_limits(step_count=2, tool_calls=0)
    except BudgetExceeded as exc:
        assert "maximum reasoning steps exceeded" in str(exc)
    else:
        raise AssertionError("BudgetExceeded was not raised")
