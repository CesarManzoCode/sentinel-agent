# Contributing

## Goals

Contributions must preserve the repository's core commitments:

- strict dependency direction: `interfaces/infrastructure -> application -> domain`
- policy-gated side effects
- Linux-first operational correctness
- maintainable Python with explicit contracts and strong typing
- durable tests for every behavior that changes

## Workflow

1. Create a focused branch.
2. Add or update tests.
3. Run `make lint typecheck test`.
4. Update docs and examples when operator behavior changes.
5. Add or update an ADR when the change affects architecture or safety posture.
6. Open a pull request using the repository template.

## Design rules

- Do not introduce infrastructure dependencies into the domain layer.
- Do not bypass the policy engine for any tool invocation.
- Do not add a new tool without:
  - a typed manifest,
  - risk classification,
  - policy coverage,
  - tests,
  - operator-facing documentation.
- Prefer explicit wiring in `bootstrap.py` over hidden dependency injection frameworks.
- Avoid adding heavy runtime dependencies without a clear operational reason.

## Tests expected in pull requests

- unit tests for changed domain or application logic
- contract tests when adding a new adapter implementation
- integration tests when wiring or persistence changes
- end-to-end tests for any new high-risk workflow

## Commit quality

Commits should be small enough to review, but large enough to preserve logical coherence. Squash fixup commits before merge.

## Security-sensitive contributions

Changes related to privilege, command execution, filesystem access, package management, or secret handling require an explicit security impact note in the pull request.
