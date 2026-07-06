from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .plan_pack_validator import AUTHORITY_LOCKS, GuardianPlanPackReport
from .session_log import safe_slug, timestamp_utc

RECEIPT_TYPE = "guardian_plan_pack_validation"
RECEIPT_VERSION = "v0"
EVIDENCE_SOURCE = "guardian_plan_pack_validator"
EVIDENCE_GENERATED_BY = "codexrun guardian validate-plan-pack"
MANIFEST_HASH_ALGORITHM = "sha256"


def _required_file_entry(path: Path) -> dict[str, Any]:
    # Manifest hashes strengthen evidence integrity. They do not approve the
    # plan, make Guardian operational, or mutate durable state. Only genuine
    # regular files are hashed; symlinks are treated conservatively as
    # not-present so an unsafe link can never pull bytes from outside the plan
    # pack into the digest. Bytes are hashed exactly as stored (no line-ending
    # normalization).
    if path.is_symlink() or not path.is_file():
        return {"present": False, "sha256": None, "size_bytes": None}
    data = path.read_bytes()
    return {
        "present": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def build_receipt_payload(
    report: GuardianPlanPackReport,
    *,
    command: str,
    created_at: str,
    notes: str = "",
) -> dict[str, Any]:
    validator_json = report.to_json_dict()
    return {
        "receipt_type": RECEIPT_TYPE,
        "receipt_version": RECEIPT_VERSION,
        "created_at": created_at,
        "plan_pack_path": str(report.plan_pack_path),
        "plan_pack_name": report.plan_pack_path.name,
        "command": command,
        "validation": {
            "valid": report.valid,
            "result": report.result,
            "reason": report.reason,
        },
        "report": {
            "required_files": validator_json["required_files"],
            "boundary_checks": validator_json["boundary_checks"],
            "task_spec": validator_json["task_spec"],
            "escalation": validator_json["escalation"],
            "issues": validator_json["issues"],
        },
        "authority": dict(AUTHORITY_LOCKS),
        "evidence": {
            "source": EVIDENCE_SOURCE,
            "generated_by": EVIDENCE_GENERATED_BY,
            "evidence_not_authority": True,
            "approval_granted": False,
            "execution_performed": False,
            "codexify_ingestion_performed": False,
            "durable_mutation_performed": False,
        },
        "plan_pack_manifest": {
            "hash_algorithm": MANIFEST_HASH_ALGORITHM,
            "files": {
                name: _required_file_entry(report.plan_pack_path / name)
                for name in report.required_files
            },
        },
        "notes": notes,
    }


def write_receipt(
    report: GuardianPlanPackReport,
    *,
    command: str,
    receipts_dir: Path,
    notes: str = "",
) -> Path:
    created_at = timestamp_utc()
    payload = build_receipt_payload(
        report, command=command, created_at=created_at, notes=notes
    )
    slug = safe_slug(report.plan_pack_path.name)
    filename = f"{created_at}-plan-pack-validation-{slug}.json"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / filename
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
