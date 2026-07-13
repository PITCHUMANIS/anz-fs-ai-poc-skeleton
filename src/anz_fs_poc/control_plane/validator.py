from __future__ import annotations

from dataclasses import dataclass

from anz_fs_poc.models import Citation, FeeResult

# Article §5.1 item 7: output schema validation — refuse free-form when
# structure is required. For this staff-assist slice, a valid ANSWER must have
# non-empty text and at least one grounding citation, and any dollar amount in
# the answer must be backed by the deterministic fee engine (not model-invented).


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    reason: str


def validate_answer(answer: str, citations: list[Citation], fee: FeeResult | None) -> ValidationResult:
    if not answer or not answer.strip():
        return ValidationResult(False, "Empty model output.")
    if not citations:
        return ValidationResult(False, "Answer produced without grounding citations.")
    if "$" in answer or "a$" in answer.lower():
        if fee is None:
            return ValidationResult(False, "Dollar amount present without deterministic fee attribution.")
    return ValidationResult(True, "Output schema valid.")
