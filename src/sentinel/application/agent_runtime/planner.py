from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.llm.llm_gateway import LLMGateway
from sentinel.application.llm.prompt_assembler import PromptAssembler
from sentinel.application.llm.structured_output import StructuredOutputService
from sentinel.domain.agent.entities import AgentSession, Plan, PlanStep
from sentinel.domain.agent.value_objects import ActionDirective
from sentinel.domain.memory.entities import RetrievalBundle
from sentinel.domain.tools.entities import ToolSpec


_PLANNER_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "action": {"type": "string"},
        "response": {"type": "string"},
        "tool_name": {"type": "string"},
        "tool_args": {"type": "object"},
        "plan_goal": {"type": "string"},
        "plan_steps": {"type": "array"},
        "confidence": {"type": "number"},
    },
    "required": ["action"],
}


@dataclass(slots=True)
class PlannerService:
    llm_gateway: LLMGateway
    prompt_assembler: PromptAssembler
    structured_output: StructuredOutputService

    async def plan(
        self,
        session: AgentSession,
        user_message: str,
        summary: str,
        memories: RetrievalBundle,
        tools: list[ToolSpec],
    ) -> ActionDirective:
        prompt = self.prompt_assembler.planning_prompt(
            session, user_message, summary, memories, tools
        )

        # -------- LLM CALL --------
        payload, _usage = await self.llm_gateway.complete_json(
            prompt, _PLANNER_SCHEMA
        )

        # -------- VALIDATION --------
        try:
            valid = self.structured_output.validate_directive(payload)
        except Exception:
            return ActionDirective(
                action="respond",
                response="Respuesta generada sin planificación estructurada.",
                plan_goal=None,
                plan_steps=(),
                tool_name=None,
                tool_args={},
                confidence=0.0,
            )

        # -------- NORMALIZATION --------
        return ActionDirective(
            action=str(valid.get("action", "respond")),
            response=str(valid.get("response") or valid.get("content") or "") or None,
            plan_goal=str(valid.get("plan_goal") or "") or None,
            plan_steps=tuple(valid.get("plan_steps", [])),  # type: ignore[arg-type]
            tool_name=str(valid.get("tool_name") or "") or None,
            tool_args=dict(valid.get("tool_args", {})),  # type: ignore[arg-type]
            confidence=float(valid.get("confidence", 0.0)),
        )

    @staticmethod
    def to_plan(directive: ActionDirective, fallback_goal: str) -> Plan:
        steps: list[PlanStep] = []

        for index, raw_step in enumerate(directive.plan_steps, start=1):
            title = str(raw_step.get("title", f"step-{index}"))
            description = str(raw_step.get("description", title))

            steps.append(
                PlanStep(
                    step_id=f"step-{index}",
                    title=title,
                    description=description,
                )
            )

        # fallback: si no hay plan_steps pero hay tool → crea un step implícito
        if directive.tool_name and not steps:
            steps.append(
                PlanStep(
                    step_id="step-1",
                    title=f"Use {directive.tool_name}",
                    description=f"Invoke {directive.tool_name}",
                    tool_name=directive.tool_name,
                    tool_args=directive.tool_args,
                )
            )

        return Plan(
            goal=directive.plan_goal or fallback_goal,
            steps=steps,
        )