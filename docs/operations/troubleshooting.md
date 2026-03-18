# Troubleshooting

## Groq authentication errors
Validate `SENTINEL_GROQ_API_KEY` and run `sentinel config validate`.

## Vector index issues
Delete the vector index directory and run a memory reindex operation.

## Tool blocked by policy
Inspect `sentinel trace --last` and review the policy decision plus capability scope.

## Slow prompts
Reduce `memory.top_k`, use the `safe` or `minimal` profile, and inspect the token budget trace.
