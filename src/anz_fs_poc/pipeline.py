from __future__ import annotations

from anz_fs_poc.config import Settings, get_settings
from anz_fs_poc.control_plane.audit import AuditLogger
from anz_fs_poc.control_plane.auth import authenticate
from anz_fs_poc.control_plane.hitl import hitl_message, requires_hitl
from anz_fs_poc.control_plane.pii import redact_pii
from anz_fs_poc.control_plane.policy import evaluate_policy
from anz_fs_poc.control_plane.validator import validate_answer
from anz_fs_poc.deterministic.fees import lookup_fee
from anz_fs_poc.models import AssistRequest, AssistResponse, Outcome, TraceEvent
from anz_fs_poc.prompt_pack import get_prompt_pack
from anz_fs_poc.providers import get_provider
from anz_fs_poc.providers.base import ProviderUnavailable
from anz_fs_poc.rag.corpus import load_corpus
from anz_fs_poc.rag.retriever import retrieve


class AssistPipeline:
    """Thin vertical slice of the article §5 control-plane sequence."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.chunks = load_corpus(self.settings.corpus_dir)
        self.provider = get_provider(self.settings)
        self.audit = AuditLogger(self.settings.audit_dir)
        self.prompt_pack = get_prompt_pack()

    def _base_kwargs(self) -> dict:
        return {
            "model_id": self.settings.model_id,
            "region": self.settings.region,
            "prompt_pack_version": self.prompt_pack.version,
            "prompt_pack_hash": self.prompt_pack.hash,
        }

    def _finalise(
        self,
        request: AssistRequest,
        response: AssistResponse,
        redacted_query: str,
        *,
        persist_audit: bool,
    ) -> AssistResponse:
        if persist_audit:
            self.audit.write(request, response, redacted_query=redacted_query)
        return response

    def run(self, request: AssistRequest, *, persist_audit: bool = True) -> AssistResponse:
        trace: list[TraceEvent] = []

        # Redact before anything is logged or sent, so no downstream step sees raw PII.
        pii = redact_pii(request.query)

        # Auth denial should be a clean, audited refusal — not an unhandled crash.
        try:
            principal = authenticate(request.user_id, request.role, request.purpose)
        except PermissionError as exc:
            trace.append(TraceEvent(step="auth", detail="Authentication/purpose denied", data={"error": str(exc)}))
            response = AssistResponse(
                outcome=Outcome.REFUSE,
                answer=f"Access denied: {exc}",
                redactions=pii.redactions,
                trace=trace,
                system_notes=["Request refused at authentication/purpose check."],
                **self._base_kwargs(),
            )
            return self._finalise(request, response, pii.text, persist_audit=persist_audit)

        trace.append(TraceEvent(step="auth", detail="Authenticated principal", data={"user_id": principal.user_id, "role": principal.role.value}))
        trace.append(TraceEvent(step="pii", detail="PII redaction applied", data={"redactions": pii.redactions}))

        policy = evaluate_policy(pii.text)
        trace.append(TraceEvent(step="policy", detail=policy.reason, data={"allow_model_call": policy.allow_model_call}))

        if not policy.allow_model_call:
            hitl = requires_hitl(policy.outcome_hint, request.role, policy.hitl_required)
            outcome = Outcome.HITL if hitl else Outcome.REFUSE
            answer = hitl_message(policy.reason) if hitl else policy.reason
            response = AssistResponse(
                outcome=outcome,
                answer=answer,
                hitl_required=hitl,
                redactions=pii.redactions,
                trace=trace,
                system_notes=["Model call skipped due to policy."],
                **self._base_kwargs(),
            )
            return self._finalise(request, response, pii.text, persist_audit=persist_audit)

        citations = retrieve(
            pii.text,
            self.chunks,
            min_score=self.settings.min_retrieval_score,
        )
        trace.append(
            TraceEvent(
                step="retrieve",
                detail="Approved-corpus retrieval",
                data={"hit_count": len(citations), "doc_ids": [c.doc_id for c in citations]},
            )
        )

        if not citations:
            response = AssistResponse(
                outcome=Outcome.REFUSE,
                answer=(
                    "No approved source found with sufficient support. "
                    "Escalate to an SME or search the controlled knowledge base."
                ),
                redactions=pii.redactions,
                trace=trace,
                system_notes=["Insufficient retrieval support — refused (§6.3 'I don't know' path)."],
                **self._base_kwargs(),
            )
            return self._finalise(request, response, pii.text, persist_audit=persist_audit)

        fee = lookup_fee(pii.text)
        system_notes: list[str] = []
        if fee:
            system_notes.append(
                f"Used deterministic fee engine for {fee.fee_code}: A${fee.amount_aud:.2f} (not LLM-inferred)."
            )
        system_notes.append(f"Inference path: provider={self.settings.provider}, region={self.settings.region}.")

        # Degraded mode (§5.1 item 10): if the model endpoint is unavailable, the
        # process must still return something safe and defensible.
        try:
            model_out = self.provider.generate(
                query=pii.text,
                citations=citations,
                system_notes=system_notes,
                system_prompt=self.prompt_pack.system_prompt,
            )
        except ProviderUnavailable as exc:
            trace.append(TraceEvent(step="degraded", detail="Provider unavailable", data={"error": str(exc)}))
            degraded_answer = (
                "The assistant is temporarily unavailable. Use the cited approved sources directly "
                "and follow standard procedure; escalate to a team leader if needed."
            )
            if fee:
                degraded_answer += f"\n\nAuthoritative fee ({fee.fee_code}): A${fee.amount_aud:.2f} — {fee.name}."
            response = AssistResponse(
                outcome=Outcome.DEGRADED,
                answer=degraded_answer,
                citations=citations,
                fee=fee,
                redactions=pii.redactions,
                trace=trace,
                system_notes=system_notes + ["Degraded mode: served citations without model generation."],
                **self._base_kwargs(),
            )
            return self._finalise(request, response, pii.text, persist_audit=persist_audit)

        trace.append(TraceEvent(step="model", detail="Provider generation complete", data={"model_id": model_out.model_id}))

        answer = model_out.text
        if fee:
            answer += f"\n\nAuthoritative fee ({fee.fee_code}): A${fee.amount_aud:.2f} — {fee.name}."

        # Output schema validation (§5.1 item 7): refuse rather than emit unstructured/ungrounded output.
        validation = validate_answer(answer, citations, fee)
        trace.append(TraceEvent(step="validate", detail=validation.reason, data={"valid": validation.valid}))
        if not validation.valid:
            response = AssistResponse(
                outcome=Outcome.REFUSE,
                answer=(
                    "The drafted response failed output validation and was withheld. "
                    "Escalate to an SME."
                ),
                citations=citations,
                redactions=pii.redactions,
                trace=trace,
                system_notes=system_notes + [f"Output validation failed: {validation.reason}"],
                **self._base_kwargs(),
            )
            return self._finalise(request, response, pii.text, persist_audit=persist_audit)

        response = AssistResponse(
            outcome=Outcome.ANSWER,
            answer=answer,
            citations=citations,
            fee=fee,
            hitl_required=False,
            redactions=pii.redactions,
            trace=trace,
            system_notes=system_notes,
            **self._base_kwargs(),
        )
        return self._finalise(request, response, pii.text, persist_audit=persist_audit)
