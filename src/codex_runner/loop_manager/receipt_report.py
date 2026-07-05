from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .contracts import (
    LoopManagerError,
    LoopReceipt,
    RECEIPT_VERSION_V0,
    RECEIPT_VERSION_V1,
    V1LoopReceipt,
    load_receipt_payload,
)

V0_MISSING_PROOF_FIELDS = [
    "attempt_id",
    "explicit receipt_ref",
    "structured validation outputs",
    "per-criterion acceptance results",
    "reviewer_decision",
    "actual changed-file semantics",
]


@dataclass(slots=True)
class ReceiptReport:
    receipt_path: str
    version: str
    schema_valid: bool
    mode: str
    evidence_posture: str
    trust_level: str
    actionability: str
    authority_warnings: list[str] = field(default_factory=list)
    missing_proof_fields: list[str] = field(default_factory=list)
    operator_review_triggers: list[str] = field(default_factory=list)
    lifecycle_mutation_allowed: bool = False
    ingestion_allowed: bool = False
    operator_review_required: bool = True
    codexify_ingestion_readiness: str = "blocked"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["receipt_version"] = payload.pop("version")
        payload["operator_review_required_fields"] = list(
            self.operator_review_triggers
        )
        payload["durable_action_allowed"] = False
        payload["ingestion_performed"] = False
        return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pi Loop receipt compatibility report"
    )
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON report output",
    )
    return parser


