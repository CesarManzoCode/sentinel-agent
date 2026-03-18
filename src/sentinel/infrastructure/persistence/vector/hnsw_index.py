from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from sentinel.shared.utils import ensure_directory


try:  # pragma: no cover - optional dependency
    import hnswlib  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    hnswlib = None


@dataclass(slots=True)
class HNSWIndexStore:
    index_dir: Path
    dimension: int
    _vectors: dict[str, list[float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ensure_directory(self.index_dir)
        self._load()

    @property
    def _json_file(self) -> Path:
        return self.index_dir / "vectors.json"

    def _load(self) -> None:
        if self._json_file.exists():
            self._vectors = json.loads(self._json_file.read_text(encoding="utf-8"))
        else:
            self._vectors = {}

    def persist(self) -> None:
        self._json_file.write_text(json.dumps(self._vectors), encoding="utf-8")

    def add(self, key: str, vector: list[float]) -> None:
        if len(vector) != self.dimension:
            vector = (vector + [0.0] * self.dimension)[: self.dimension]
        self._vectors[key] = vector
        self.persist()

    def delete(self, key: str) -> None:
        self._vectors.pop(key, None)
        self.persist()

    def query(self, vector: list[float], limit: int) -> list[tuple[str, float]]:
        if not self._vectors:
            return []
        scores = [(key, self._cosine_similarity(vector, stored)) for key, stored in self._vectors.items()]
        return sorted(scores, key=lambda item: item[1], reverse=True)[:limit]

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)
