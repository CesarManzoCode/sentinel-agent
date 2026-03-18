from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

_WHITESPACE_RE = re.compile(r"\s+")


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compact_text(text: str, max_chars: int) -> str:
    normalized = _WHITESPACE_RE.sub(" ", text.strip())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1] + "…"


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_subpath(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def chunked[T](items: Iterable[T], size: int) -> list[list[T]]:
    bucket: list[T] = []
    chunks: list[list[T]] = []
    for item in items:
        bucket.append(item)
        if len(bucket) >= size:
            chunks.append(bucket)
            bucket = []
    if bucket:
        chunks.append(bucket)
    return chunks
