from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class SessionId:
    value: str

    @classmethod
    def new(cls) -> "SessionId":
        return cls(value=f"sess_{uuid4().hex}")

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True, frozen=True)
class TraceId:
    value: str

    @classmethod
    def new(cls) -> "TraceId":
        return cls(value=f"trc_{uuid4().hex}")

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True, frozen=True)
class MemoryId:
    value: str

    @classmethod
    def new(cls) -> "MemoryId":
        return cls(value=f"mem_{uuid4().hex}")

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True, frozen=True)
class InvocationId:
    value: str

    @classmethod
    def new(cls) -> "InvocationId":
        return cls(value=f"inv_{uuid4().hex}")

    def __str__(self) -> str:
        return self.value
