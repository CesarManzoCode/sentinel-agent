# Security Policy

## Supported versions

The latest minor release on the default branch is supported for security fixes.

## Reporting a vulnerability

Please report vulnerabilities privately to the maintainers. Include:

- affected version or commit
- threat model assumptions
- reproduction steps
- expected vs actual behavior
- logs or traces with secrets removed

Do not open a public issue for active vulnerabilities.

## Threat model summary

This project assumes:

- the agent runs on a user-controlled Linux machine
- the operator may request inspection, modification, or package operations
- the LLM is fallible and must never be trusted with direct side-effect execution
- secrets may appear in prompts, file contents, tool outputs, or environment variables

### Defended risks

- accidental destructive commands
- tool execution outside user intent scope
- replay of stale approvals
- secret persistence in traces or memory
- filesystem traversal outside approved roots
- shell injection via structured command interfaces

### Explicit non-goals

- remote multi-user tenancy
- hard OS-level isolation equivalent to a virtual machine
- stealth or invisible privilege escalation
- blind autonomous action without operator accountability

## Security controls

- central policy engine
- dynamic risk classification
- exact approval tokens with expiry
- path normalization and jail enforcement
- command validation and binary deny lists
- bubblewrap support when available
- structured logs plus append-only audit sink
- redaction before persistence

## Safe defaults

- privileged execution disabled
- raw shell mode disabled
- write operations require approval unless profile explicitly relaxes policy
- package install/remove operations are high risk
- secret candidates are excluded from memory write-back
