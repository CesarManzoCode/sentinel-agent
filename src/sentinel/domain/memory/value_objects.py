from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SalienceScore:
    value: float

    def normalized(self) -> float:
        return max(0.0, min(1.0, self.value))


@dataclass(slots=True, frozen=True)
class MemoryEmbeddingRef:
    key: str
    dimension: int


@dataclass(slots=True, frozen=True)
class MemoryScope:
    value: str


@dataclass(slots=True, frozen=True)
class TokenCost:
    value: int


@dataclass(slots=True, frozen=True)
class RecencyWeight:
    value: float
