from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .plan_pack_validator import AUTHORITY_LOCKS
from .repo_boundary import resolve_repo_root
from .session_log import safe_slug, timestamp_utc

ORCHESTRATION_TYPE = "guardian_operated_dry_run"
ORCHESTRATION_VERSION = "v0"
HASH_ALGORITHM = "sha256"
RECEIPT_TYPE = "guardian_plan_pack_validation"
RECEIPT_VERSION = "v0"
AUTHORIZATION_PHRASE = "dry-run orchestration preparation allowed"
BOUNDARY_CONFLICT_PHRASES = (
    "dry-run orchestration forbidden",
    "orchestration forbidden",
    "guardian orchestration forbidden",
)

AUTHORITY_KEYS = tuple(AUTHORITY_LOCKS.keys())

EVIDENCE_BLOCK: dict[str, Any] = {
    "orchestration_record_only": True,
    "execution_performed": False,
    "pi_loop_invoked": False,
    "codexify_ingestion_performed": False,
    "durable_mutation_performed": False,
    "source_mutation_performed": False,
    "approval_granted": False,
}

INTENDED_ACTION: dict[str, Any] = {
    "kind": "dry_run_orchestration_preparation",
    "description": "prepare bounded dry-run orchestration record only",
}

PASS_REASON = (
    "all preconditions passed; dry-run orchestration record prepared "
    "(no execution occurred)"
)


def _resolve_safely(path: Path) -> Path | None:
    try:
        return path.expanduser().resolve()
    except (OSError, RuntimeError):
        return None


def _path_inside(child: Path, root: Path) -> bool:
    return child == root or root in child.parents


def _repo_boundary_ok(path: Path, repo_root: Path) -> bool:
    resolved = _resolve_safely(path)
    if resolved is None:
        return False
    return _path_inside(resolved, repo_root)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _empty_preconditions() -> dict[str, bool]:
    return {
        "plan_pack_exists": False,
        "receipt_exists": False,
        "receipt_type_valid": False,
        "receipt_version_valid": False,
        "receipt_validation_passed": False,
        "authority_locks_false": False,
        "evidence_flags_non_authoritative": False,
        "manifest_algorithm_sha256": False,
        "manifest_hashes_match": False,
        "authorization_allows_dry_run_orchestration": False,
        "boundaries_allow_dry_run_orchestration": False,
        "repo_boundary_valid": False,
    }


