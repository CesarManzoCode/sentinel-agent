# LLM layer

The application depends on an `LLMPort` abstraction. The first provider implementation targets Groq.

## Responsibilities

- generate text
- stream incremental tokens
- generate structured JSON envelopes
- report usage metadata
- retry transient failures

## Prompt composition

Prompts are assembled from:

- system policy
- user turn
- session summary
- retrieval memory pack
- enabled tool manifests
- schema requirements

## Structured output

Critical outputs are validated against expected JSON shapes. Invalid responses can trigger one bounded repair attempt.
