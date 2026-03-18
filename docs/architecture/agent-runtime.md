# Agent runtime

The runtime is an explicit state machine. It never allows the model to execute side effects directly.

## Turn states

- `IDLE`
- `PLANNING`
- `WAITING_APPROVAL`
- `EXECUTING`
- `REFLECTING`
- `RESPONDING`
- `FINALIZED`
- `FAILED`

## Runtime loop

1. Build scoped context.
2. Ask the planner for a structured directive.
3. If a tool is proposed, evaluate policy and approvals.
4. Execute the tool through the dispatcher.
5. Normalize the result and append to trace.
6. Reflect and either continue, replan, or stop.
7. Produce the final answer.

## Hard controls

- max reasoning steps per turn
- max tool calls per turn
- token budgets
- wall-clock timeout
- no raw chain-of-thought persistence
