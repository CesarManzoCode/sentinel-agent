# sentinel-agent

A local-first AI agent for the terminal, designed for safe system operations, automation, and developer workflows.

Sentinel executes tasks through a structured agent runtime with strict safety controls, policy-gated tool execution, and local persistence. No cloud orchestration, hidden actions, or GUI is required.

## Overview

sentinel-agent is a Linux-first, terminal-only AI agent built as a modular monolith with Hexagonal and Clean Architecture boundaries. It targets developer tooling and local system operations rather than chat-only demos.

Core capabilities include:

- Groq-backed inference behind a provider abstraction
- An explicit agent runtime: planning → execution → reflection → response
- A universal policy gate for tool invocations
- Hybrid memory using SQLite FTS5 and an on-disk semantic index
- Structured logs, traces, audit records, and approval workflows
- CLI-first operation with no GUI or web dependency

## What Sentinel can do

- Inspect processes, logs, and environment information
- Execute terminal commands through policy enforcement
- Navigate and manipulate files within configured boundaries
- Persist and retrieve contextual memory across sessions
- Assist with debugging, diagnostics, and system workflows
- Keep execution transparent and auditable

## Design principles

- **Local-first persistence:** sessions, memories, approvals, traces, and metadata are stored locally.
- **Policy-enforced execution:** every tool call passes through a centralized policy engine.
- **Small-model efficiency:** token budgeting, memory summarization, and selective context injection.
- **Controlled extensibility:** typed tool manifests, explicit ports, and registered plugins.
- **Operational transparency:** structured logs, per-turn traces, and a durable audit trail.

## Architecture

- `src/sentinel/domain` — framework-free business logic and ports
- `src/sentinel/application` — orchestration, use cases, and runtime flow
- `src/sentinel/infrastructure` — persistence, LLM providers, CLI, and tools
- `src/sentinel/interfaces` — inbound adapters
- `docs/` — architecture, ADRs, and operational documentation
- `tests/` — unit, contract, integration, and end-to-end tests

## Supported environment

- Linux-first
- Optimized for Arch Linux and `pacman`
- Extensible package abstraction for other distributions

## Quick start

```bash
git clone https://github.com/CesarManzoCode/sentinel-agent.git
cd sentinel-agent

cp .env.example .env

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

sentinel config validate
sentinel chat
```

At minimum, configure:

```env
SENTINEL_GROQ_API_KEY=your_api_key_here
```

Optional settings include:

```env
SENTINEL_GROQ_MODEL=llama-3.3-70b-versatile
SENTINEL_PROFILE=balanced
```

## CLI commands

```bash
sentinel chat
sentinel tools
sentinel trace --last
sentinel memory search "python crash"
sentinel config validate
```

## Security model

Sentinel uses the following controls:

- Privileged operations are disabled by default.
- Structured command execution is the default mode.
- Raw shell execution is treated as high risk.
- Approvals are bound to normalized arguments and session context.
- Filesystem access is restricted to configured roots.
- Secrets are redacted before persistence.

See [SECURITY.md](SECURITY.md) and the [safety model](docs/architecture/safety-model.md) for details.

## Runtime data

Runtime artifacts are stored under `data/` by default:

- `data/sentinel.db` — primary SQLite database
- `data/logs/` — structured logs
- `data/audit/` — append-only audit log
- `data/vector/` — semantic index
- `data/cache/` — embedding cache
- `data/runtime/` — transient state

These paths are not intended for version control.

## Testing

```bash
pytest
```

Integration tests that require a Groq API key are skipped when it is not configured.

## Documentation

```bash
mkdocs serve
```

The documentation covers architecture, safety, development, operations, and ADRs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to architecture boundaries, the safety model, persistence, or the tool runtime should include an ADR update in `docs/adr/`.

## Status

Sentinel is actively developed and intended for advanced local workflows and experimentation.

## License

See [LICENSE](LICENSE).
