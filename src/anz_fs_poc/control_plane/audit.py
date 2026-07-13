from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from anz_fs_poc.models import AssistRequest, AssistResponse


class AuditLogger:
    def __init__(self, audit_dir: Path) -> None:
        self.audit_dir = audit_dir
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        request: AssistRequest,
        response: AssistResponse,
        *,
        redacted_query: str,
    ) -> Path:
        # Data minimisation (article §11): never persist the raw query, which may
        # contain PII. Store the redacted form plus which redactions fired.
        record = {
            "id": str(uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "request": {
                "query_redacted": redacted_query,
                "redactions": list(response.redactions),
                "user_id": request.user_id,
                "role": request.role.value,
                "purpose": request.purpose,
            },
            "steering": {
                "model_id": response.model_id,
                "region": response.region,
                "prompt_pack_version": response.prompt_pack_version,
                "prompt_pack_hash": response.prompt_pack_hash,
            },
            # Reviewer action is populated by the HITL workflow in a real system;
            # null here means "not yet reviewed".
            "reviewer_action": None,
            "response": response.to_dict(),
        }
        # Tamper-evidence: record a content hash so later edits are detectable.
        record["integrity_sha256"] = hashlib.sha256(
            json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        path = self.audit_dir / f"{record['id']}.json"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return path
