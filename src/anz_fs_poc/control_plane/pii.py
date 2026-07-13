from __future__ import annotations

import re
from dataclasses import dataclass


# Illustrative patterns only — not a production PII engine. A real deployment
# would use a managed PII/NER service. Order matters: match longer, more
# specific identifiers (PAN, Medicare) before the shorter TFN pattern.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("PAN_LIKE", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("MEDICARE_LIKE", re.compile(r"\b\d{4}\s?\d{5}\s?\d(?:/\d)?\b")),
    ("TFN_LIKE", re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
]


@dataclass
class PiiResult:
    text: str
    redactions: list[str]


def redact_pii(text: str) -> PiiResult:
    redactions: list[str] = []
    cleaned = text
    for label, pattern in _PATTERNS:
        if pattern.search(cleaned):
            redactions.append(label)
            cleaned = pattern.sub(f"[REDACTED:{label}]", cleaned)
    return PiiResult(text=cleaned, redactions=redactions)
