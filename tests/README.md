# Test suite

- `unit/`: pure domain and application logic
- `contract/`: adapter interface behavior
- `integration/`: wiring across real modules with test doubles
- `e2e/`: scenario flows that exercise the full stack with realistic local side effects

Tests avoid network and destructive host interaction by default. Groq integration is opt-in.
