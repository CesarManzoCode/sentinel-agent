from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.agent.entities import ChatMessage
from sentinel.shared.utils import compact_text


@dataclass(slots=True)
class ConversationCompactor:
    max_messages: int = 10
    summary_size: int = 1200

    def compact(self, messages: list[ChatMessage], previous_summary: str) -> tuple[list[ChatMessage], str]:
        if len(messages) <= self.max_messages:
            return messages, previous_summary
        older = messages[:-self.max_messages]
        retained = messages[-self.max_messages :]
        joined = " ".join(f"{message.role}: {message.content}" for message in older)
        summary = compact_text(f"{previous_summary} {joined}".strip(), self.summary_size)
        return retained, summary
