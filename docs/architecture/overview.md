# Architecture overview

`sentinel-agent` is a modular monolith that enforces the dependency direction:

`interfaces / infrastructure -> application -> domain`

## Layers

### Domain
Framework-free business language, invariants, value objects, and ports.

### Application
Use cases, orchestration, policy flow, token budgeting, memory selection, and response synthesis.

### Infrastructure
Groq API integration, SQLite persistence, local embeddings, tooling, CLI implementation, and telemetry sinks.

### Interfaces
Inbound adapters that translate terminal interactions into use case calls and render the result.

## Request flow

1. CLI accepts a user turn.
2. Session manager loads or creates state.
3. Context builder assembles prompt context.
4. Planner requests a structured action.
5. Tool dispatcher routes tool calls through policy checks.
6. Reflection decides whether to continue or stop.
7. Responder generates the final answer.
8. Trace, summary, and memory write-back persist.
