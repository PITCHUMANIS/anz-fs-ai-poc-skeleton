from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    allow_model_call: bool
    outcome_hint: str | None
    reason: str
    hitl_required: bool = False


_REFUSAL_PATTERNS: list[tuple[str, re.Pattern[str], bool]] = [
    (
        "fee_waiver",
        re.compile(r"\b(waive|waiver|write[\s-]?off)\b.*\b(fee|charge)\b|\b(fee|charge)\b.*\b(waive|waiver)\b", re.I),
        True,
    ),
    (
        "refund_or_compensation",
        re.compile(r"\b(refund|goodwill|compensation|remediat(?:e|ion))\b", re.I),
        True,
    ),
    (
        "prompt_injection",
        re.compile(r"ignore (all |any )?(previous|prior|above) instructions|reveal (the )?system prompt", re.I),
        False,
    ),
    (
        "secret_list",
        re.compile(r"\b(secret|hidden)\b.*\b(waiver|vip|internal list)\b", re.I),
        False,
    ),
]


def evaluate_policy(query: str) -> PolicyDecision:
    for name, pattern, hitl in _REFUSAL_PATTERNS:
        if pattern.search(query):
            if name in {"fee_waiver", "refund_or_compensation"}:
                return PolicyDecision(
                    allow_model_call=False,
                    outcome_hint="hitl",
                    reason=f"High-consequence request blocked by policy rule '{name}'. Requires human authority.",
                    hitl_required=True,
                )
            return PolicyDecision(
                allow_model_call=False,
                outcome_hint="refuse",
                reason=f"Request blocked by policy rule '{name}'.",
                hitl_required=False,
            )
    return PolicyDecision(allow_model_call=True, outcome_hint=None, reason="No policy block.", hitl_required=False)
