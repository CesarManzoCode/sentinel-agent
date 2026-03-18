from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ModelCapabilities:
    model: str
    context_window: int
    supports_streaming: bool
    supports_structured_output: bool


@dataclass(slots=True, frozen=True)
class PromptEnvelope:
    system: str
    user: str
    context: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
