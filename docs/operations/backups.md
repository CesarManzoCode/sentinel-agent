# Backups

To back up a local installation:

1. stop active sessions
2. copy `data/sentinel.db`
3. copy `data/vector/`
4. optionally copy `data/cache/`
5. keep config files and `.env` separately and securely

SQLite WAL mode should be checkpointed before cold backups if the process is actively running.
