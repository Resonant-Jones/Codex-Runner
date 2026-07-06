from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .session_log import safe_slug, timestamp_utc

RECEIPT_TYPE = "guardian_dry_run_orchestration"
RECEIPT_VERSION = "v0"


def _validation_receipt_digest(path: Path) -> dict[str, Any]:
    # An orchestration receipt records a preflight outcome. It is not approval,
    # not dispatch, not Pi Loop invocation authority, not execution proof, and
    # not Codexify ingestion. The validation-receipt hash proves receipt file
    # continuity, not receipt correctness.
    try:
        data = path.read_bytes()
    except OSError:
        return {"path": str(path), "sha256": None, "size_bytes": None}
    return {
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def build_orchestration_receipt_payload(
    result: dict[str, Any],
    *,
    orchestration_log_path: Path | None,
) -> dict[str, Any]:
    validation_receipt_path = Path(result["validation_receipt_path"])
    evidence = dict(result["evidence"])
    evidence["orchestration_receipt_only"] = True
    evidence["dispatch_performed"] = False
    evidence["merge_performed"] = False
    return {
        "receipt_type": RECEIPT_TYPE,
        "receipt_version": RECEIPT_VERSION,
        "created_at": timestamp_utc(),
        "orchestration_type": result["orchestration_type"],
        "orchestration_version": result["orchestration_version"],
        "result": result["result"],
        "reason": result["reason"],
        "plan_pack_path": result["plan_pack_path"],
        "validation_receipt_path": result["validation_receipt_path"],
        "orchestration_log_path": (
            str(orchestration_log_path) if orchestration_log_path else None
        ),
        "preconditions": dict(result["preconditions"]),
        "receipt_hash_verification": dict(result["receipt_hash_verification"]),
        "authority": dict(result["authority"]),
        "evidence": evidence,
        "inputs": {
            "validation_receipt": _validation_receipt_digest(
                validation_receipt_path
            ),
            "plan_pack_manifest": dict(result["receipt_hash_verification"]),
        },
        "intended_action": dict(result["intended_action"]),
        "notes": "",
    }


def write_orchestration_receipt(
    result: dict[str, Any],
    *,
    orchestration_log_path: Path | None,
    receipts_dir: Path,
) -> Path:
    payload = build_orchestration_receipt_payload(
        result, orchestration_log_path=orchestration_log_path
    )
    created_at = payload["created_at"]
    slug = safe_slug(Path(result["plan_pack_path"]).name)
    filename = f"{created_at}-guardian-operated-dry-run-receipt-{slug}.json"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / filename
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
