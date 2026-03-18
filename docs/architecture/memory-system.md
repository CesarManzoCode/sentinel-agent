# Memory system

The memory subsystem is optimized for smaller context windows.

## Tiers

- working memory: current turn and session summary
- long-term memory: durable records across sessions
- retrieval memory: selected subset injected into prompts

## Retrieval strategy

1. lexical retrieval using SQLite FTS5
2. semantic retrieval using on-disk vector index
3. reciprocal rank fusion
4. recency and salience reweighting
5. token-budgeted packaging

## Write-back

At session boundaries, the system:

- compacts old turns
- extracts episodic and preference candidates
- removes duplicates and secret-bearing content
- updates salience
- persists memory and vector index