def _load_receipt(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _verify_manifest_hashes(
    plan_pack: Path, files_manifest: Any
) -> tuple[bool, dict[str, Any]]:
    hash_files: dict[str, Any] = {}
    if not isinstance(files_manifest, dict) or not files_manifest:
        return False, {"hash_algorithm": HASH_ALGORITHM, "files": hash_files}
    all_match = True
    for name, raw_entry in files_manifest.items():
        entry = raw_entry if isinstance(raw_entry, dict) else {}
        expected = entry.get("sha256")
        file_path = plan_pack / name
        actual: str | None = None
        size: int | None = None
        if file_path.is_file() and not file_path.is_symlink():
            data = file_path.read_bytes()
            actual = hashlib.sha256(data).hexdigest()
            size = len(data)
        matches = expected is not None and actual is not None and expected == actual
        if not matches:
            all_match = False
        hash_files[name] = {
            "expected_sha256": expected,
            "actual_sha256": actual,
            "matches": matches,
            "size_bytes": size,
        }
    return all_match, {"hash_algorithm": HASH_ALGORITHM, "files": hash_files}


def preflight(
    plan_pack_path: Path,
    receipt_path: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    trusted_repo_root = resolve_repo_root(repo_root)
    preconditions = _empty_preconditions()
    plan_pack = _resolve_safely(plan_pack_path)
    receipt_resolved = _resolve_safely(receipt_path)

    preconditions["repo_boundary_valid"] = bool(
        _repo_boundary_ok(plan_pack_path, trusted_repo_root)
        and _repo_boundary_ok(receipt_path, trusted_repo_root)
    )

    if plan_pack is not None and plan_pack.is_dir():
        preconditions["plan_pack_exists"] = True
    if receipt_resolved is not None and receipt_resolved.is_file():
        preconditions["receipt_exists"] = True

    receipt: dict[str, Any] = {}
    if preconditions["receipt_exists"] and receipt_resolved is not None:
        receipt = _load_receipt(receipt_resolved)

    if receipt:
        preconditions["receipt_type_valid"] = receipt.get("receipt_type") == RECEIPT_TYPE
        preconditions["receipt_version_valid"] = (
            receipt.get("receipt_version") == RECEIPT_VERSION
        )
        validation = receipt.get("validation") or {}
        preconditions["receipt_validation_passed"] = validation.get("valid") is True

        authority = receipt.get("authority") or {}
        preconditions["authority_locks_false"] = (
            isinstance(authority, dict)
            and set(authority.keys()) == set(AUTHORITY_KEYS)
            and all(value is False for value in authority.values())
        )

        evidence = receipt.get("evidence") or {}
        preconditions["evidence_flags_non_authoritative"] = (
            isinstance(evidence, dict)
            and evidence.get("approval_granted") is False
            and evidence.get("execution_performed") is False
            and evidence.get("codexify_ingestion_performed") is False
            and evidence.get("durable_mutation_performed") is False
        )

        manifest = receipt.get("plan_pack_manifest") or {}
        preconditions["manifest_algorithm_sha256"] = (
            isinstance(manifest, dict) and manifest.get("hash_algorithm") == HASH_ALGORITHM
        )

    manifest = receipt.get("plan_pack_manifest") or {} if receipt else {}
    files_manifest = manifest.get("files") if isinstance(manifest, dict) else None
    if (
        preconditions["plan_pack_exists"]
        and preconditions["manifest_algorithm_sha256"]
        and plan_pack is not None
    ):
        matches, hash_verification = _verify_manifest_hashes(plan_pack, files_manifest)
        preconditions["manifest_hashes_match"] = matches
    else:
        preconditions["manifest_hashes_match"] = False
        hash_verification = {"hash_algorithm": HASH_ALGORITHM, "files": {}}

    if preconditions["plan_pack_exists"] and plan_pack is not None:
        auth_text = _read_text(plan_pack / "AUTHORIZATION.md")
        preconditions["authorization_allows_dry_run_orchestration"] = (
            AUTHORIZATION_PHRASE in auth_text
        )
        boundary_text = _read_text(plan_pack / "BOUNDARIES.md")
        preconditions["boundaries_allow_dry_run_orchestration"] = not any(
            phrase in boundary_text for phrase in BOUNDARY_CONFLICT_PHRASES
        )

    all_passed = all(preconditions.values())
    failed = [name for name, ok in preconditions.items() if not ok]
    reason = PASS_REASON if all_passed else "preconditions failed: " + ", ".join(failed)

    return {
        "orchestration_type": ORCHESTRATION_TYPE,
        "orchestration_version": ORCHESTRATION_VERSION,
        "result": "pass" if all_passed else "fail",
        "reason": reason,
        "created_at": timestamp_utc(),
        "repo_root": str(trusted_repo_root),
        "plan_pack_path": str(plan_pack) if plan_pack else str(plan_pack_path),
        "validation_receipt_path": (
            str(receipt_resolved) if receipt_resolved else str(receipt_path)
        ),
        "preconditions": preconditions,
        "receipt_hash_verification": hash_verification,
        "authority": dict(AUTHORITY_LOCKS),
        "evidence": dict(EVIDENCE_BLOCK),
        "intended_action": dict(INTENDED_ACTION),
        "notes": "",
    }


def render_result(result: dict[str, Any]) -> str:
    lines: list[str] = []
    if result["result"] == "pass":
        lines.append("Guardian dry-run orchestration preflight: PASS")
        lines.append(f"Repository root: {result['repo_root']}")
        lines.append(f"Plan Pack: {result['plan_pack_path']}")
        lines.append(f"Validation receipt: {result['validation_receipt_path']}")
        lines.append("Hash verification: PASS")
    else:
        lines.append("Guardian dry-run orchestration preflight: FAIL")
        lines.append(f"Reason: {result['reason']}")
        failed = [name for name, ok in result["preconditions"].items() if not ok]
        lines.append("Failed checks:")
        for name in failed:
            lines.append(f"- {name}")
    lines.append(
        "Authority: no execution, no Pi Loop, no Codexify, no durable mutation"
    )
    return "\n".join(lines) + "\n"


def write_orchestration_log(
    result: dict[str, Any], *, orchestrations_dir: Path
) -> Path:
    created_at = result.get("created_at") or timestamp_utc()
    slug = safe_slug(Path(result["plan_pack_path"]).name)
    filename = f"{created_at}-guardian-operated-dry-run-{slug}.json"
    orchestrations_dir.mkdir(parents=True, exist_ok=True)
    path = orchestrations_dir / filename
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return path
