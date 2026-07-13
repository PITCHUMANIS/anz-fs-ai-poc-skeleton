from __future__ import annotations

import hashlib
from dataclasses import dataclass

# Article §10.2: version everything that steers behaviour, and record which
# version produced which eval scores. The hash lets an auditor prove that the
# system prompt in an audit record matches a known, reviewed prompt pack.

SYSTEM_PROMPT = (
    "You are a staff-facing assistant for a retail bank. "
    "Answer only from the approved sources provided, and cite them. "
    "Use the deterministic fee engine for any dollar amounts; never invent fees, "
    "rates, or dates. Never make a customer commitment (waiver, refund, "
    "remediation, or personal financial advice) — route those to a human. "
    "If the approved sources do not support an answer, say you do not know and "
    "escalate rather than guessing."
)

PROMPT_PACK_VERSION = "2026.07.1"


@dataclass(frozen=True)
class PromptPack:
    version: str
    system_prompt: str

    @property
    def hash(self) -> str:
        digest = hashlib.sha256(f"{self.version}\n{self.system_prompt}".encode("utf-8"))
        return digest.hexdigest()[:16]


def get_prompt_pack() -> PromptPack:
    return PromptPack(version=PROMPT_PACK_VERSION, system_prompt=SYSTEM_PROMPT)
