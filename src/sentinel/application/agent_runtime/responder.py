
from __future__ import annotations

from dataclasses import dataclass

from sentinel.application.llm.llm_gateway import LLMGateway
from sentinel.application.llm.prompt_assembler import PromptAssembler
from sentinel.domain.agent.entities import AgentSession


@dataclass(slots=True)
class ResponseService:
    llm_gateway: LLMGateway
    prompt_assembler: PromptAssembler

    async def respond(
        self,
        session: AgentSession,
        user_message: str,
        observations: list[str],
    ) -> str:
        prompt = self.prompt_assembler.response_prompt(
            session=session,
            user_message=user_message,
            observations=observations,
        )

        try:
            text, _usage = await self.llm_gateway.complete(prompt)
        except Exception:
            return "Ocurrió un error generando la respuesta. Intenta nuevamente."

        # -------- NORMALIZACIÓN --------
        cleaned = (text or "").strip()

        # fallback defensivo
        if not cleaned:
            return "No se pudo generar una respuesta válida."

        # evitar respuestas genéricas no deseadas
        if "language model" in cleaned.lower():
            return "Estoy aquí para ayudarte con tareas en tu sistema. ¿Qué necesitas?"

        return cleaned