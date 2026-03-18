# ADR 0004: policy-gated tool execution

## Status
Accepted

## Decision
Every tool invocation must pass through a central policy engine.

## Rationale
Safety logic scattered across tools becomes inconsistent and brittle. A single policy gate is easier to test, audit, and evolve.

## Consequences
- no bypass path exists for side effects
- approvals are standardized
- risk classification remains centrally enforced
