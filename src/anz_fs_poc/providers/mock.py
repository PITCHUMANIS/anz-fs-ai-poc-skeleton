from __future__ import annotations

from anz_fs_poc.models import Citation
from anz_fs_poc.providers.base import ModelOutput, ModelProvider, ProviderUnavailable


class MockProvider(ModelProvider):
    """Offline stand-in for a regional model endpoint."""

    def __init__(self, model_id: str = "mock-fs-assist-v1", *, unavailable: bool = False) -> None:
        self.model_id = model_id
        self.unavailable = unavailable

    def generate(
        self,
        *,
        query: str,
        citations: list[Citation],
        system_notes: list[str],
        system_prompt: str,
    ) -> ModelOutput:
        if self.unavailable:
            raise ProviderUnavailable("Mock provider forced unavailable (degraded-mode demo).")
        if not citations:
            text = (
                "I do not have enough support in the approved corpus to answer confidently. "
                "Please escalate to an SME or search the controlled knowledge base."
            )
            return ModelOutput(text=text, model_id=self.model_id)

        bullets = []
        for c in citations[:3]:
            bullets.append(f"- From {c.doc_id} § {c.section}: {c.preview}")

        notes = "\n".join(f"- {n}" for n in system_notes) if system_notes else "- None"
        text = (
            f"Staff speaking notes for: {query.strip()}\n\n"
            f"Grounded points:\n"
            + "\n".join(bullets)
            + "\n\nSystem notes:\n"
            + notes
            + "\n\nReminder: do not make customer commitments from this assistant; "
            "use HITL / team-leader authority for waivers, refunds, or remediation."
        )
        return ModelOutput(text=text, model_id=self.model_id)
