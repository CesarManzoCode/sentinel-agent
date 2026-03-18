# SQLite migrations

This repository keeps the local schema intentionally lightweight.

The application bootstraps the initial schema automatically through `DatabaseManager.initialize()`.
The files in `versions/` document the schema evolution history and support future external migration tooling if needed.
