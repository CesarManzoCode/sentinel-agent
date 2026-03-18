# Testing

The test suite is organized as:

- unit: pure domain and application logic
- contract: provider, repository, and tool adapter contracts
- integration: real wiring with local test doubles
- e2e: scenario-driven sessions

Groq integration tests are opt-in and require a real API key.
