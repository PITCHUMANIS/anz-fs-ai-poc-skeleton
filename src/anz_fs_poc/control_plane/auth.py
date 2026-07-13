from __future__ import annotations

from dataclasses import dataclass

from anz_fs_poc.models import Role


ALLOWED_PURPOSES = {"staff_assist", "contact_centre_support", "training_demo"}


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: Role
    purpose: str


def authenticate(user_id: str, role: Role, purpose: str) -> Principal:
    """PoC auth stub — replace with Entra ID / SSO in a real deployment."""
    if purpose not in ALLOWED_PURPOSES:
        raise PermissionError(f"Purpose '{purpose}' is not allow-listed for this PoC.")
    return Principal(user_id=user_id, role=role, purpose=purpose)
