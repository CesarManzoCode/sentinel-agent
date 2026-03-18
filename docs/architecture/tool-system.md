# Tool system

Tools are declared as typed adapters with manifests.

## Manifest fields

- name
- description
- category
- argument schema
- side-effect profile
- baseline risk
- timeout
- concurrency safety
- approval policy

## Built-in tool families

- terminal execution
- filesystem navigation, reading, writing
- system inspection
- internet search and fetch
- package management

## Execution lifecycle

1. planner emits a tool proposal
2. arguments bind and validate
3. capability scope checks relevance to user intent
4. risk evaluator assigns dynamic risk
5. approval service checks exact-match approval
6. adapter executes under controlled runtime
7. result normalizer produces the standard envelope
8. trace and audit records persist
