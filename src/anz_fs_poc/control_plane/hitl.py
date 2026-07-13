from __future__ import annotations

from anz_fs_poc.models import Role


def requires_hitl(outcome_hint: str | None, role: Role, policy_hitl: bool) -> bool:
    if policy_hitl:
        return True
    if outcome_hint == "hitl":
        return True
    # Team leaders may clear some drafts in a real system; agents always escalate high-consequence.
    return False


def hitl_message(reason: str) -> str:
    return (
        "This request requires human review before any customer commitment. "
        f"Reason: {reason} Draft speaking notes only after team-leader approval."
    )
