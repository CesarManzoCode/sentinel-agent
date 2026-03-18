# Safety model

Every tool invocation is gated by the policy engine.

## Risk classes

- low: read-only actions in approved scope
- medium: bounded writes or sensitive reads
- high: destructive or system-wide effects

## Key controls

- capability scope derived from user intent
- exact approval token binding
- path normalization and jail enforcement
- structured command validation
- secret redaction before persistence
- privilege escalation disabled by default

## Approval rules

Approvals are bound to:

- session id
- tool name
- normalized arguments hash
- target resources
- expiry time

This prevents broad approval replay.
