# ADR 0003: hybrid memory retrieval

## Status
Accepted

## Decision
Use lexical retrieval through SQLite FTS5 and semantic retrieval through an on-disk vector index.

## Rationale
Tool-oriented agents need exact matching for filenames, commands, packages, and errors, while still benefiting from semantic recall.

## Consequences
- memory indexing includes text and embeddings
- retrieval uses fusion rather than a single ranking source
- prompt packaging remains token-budgeted
