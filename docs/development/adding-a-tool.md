# Adding a tool

A new tool must provide:

- a typed `ToolSpec`
- an adapter implementing `ToolAdapterPort`
- a baseline risk and side-effect profile
- policy tests
- adapter contract tests
- documentation and examples

Do not place safety logic only inside the adapter. Adapter-level validation complements but never replaces the central policy engine.
