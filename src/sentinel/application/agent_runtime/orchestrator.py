from __future__ import annotations

import logging
from dataclasses import dataclass

from sentinel.application.agent_runtime.budgets import BudgetManager
from sentinel.application.agent_runtime.context_builder import ContextBuilder
from sentinel.application.agent_runtime.dto import ApprovalPrompt, HandleTurnRequest, HandleTurnResponse
from sentinel.application.agent_runtime.executor import ExecutionService
from sentinel.application.agent_runtime.planner import PlannerService
from sentinel.application.agent_runtime.reflector import ReflectionService
from sentinel.application.agent_runtime.responder import ResponseService
from sentinel.application.agent_runtime.session_manager import SessionManager
from sentinel.application.agent_runtime.state_machine import TurnStateMachine
from sentinel.application.audit.trace_service import TraceService
from sentinel.application.memory.consolidation_service import MemoryConsolidationService
from sentinel.application.tools.capability_scope import CapabilityScopeService
from sentinel.domain.agent.value_objects import ExecutionBudget
from sentinel.domain.common.enums import TurnState
from sentinel.domain.common.errors import ApprovalRequired, BudgetExceeded, PolicyViolation
from sentinel.shared.constants import (
    TRACE_EVENT_PLAN_CREATED,
    TRACE_EVENT_RESPONSE_READY,
    TRACE_EVENT_TOOL_FINISHED,
    TRACE_EVENT_TOOL_STARTED,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentOrchestrator:
    session_manager: SessionManager
    context_builder: ContextBuilder
    planner: PlannerService
    executor: ExecutionService
    reflector: ReflectionService
    responder: ResponseService
    trace_service: TraceService
    scope_service: CapabilityScopeService
    memory_consolidation: MemoryConsolidationService
    default_budget: ExecutionBudget
    memory_top_k: int

    async def handle_turn(self, request: HandleTurnRequest) -> HandleTurnResponse:
        session = self.session_manager.load_or_create(request.session_id, request.user_message)
        self.session_manager.append_user_message(session, request.user_message)
        trace = self.trace_service.start(session.session_id)
        machine = TurnStateMachine()
        budget = BudgetManager(self.default_budget)
        scope = self.scope_service.derive(request.user_message)
        debug_events: list[str] = [f"scope: {scope.describe()}"] if request.debug else []
        tool_events: list[str] = []
        observations: list[str] = []
        approvals: list[ApprovalPrompt] = []
        final_message = ""
        directive_tool_name: str | None = None

        while True:
            try:
                machine.transition(TurnState.PLANNING)
                budget.next_step()
                context = await self.context_builder.build(session, request.user_message, self.memory_top_k)
                directive = await self.planner.plan(
                    session=session,
                    user_message=request.user_message
                    + ("\nLatest observations:\n" + "\n".join(observations) if observations else ""),
                    summary=str(context["summary"]),
                    memories=context["memories"],  # type: ignore[arg-type]
                    tools=context["tools"],  # type: ignore[arg-type]
                )
                directive_tool_name = directive.tool_name
                self.trace_service.append(
                    str(trace.trace_id),
                    TRACE_EVENT_PLAN_CREATED,
                    {"action": directive.action, "tool_name": directive.tool_name, "confidence": directive.confidence},
                )
                if request.debug:
                    debug_events.append(
                        f"planner: action={directive.action} tool={directive.tool_name} confidence={directive.confidence:.2f}"
                    )

                if directive.action in {"respond", "stop"}:
                    machine.transition(TurnState.RESPONDING)
                    final_message = directive.response or await self.responder.respond(
                        session=session,
                        user_message=request.user_message,
                        observations=observations,
                    )
                    self.trace_service.append(
                        str(trace.trace_id),
                        TRACE_EVENT_RESPONSE_READY,
                        {"message": final_message[:500]},
                    )
                    machine.transition(TurnState.FINALIZED)
                    break

                if directive.action == "tool" and directive.tool_name:
                    machine.transition(TurnState.EXECUTING)
                    budget.register_tool_call()
                    tool_events.append(f"calling {directive.tool_name}")
                    self.trace_service.append(
                        str(trace.trace_id),
                        TRACE_EVENT_TOOL_STARTED,
                        {"tool_name": directive.tool_name, "args": directive.tool_args},
                    )
                    result = await self.executor.execute(
                        session_id=session.session_id,
                        trace_id=str(trace.trace_id),
                        scope=scope,
                        tool_name=directive.tool_name,
                        tool_args=directive.tool_args,
                    )
                    observation = f"[{result.tool_name}] success={result.success} stdout={result.stdout} stderr={result.stderr}"
                    observations.append(observation)
                    tool_events.append(f"{result.tool_name} -> {'ok' if result.success else 'error'}")
                    self.trace_service.append(
                        str(trace.trace_id),
                        TRACE_EVENT_TOOL_FINISHED,
                        {
                            "tool_name": result.tool_name,
                            "success": result.success,
                            "duration_ms": result.duration_ms,
                            "stdout": result.stdout[:500],
                            "stderr": result.stderr[:500],
                        },
                    )
                    machine.transition(TurnState.REFLECTING)
                    signal = self.reflector.reflect(result)
                    if signal.reason == "tool_failed":
                        observations.append("planner should re-evaluate after tool failure")
                    machine.state = TurnState.IDLE
                    continue

                machine.transition(TurnState.RESPONDING)
                final_message = await self.responder.respond(session, request.user_message, observations)
                machine.transition(TurnState.FINALIZED)
                break

            except ApprovalRequired as approval_exc:
                machine.state = TurnState.WAITING_APPROVAL
                approvals.append(
                    ApprovalPrompt(
                        token=approval_exc.token,
                        tool_name=directive_tool_name or "unknown",
                        risk="approval-required",
                        preview="Use `/approve <token>` or `/deny <token>` to continue.",
                    )
                )
                final_message = "Action requires approval before execution."
                break
            except (BudgetExceeded, PolicyViolation) as exc:
                machine.state = TurnState.FAILED
                final_message = f"Blocked by runtime policy: {exc}"
                break
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.exception("turn failed", extra={"trace_id": str(trace.trace_id)})
                machine.state = TurnState.FAILED
                final_message = f"Unexpected runtime failure: {exc}"
                break

        self.session_manager.append_assistant_message(session, final_message)
        self.session_manager.compact(session)
        await self.memory_consolidation.consolidate_session(
            str(session.session_id), [message.content for message in session.messages]
        )

        return HandleTurnResponse(
            session_id=str(session.session_id),
            trace_id=str(trace.trace_id),
            message=final_message,
            approvals=approvals,
            debug_events=debug_events,
            tool_events=tool_events,
        )
