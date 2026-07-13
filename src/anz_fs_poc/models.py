from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Role(str, Enum):
    AGENT = "agent"
    TEAM_LEADER = "team_leader"
    ADMIN = "admin"


class Outcome(str, Enum):
    ANSWER = "answer"
    REFUSE = "refuse"
    HITL = "hitl"
    DEGRADED = "degraded"


@dataclass
class Citation:
    doc_id: str
    section: str
    preview: str
    score: float


@dataclass
class FeeResult:
    fee_code: str
    name: str
    amount_aud: float
    source: str = "deterministic_fee_engine"


@dataclass
class TraceEvent:
    step: str
    detail: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssistRequest:
    query: str
    user_id: str = "agent.demo"
    role: Role = Role.AGENT
    purpose: str = "staff_assist"


@dataclass
class AssistResponse:
    outcome: Outcome
    answer: str
    citations: list[Citation] = field(default_factory=list)
    fee: FeeResult | None = None
    hitl_required: bool = False
    redactions: list[str] = field(default_factory=list)
    model_id: str = ""
    region: str = ""
    prompt_pack_version: str = ""
    prompt_pack_hash: str = ""
    trace: list[TraceEvent] = field(default_factory=list)
    system_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["outcome"] = self.outcome.value
        return payload
