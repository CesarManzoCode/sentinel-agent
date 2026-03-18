from __future__ import annotations


class SentinelError(Exception):
    """Base exception for the project."""


class PolicyViolation(SentinelError):
    pass


class InvalidToolInvocation(SentinelError):
    pass


class MemoryConflict(SentinelError):
    pass


class BudgetExceeded(SentinelError):
    pass


class ApprovalRequired(SentinelError):
    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


class StructuredOutputError(SentinelError):
    pass


class ConfigurationError(SentinelError):
    pass


class PersistenceError(SentinelError):
    pass
