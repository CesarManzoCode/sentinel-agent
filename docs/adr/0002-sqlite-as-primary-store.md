# ADR 0002: SQLite as primary store

## Status
Accepted

## Decision
Use SQLite in WAL mode as the primary persistent store.

## Rationale
SQLite provides local durability, transactions, backup simplicity, and low operational overhead for a single-user Linux application.

## Consequences
- repositories are implemented against SQLite
- migrations remain local and lightweight
- no external database service is required
