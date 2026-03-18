from __future__ import annotations

from dataclasses import dataclass

from sentinel.domain.llm.value_objects import ModelCapabilities


@dataclass(slots=True)
class ProviderModelCatalog:
    _models: dict[str, ModelCapabilities]

    @classmethod
    def default(cls) -> "ProviderModelCatalog":
        return cls(
            _models={
                "llama-3.3-70b-versatile": ModelCapabilities(
                    model="llama-3.3-70b-versatile",
                    context_window=128_000,
                    supports_streaming=True,
                    supports_structured_output=True,
                ),
                "llama-3.1-8b-instant": ModelCapabilities(
                    model="llama-3.1-8b-instant",
                    context_window=128_000,
                    supports_streaming=True,
                    supports_structured_output=True,
                ),
            }
        )

    def get(self, model: str) -> ModelCapabilities:
        return self._models.get(
            model,
            ModelCapabilities(
                model=model,
                context_window=32_000,
                supports_streaming=True,
                supports_structured_output=False,
            ),
        )
