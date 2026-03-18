# ADR 0001: modular monolith

## Status
Accepted

## Decision
Use a modular monolith with strict layer boundaries instead of microservices.

## Rationale
The product is a local-first single-user system. Microservices would add deployment, debugging, and operational complexity without material benefit.

## Consequences
- explicit module boundaries remain mandatory
- extraction is possible later if justified
- the repository stays easy to run locally
