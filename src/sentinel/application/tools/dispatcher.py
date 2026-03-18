from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.safety.policy_engine import PolicyEngine
from sentinel.application.tools.argument_binding import ArgumentBinder
from sentinel.application.tools.result_normalizer import ToolResultNormalizer
from sentinel.domain.common.errors import InvalidToolInvocation
from sentinel.domain.safety.entities import IntentScope
from sentinel.domain.tools.entities import ToolInvocation, ToolResult
from sentinel.domain.tools.ports import ToolAdapterPort, ToolRegistryPort


@dataclass(slots=True)
class ToolDispatcher:
    registry: ToolRegistryPort
    policy_engine: PolicyEngine
    binder: ArgumentBinder
    normalizer: ToolResultNormalizer

    async def dispatch(self, session_id: str, scope: IntentScope, invocation: ToolInvocation) -> ToolResult:
        adapter = self._resolve_adapter(invocation.tool_name)
        bound_args = self.binder.bind(adapter.spec, invocation.arguments)
        normalized_invocation = ToolInvocation(
            invocation_id=invocation.invocation_id,
            session_id=invocation.session_id,
            tool_name=invocation.tool_name,
            arguments=bound_args,
            requested_at=invocation.requested_at,
            trace_id=invocation.trace_id,
        )
        decision = self.policy_engine.evaluate(session_id=session_id, scope=scope, spec=adapter.spec, invocation=normalized_invocation)
        if not decision.allowed:
            raise InvalidToolInvocation(decision.reason)
        result = await adapter.execute(normalized_invocation)
        return self.normalizer.normalize(result)

    def _resolve_adapter(self, name: str) -> ToolAdapterPort:
        adapter = self.registry.get_tool(name)
        if adapter is None:
            raise InvalidToolInvocation(f"unknown tool: {name}")
        if not hasattr(adapter, "execute") or not hasattr(adapter, "spec"):
            raise InvalidToolInvocation(f"tool adapter contract not satisfied: {name}")
        return adapter
