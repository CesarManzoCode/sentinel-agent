from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.agent.policies import AgentPolicySet
from sentinel.domain.agent.value_objects import ExecutionBudget


@dataclass(slots=True)
class BudgetManager:
    budget: ExecutionBudget
    step_count: int = 0
    tool_calls: int = 0

    def policy(self) -> AgentPolicySet:
        return AgentPolicySet(self.budget)

    def next_step(self) -> int:
        self.step_count += 1
        self.policy().assert_within_limits(self.step_count, self.tool_calls)
        return self.step_count

    def register_tool_call(self) -> int:
        self.tool_calls += 1
        self.policy().assert_within_limits(self.step_count, self.tool_calls)
        return self.tool_calls
