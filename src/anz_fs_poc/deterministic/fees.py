from __future__ import annotations

from anz_fs_poc.models import FeeResult

# Authoritative PoC fee table — amounts must NOT be LLM-inferred.
_FEES: dict[str, FeeResult] = {
    "HL_STD_ANNUAL": FeeResult(
        fee_code="HL_STD_ANNUAL",
        name="Home Loan Standard — annual package fee",
        amount_aud=395.00,
    ),
}


def lookup_fee(query: str) -> FeeResult | None:
    q = query.lower()
    if "annual" in q and ("fee" in q or "charge" in q) and ("home loan" in q or "standard" in q):
        return _FEES["HL_STD_ANNUAL"]
    if "hl_std_annual" in q or "package fee" in q:
        return _FEES["HL_STD_ANNUAL"]
    return None


def get_fee(fee_code: str) -> FeeResult | None:
    return _FEES.get(fee_code)
