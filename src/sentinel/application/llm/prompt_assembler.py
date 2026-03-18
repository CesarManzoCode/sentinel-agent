from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.agent.entities import AgentSession
from sentinel.domain.llm.value_objects import PromptEnvelope
from sentinel.domain.memory.entities import RetrievalBundle
from sentinel.domain.tools.entities import ToolSpec


@dataclass(slots=True)
class PromptAssembler:
    def planning_prompt(
    self,
    session,
    user_message: str,
    summary: str,
    memories,
    tools,
    ) -> str:

        tool_descriptions = "\n".join(
            f"- {t.name}: {t.description}" for t in tools
        )

        return f"""
You are Sentinel, a local AI agent operating in a controlled execution environment.

You are NOT a generic chatbot.
You MUST behave as an agent that can:
- reason
- decide actions
- optionally use tools
- or respond directly

You MUST ALWAYS output valid JSON.

---

# TASK
User message:
{user_message}

---

# CONTEXT
Session summary:
{summary}

---

# AVAILABLE TOOLS
{tool_descriptions}

---

# INSTRUCTIONS

You must choose ONE action:

1. "respond" → if no tools needed
2. "tool" → if a tool is required
3. "replan" → if plan must change
4. "stop" → if finished

---

# RESPONSE FORMAT (STRICT JSON)

{{
  "action": "respond | tool | replan | stop",
  "response": "string (only if action=respond)",
  "tool_name": "string (if action=tool)",
  "tool_args": {{}} ,
  "plan_goal": "string",
  "plan_steps": [],
  "confidence": 0.0
}}

---

# RULES

- NEVER say "I am a language model"
- NEVER explain your nature
- NEVER break JSON format
- If simple greeting → respond
- If unsure → respond conservatively
- Prefer direct response unless tools are needed

Return ONLY a valid JSON object.

Example:
{{
  "action": "respond",
  "response": "Hello",
  "confidence": 0.9
}}
    """

    def response_prompt(
        self,
        session: AgentSession,
        user_message: str,
        observations: list[str],
    ) -> PromptEnvelope:
        system = (
            "You are Sentinel. Answer directly, accurately, and concisely. "
            "Cite concrete findings from tool observations when relevant."
        )
        context = {
            "summary": session.summary,
            "observations": observations,
        }
        return PromptEnvelope(system=system, user=user_message, context=context)
