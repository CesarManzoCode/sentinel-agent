sentinel-agent
A local-first AI agent for the terminal — designed for safe system operations, automation, and developer workflows.

Sentinel executes tasks through a structured agent runtime with strict safety controls, policy-gated tool execution, and fully local persistence.

No cloud orchestration. No hidden actions. Full control.

Overview
sentinel-agent is a Linux-first, terminal-only AI agent built as a modular monolith with strict Hexagonal and Clean Architecture boundaries.

It is designed for serious developer tooling and local system operations — not chat demos.

Core capabilities include:

Groq-backed inference behind a provider abstraction

Explicit agent runtime (planning → execution → reflection → response)

Universal policy gate for all tool invocations

Hybrid memory (SQLite FTS5 + on-disk semantic index)

Structured logs, traces, audit records, and approval workflows

CLI-first operation with no GUI or web dependencies

What can Sentinel do?
Inspect your system (processes, logs, environment variables)

Safely execute terminal commands with policy enforcement

Navigate and manipulate files within controlled boundaries

Persist and retrieve contextual memory across sessions

Assist with debugging, diagnostics, and system-level workflows

Provide transparent, auditable execution of all actions

Why Sentinel?
Most AI agents prioritize convenience over control.

Sentinel is built differently:

Local-first by default — your data never leaves your machine

Policy-enforced execution — every side effect is explicitly gated

Auditable runtime — all actions are traceable and inspectable

Deterministic structure — no hidden chains or opaque behaviors

Built for real work — system interaction, not just conversation

Architecture
The repository follows a strict layered architecture:

src/sentinel/domain — framework-free business logic and ports

src/sentinel/application — orchestration, use cases, and runtime flow

src/sentinel/infrastructure — persistence, LLM providers, CLI, tools

src/sentinel/interfaces — inbound adapters (CLI controllers/presenters)

docs/ — architecture, ADRs, and operational documentation

tests/ — unit, contract, integration, and end-to-end tests

This separation enforces clear boundaries, testability, and long-term maintainability.

Core Design Principles
Local-first persistence
All sessions, memories, approvals, traces, and metadata are stored locally.

Policy-enforced execution
Every tool call passes through a centralized policy engine.

Small-model efficiency
Token budgeting, memory summarization, and selective context injection.

Extensibility without chaos
Typed tool manifests, explicit ports, and controlled plugin registration.

Operational transparency
Structured logs, per-turn traces, and a durable audit trail.

Supported Environment
Linux-first (primary target)

Optimized for Arch Linux (pacman)

Extensible package abstraction for other distributions

Quick Start
git clone https://github.com/your-username/sentinel-agent
cd sentinel-agent

cp .env.example .env

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

sentinel config validate
sentinel chat
Required Environment Variables
At minimum:

SENTINEL_GROQ_API_KEY=your_api_key_here
Optional:

SENTINEL_GROQ_MODEL=llama-3.3-70b-versatile
SENTINEL_PROFILE=balanced
CLI Commands
sentinel chat
sentinel tools
sentinel trace --last
sentinel memory search "python crash"
sentinel config validate
Security Model
Sentinel enforces a strict safety posture:

Privileged operations are disabled by default

Structured command execution is the default mode

Raw shell execution is treated as high risk

Approvals are bound to normalized arguments and session context

Filesystem access is restricted to configured roots

Secret redaction is applied before persistence

For full details:

SECURITY.md

docs/architecture/safety-model.md

Runtime Data
By default, runtime artifacts are stored locally under data/:

data/sentinel.db — primary SQLite database

data/logs/ — structured logs

data/audit/ — append-only audit log

data/vector/ — semantic index

data/cache/ — embedding cache

data/runtime/ — transient state

These files are not intended for version control.

Testing
Run all tests:

pytest
Notes:

Integration tests requiring a Groq API key are skipped automatically if not configured

The test suite includes unit, contract, integration, and end-to-end coverage

Documentation
Serve documentation locally:

mkdocs serve
Documentation includes:

Architecture breakdown

Safety model

Development guides

Operational practices

Architectural Decision Records (ADRs)

Contributing
See CONTRIBUTING.md.

Changes affecting:

architecture boundaries

safety model

persistence

tool runtime

should include an ADR update in docs/adr/.

Status
Sentinel is an actively developed project focused on building a robust, local-first AI agent runtime.

The current version is stable enough for advanced local workflows and experimentation, with ongoing improvements in tool coverage, safety enforcement, and developer ergonomics.

License
See LICENSE.