def _load_raw_receipt(receipt_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LoopManagerError(f"receipt file not found: {receipt_path}") from exc
    except json.JSONDecodeError as exc:
        raise LoopManagerError(f"invalid receipt JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise LoopManagerError("receipt payload must decode to an object")
    return payload


def detect_receipt_version(payload: dict[str, Any]) -> str:
    version = payload.get("receipt_version")
    if version is None:
        return "unknown"
    return str(version).strip() or "unknown"


def classify_receipt(receipt_path: Path) -> ReceiptReport:
    report = ReceiptReport(
        receipt_path=str(receipt_path),
        version="unknown",
        schema_valid=False,
        mode="unknown",
        evidence_posture="unknown",
        trust_level="unknown",
        actionability="review_required",
        operator_review_required=True,
        codexify_ingestion_readiness="blocked",
        reason="Receipt could not be classified yet.",
    )
    try:
        raw_payload = _load_raw_receipt(receipt_path)
    except LoopManagerError as exc:
        report.operator_review_triggers.append(str(exc))
        report.reason = f"Schema validation failed: {exc}"
        return report

    version = detect_receipt_version(raw_payload)
    report.version = version

    if version == "unknown":
        report.evidence_posture = "unknown"
        report.missing_proof_fields = ["receipt_version"]
        report.operator_review_triggers.append(
            "Receipt is missing receipt_version and cannot be trusted as a known schema."
        )
        report.reason = "Receipt is missing receipt_version."
        return report

    try:
        parsed = load_receipt_payload(receipt_path)
    except LoopManagerError as exc:
        report.operator_review_triggers.append(str(exc))
        report.reason = f"Schema validation failed: {exc}"
        return report

    report.schema_valid = True
    if isinstance(parsed, LoopReceipt):
        return _classify_v0(receipt_path, parsed, report)
    if isinstance(parsed, V1LoopReceipt):
        return _classify_v1(receipt_path, parsed, report)
    report.reason = "Unknown receipt payload class."
    return report


def _classify_v0(
    receipt_path: Path, receipt: LoopReceipt, report: ReceiptReport
) -> ReceiptReport:
    del receipt_path
    report.version = RECEIPT_VERSION_V0
    report.mode = "dry_run"
    report.evidence_posture = "attached_evidence"
    report.trust_level = "validation_captured"
    report.actionability = "review_required"
    report.lifecycle_mutation_allowed = False
    report.ingestion_allowed = False
    report.operator_review_required = True
    report.codexify_ingestion_readiness = "blocked"
    report.missing_proof_fields = list(V0_MISSING_PROOF_FIELDS)
    report.operator_review_triggers.append(
        "v0 receipt cannot become durable proof without review."
    )
    report.reason = (
        "v0 receipts are admissible as attached evidence but are not "
        "Codexify-native durable proof artifacts."
    )
    return report


def _classify_v1(
    receipt_path: Path, receipt: V1LoopReceipt, report: ReceiptReport
) -> ReceiptReport:
    del receipt_path
    report.version = RECEIPT_VERSION_V1
    report.mode = receipt.mode_trust_actionability.receipt_mode
    report.evidence_posture = "proof_envelope_candidate"
    report.trust_level = receipt.mode_trust_actionability.trust_level
    report.actionability = receipt.mode_trust_actionability.actionability
    report.lifecycle_mutation_allowed = False
    report.ingestion_allowed = False
    report.operator_review_required = (
        receipt.review.operator_review_required
        or receipt.review.reviewer_decision is None
    )
    missing: list[str] = []
    warnings: list[str] = []

    if receipt.identity.attempt_id is None:
        missing.append("attempt_id")
    if receipt.identity.work_order_id is None:
        missing.append("work_order_id")
    if receipt.artifacts.receipt_ref is None:
        missing.append("explicit receipt_ref")
    if not receipt.validation:
        missing.append("structured validation outputs")
    if not receipt.acceptance:
        missing.append("per-criterion acceptance results")
    if not receipt.changes:
        missing.append("actual changed-file semantics")

    if receipt.trust_level_requires_reviewer_evidence():
        missing_reviewer_bits: list[str] = []
        if receipt.review.reviewer is None:
            missing_reviewer_bits.append("reviewer")
        if receipt.review.reviewed_at is None:
            missing_reviewer_bits.append("reviewed_at")
        if receipt.review.reviewer_decision is None:
            missing_reviewer_bits.append("reviewer_decision")
        if missing_reviewer_bits:
            if len(missing_reviewer_bits) == 3:
                required_text = "reviewer, reviewed_at, and reviewer_decision"
            elif len(missing_reviewer_bits) == 2:
                required_text = " and ".join(missing_reviewer_bits)
            else:
                required_text = missing_reviewer_bits[0]
            warnings.append(
                "trust_level="
                f"{receipt.mode_trust_actionability.trust_level} requires "
                + required_text
                + "."
            )
            missing.extend(bit for bit in missing_reviewer_bits if bit not in missing)

    if any(
        change.change_kind == "proposed" and "*" in change.path
        for change in receipt.changes
    ):
        warnings.append(
            "Proposed/globbed change semantics are weaker than actual changed-file evidence."
        )
        if "actual changed-file semantics" not in missing:
            missing.append("actual changed-file semantics")

    report.authority_warnings = warnings
    report.missing_proof_fields = missing

    if missing or warnings:
        report.actionability = "review_required"
        report.codexify_ingestion_readiness = "blocked"
        report.operator_review_triggers.extend(
            warnings
            or [
                "v1 proof envelope is missing fields required for Codexify ingestion."
            ]
        )
        report.reason = (
            "v1 receipt is recognized, but required proof-envelope fields or "
            "review authority evidence are incomplete."
        )
        return report

    report.codexify_ingestion_readiness = "candidate"
    report.operator_review_triggers.append(
        "v1 receipt remains evidence pending governed operator review."
    )
    report.reason = (
        "v1 receipt is a compatible proof-envelope candidate pending operator review."
    )
    return report


def render_report(report: ReceiptReport) -> str:
    missing_lines = report.missing_proof_fields or ["none"]
    warning_lines = report.authority_warnings or ["none"]
    trigger_lines = report.operator_review_triggers or ["none"]
    return "\n".join(
        [
            "Pi Loop Receipt Compatibility Report",
            "Receipt:",
            f"  path: {report.receipt_path}",
            f"  version: {report.version}",
            f"  schema_valid: {str(report.schema_valid).lower()}",
            "Evidence posture:",
            f"  mode: {report.mode}",
            f"  evidence_posture: {report.evidence_posture}",
            f"  trust_level: {report.trust_level}",
            f"  actionability: {report.actionability}",
            "Authority posture:",
            "  receipt_is_evidence_not_truth: true",
            f"  lifecycle_mutation_allowed: {str(report.lifecycle_mutation_allowed).lower()}",
            f"  ingestion_allowed: {str(report.ingestion_allowed).lower()}",
            f"  operator_review_required: {str(report.operator_review_required).lower()}",
            "Missing proof fields:",
            *[f"  - {item}" for item in missing_lines],
            "Authority warnings:",
            *[f"  - {item}" for item in warning_lines],
            "Operator review triggers:",
            *[f"  - {item}" for item in trigger_lines],
            "Codexify ingestion readiness:",
            f"  {report.codexify_ingestion_readiness}",
            "Reason:",
            f"  {report.reason}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = classify_receipt(args.receipt.expanduser().resolve())
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_report(report))
    return 0 if report.schema_valid else 1
