# Logging

The runtime emits:

- human logs to stderr/stdout
- JSON logs to `data/logs/app.log`
- append-only audit logs to `data/audit/audit.log`

Sensitive values are redacted before persistence. Debug mode increases decision visibility but does not print hidden reasoning verbatim.
