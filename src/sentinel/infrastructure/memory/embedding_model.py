from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass

from sentinel.domain.memory.ports import EmbeddingPort
from sentinel.infrastructure.persistence.vector.embedding_cache import EmbeddingCache
from sentinel.shared.utils import stable_hash


_TOKEN_RE = re.compile(r"[A-Za-z0-9_./:-]+")

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


@dataclass(slots=True)
class LocalEmbeddingModel(EmbeddingPort):
    dimension: int
    cache: EmbeddingCache
    model_name: str = "all-MiniLM-L6-v2"

    def __post_init__(self) -> None:
        self._model = SentenceTransformer(self.model_name) if SentenceTransformer is not None else None

    def embed(self, text: str) -> list[float]:
        cache_key = stable_hash({"model": self.model_name, "text": text})
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        vector = self._embed_transformer(text) if self._model is not None else self._embed_hash(text)
        self.cache.save(cache_key, stable_hash(text), vector)
        return vector

    def _embed_transformer(self, text: str) -> list[float]:  # pragma: no cover - optional dependency
        assert self._model is not None
        vector = self._model.encode(text, normalize_embeddings=True)
        return [float(value) for value in vector.tolist()]

    def _embed_hash(self, text: str) -> list[float]:
        counts = Counter(token.lower() for token in _TOKEN_RE.findall(text))
        vector = [0.0] * self.dimension
        if not counts:
            return vector
        for token, count in counts.items():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vector[index] += float(count)
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
