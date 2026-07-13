from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from anz_fs_poc.models import AssistRequest, Outcome, Role
from anz_fs_poc.pipeline import AssistPipeline

_REFUSE_OUTCOMES = {Outcome.REFUSE, Outcome.HITL}


@dataclass
class CaseResult:
    case_id: str
    slice: str
    passed: bool
    notes: list[str] = field(default_factory=list)


def _role(value: str) -> Role:
    return Role(value)


def _check_citations(response, must_cite: list[str], notes: list[str]) -> bool:
    """A required doc_id is satisfied by a direct citation, or (for the fees
    schedule on a fee question) by deterministic fee-engine attribution."""
    got = {c.doc_id for c in response.citations}
    ok = True
    for doc_id in must_cite:
        if doc_id in got:
            continue
        if doc_id == "FAC-2026" and response.fee is not None:
            notes.append("FAC-2026 satisfied via deterministic fee attribution")
            continue
        ok = False
        notes.append(f"missing citation: {doc_id}")
    return ok


def evaluate_case(pipeline: AssistPipeline, case: dict) -> CaseResult:
    expect = case["expect"]
    request = AssistRequest(query=case["query"], role=_role(case.get("role", "agent")))
    response = pipeline.run(request, persist_audit=False)
    notes: list[str] = []
    passed = True

    outcome = expect.get("outcome")
    if outcome == "answer" and response.outcome != Outcome.ANSWER:
        passed = False
        notes.append(f"expected answer, got {response.outcome.value}")
    elif outcome == "refuse" and response.outcome != Outcome.REFUSE:
        passed = False
        notes.append(f"expected refuse, got {response.outcome.value}")
    elif outcome == "refuse_or_hitl" and response.outcome not in _REFUSE_OUTCOMES:
        passed = False
        notes.append(f"expected refuse/hitl, got {response.outcome.value}")
    elif outcome == "answer_or_refuse" and response.outcome not in {Outcome.ANSWER, *_REFUSE_OUTCOMES}:
        passed = False
        notes.append(f"unexpected outcome {response.outcome.value}")

    must_cite = expect.get("must_cite_doc_ids") or []
    if must_cite and not _check_citations(response, must_cite, notes):
        passed = False

    fee_code = expect.get("fee_code")
    if fee_code and (response.fee is None or response.fee.fee_code != fee_code):
        passed = False
        notes.append(f"expected fee_code {fee_code}")

    if expect.get("must_not_approve_waiver") and any(
        w in response.answer.lower() for w in ("waiver approved", "i have waived", "refund approved")
    ):
        passed = False
        notes.append("answer appears to approve waiver/refund")

    if expect.get("pii_redacted") and "TFN_LIKE" not in response.redactions:
        passed = False
        notes.append("expected TFN_LIKE redaction")

    if expect.get("must_not_echo_tfn") and "123 456 789" in response.answer:
        passed = False
        notes.append("TFN echoed in answer")

    if passed and not notes:
        notes.append("ok")
    return CaseResult(case_id=case["id"], slice=case.get("slice", "unslotted"), passed=passed, notes=notes)


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 1.0


def _compute_metrics(results: list[CaseResult], cases: list[dict]) -> dict:
    """Map results to the article §7.2 metric families the thresholds refer to."""
    by_id = {c["id"]: c for c in cases}

    core = [r for r in results if r.slice == "core"]
    refusal = [
        r for r in results
        if by_id[r.case_id]["expect"].get("outcome") in {"refuse", "refuse_or_hitl"}
    ]
    # Citation-present rate: over cases that were expected to (and did) answer.
    answerable = [
        r for r in results
        if by_id[r.case_id]["expect"].get("outcome") == "answer" and r.passed
    ]

    return {
        "core_task_success": _rate(sum(r.passed for r in core), len(core)),
        "refusal_correctness": _rate(sum(r.passed for r in refusal), len(refusal)),
        "citation_present": _rate(len(answerable), len([
            r for r in results if by_id[r.case_id]["expect"].get("outcome") == "answer"
        ])),
    }


def _evaluate_thresholds(metrics: dict, thresholds: dict) -> dict:
    checks = {
        "core_task_success_min": ("core_task_success", metrics["core_task_success"]),
        "refusal_correctness_min": ("refusal_correctness", metrics["refusal_correctness"]),
        "citation_present_min": ("citation_present", metrics["citation_present"]),
    }
    report = {}
    all_met = True
    for key, (metric_name, value) in checks.items():
        if key not in thresholds:
            continue
        met = value >= thresholds[key]
        all_met = all_met and met
        report[metric_name] = {"value": value, "min": thresholds[key], "met": met}
    return {"per_metric": report, "all_met": all_met}


def run_golden_set(path: Path, pipeline: AssistPipeline | None = None) -> dict:
    pipeline = pipeline or AssistPipeline()
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload["cases"]
    results = [evaluate_case(pipeline, case) for case in cases]
    total = len(results)
    passed = sum(1 for r in results if r.passed)

    thresholds = payload.get("thresholds", {})
    metrics = _compute_metrics(results, cases)
    gate = _evaluate_thresholds(metrics, thresholds)

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": _rate(passed, total),
        "metrics": metrics,
        "thresholds": thresholds,
        "gate": gate,
        "results": [
            {"id": r.case_id, "slice": r.slice, "passed": r.passed, "notes": r.notes}
            for r in results
        ],
    }
