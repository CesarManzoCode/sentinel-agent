from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.agent.value_objects import CompletionSignal, ExecutionBudget
from sentinel.domain.common.errors import BudgetExceeded


@dataclass(slots=True)
class AgentPolicySet:
    budget: ExecutionBudget

    def assert_within_limits(self, step_count: int, tool_calls: int) -> None:
        if step_count > self.budget.max_steps:
            raise BudgetExceeded(f"maximum reasoning steps exceeded: {step_count}>{self.budget.max_steps}")
        if tool_calls > self.budget.max_tool_calls:
            raise BudgetExceeded(f"maximum tool calls exceeded: {tool_calls}>{self.budget.max_tool_calls}")

    def should_stop(self, step_count: int, tool_calls: int, done: bool) -> CompletionSignal:
        if done:
            return CompletionSignal(done=True, reason="directive_completed")
        if step_count >= self.budget.max_steps:
            return CompletionSignal(done=True, reason="max_steps_reached")
        if tool_calls >= self.budget.max_tool_calls:
            return CompletionSignal(done=True, reason="max_tool_calls_reached")
        return CompletionSignal(done=False, reason="continue")

    @staticmethod
    def should_replan(last_tool_succeeded: bool, consecutive_failures: int) -> bool:
        return not last_tool_succeeded and consecutive_failures >= 1
