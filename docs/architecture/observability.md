# Observability

The system uses structured logs, traces, audit events, and metrics.

## Logs

- console logs are human-readable
- file logs are JSON
- session and trace identifiers are attached where possible
- secrets are redacted before persistence

## Traces

Each user turn produces a trace with events for:

- planning
- policy decisions
- tool execution
- reflection
- final response

## Metrics

The telemetry subsystem records:

- LLM latency
- tool latency
- token usage
- approval frequency
- policy denials
- retrieval hit counts
