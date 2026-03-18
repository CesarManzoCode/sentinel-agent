from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ApprovalToken:
    value: str


@dataclass(slots=True, frozen=True)
class RiskFactors:
    values: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class DenialReason:
    value: str


@dataclass(slots=True, frozen=True)
class RedactionRuleSet:
    mask_env_values: bool = True
    mask_long_hex_tokens: bool = True
    mask_urls_with_credentials: bool = True
