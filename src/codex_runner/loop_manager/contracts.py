from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

RECEIPT_VERSION_V0 = "v0"
RECEIPT_VERSION_V1 = "v1"
RECEIPT_KIND_V1 = "pi_loop_receipt"
RECEIPT_VERSION_VALUES = {RECEIPT_VERSION_V0, RECEIPT_VERSION_V1}
GATE_STATUS_VALUES = {"passed", "failed", "blocked", "needs_review", "skipped"}
LOOP_STATUS_VALUES = {
    "passed",
    "failed",
    "blocked",
    "needs_review",
    "max_attempts_reached",
}
STOP_REASON_VALUES = {
    "goal_satisfied",
    "validation_failed",
    "max_attempts_reached",
    "no_progress",
    "operator_review_required",
    "missing_context",
    "provider_failed",
    "execution_not_supported",
    "adr_required",
    "forbidden_path_touched",
}
ADR_IMPACT_VALUES = {
    "none",
    "uses_existing",
    "proposal_required",
    "proposal_created",
    "operator_required",
}
DOCUMENTATION_IMPACT_VALUES = {
    "none",
    "handoff_only",
    "proposal_created",
    "canonical_change_required",
}
RECEIPT_MODE_VALUES = {"dry_run", "patch_producing", "local_execution"}
TRUST_LEVEL_VALUES = {
    "artifact_only",
    "validation_captured",
    "validation_passed",
    "operator_reviewed",
    "durable_evidence_ingested",
}
ACTIONABILITY_VALUES = {
    "observe_only",
    "review_required",
    "ingestion_candidate",
}
DECLARED_BY_VALUES = {"task_spec", "repo_profile", "loop_suggested"}
ACCEPTANCE_STATUS_VALUES = {"passed", "failed", "blocked", "unknown"}
CHANGE_KIND_VALUES = {
    "proposed",
    "generated_patch",
    "applied_diff",
    "observed_git_diff",
}


class LoopManagerError(RuntimeError):
    """Raised when loop-manager invariants are violated."""


def _normalize_relpath(raw_path: str) -> str:
    value = raw_path.replace("\\", "/").strip()
    if not value:
        raise LoopManagerError("path entries cannot be empty")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise LoopManagerError(f"invalid relative path entry: {raw_path}")
    return str(pure)


def _normalize_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise LoopManagerError(f"{field_name} must be a list")
    return [str(item).strip() for item in value]


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _required_text(value: Any, field_name: str) -> str:
    text = _optional_text(value)
    if text is None:
        raise LoopManagerError(f"{field_name} cannot be empty")
    return text


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LoopManagerError(f"{field_name} must be an object")
    return dict(value)


@dataclass(slots=True)
class LoopTask:
    id: str
    objective: str
    repo_root: str | None
    max_attempts: int
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_criteria: list[str]
    validation_commands: list[str]
    operator_review_required_for: list[str]
    context_docs: list[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LoopTask":
        required = {
            "id",
            "objective",
            "repo_root",
            "max_attempts",
            "allowed_paths",
            "forbidden_paths",
            "acceptance_criteria",
            "validation_commands",
            "operator_review_required_for",
            "context_docs",
        }
        missing = sorted(required - payload.keys())
        if missing:
            raise LoopManagerError(
                f"task spec missing required fields: {', '.join(missing)}"
            )

        task = cls(
            id=str(payload["id"]).strip(),
            objective=str(payload["objective"]).strip(),
            repo_root=(
                None
                if payload["repo_root"] in (None, "")
                else str(payload["repo_root"]).strip()
            ),
            max_attempts=int(payload["max_attempts"]),
            allowed_paths=[
                _normalize_relpath(path)
                for path in _normalize_list(payload["allowed_paths"], "allowed_paths")
            ],
            forbidden_paths=[
                _normalize_relpath(path)
                for path in _normalize_list(
                    payload["forbidden_paths"], "forbidden_paths"
                )
            ],
            acceptance_criteria=_normalize_list(
                payload["acceptance_criteria"], "acceptance_criteria"
            ),
            validation_commands=_normalize_list(
                payload["validation_commands"], "validation_commands"
            ),
            operator_review_required_for=_normalize_list(
                payload["operator_review_required_for"],
                "operator_review_required_for",
            ),
            context_docs=[
                _normalize_relpath(path)
                for path in _normalize_list(payload["context_docs"], "context_docs")
            ],
        )
        task.validate()
        return task

    def validate(self) -> None:
        if not self.id:
            raise LoopManagerError("task id cannot be empty")
        if not self.objective:
            raise LoopManagerError("task objective cannot be empty")
        if self.max_attempts < 1:
            raise LoopManagerError("task max_attempts must be >= 1")
        if not self.allowed_paths:
            raise LoopManagerError("task allowed_paths cannot be empty")
        if not self.acceptance_criteria:
            raise LoopManagerError("task acceptance_criteria cannot be empty")
        if not self.validation_commands:
            raise LoopManagerError("task validation_commands cannot be empty")


@dataclass(slots=True)
class GateReceipt:
    work_order_id: str | None
    task_id: str
    run_id: str
    attempt: int
    gate_id: str
    status: str
    summary: str
    evidence_refs: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    adr_impact: str = "none"
    documentation_impact: str = "none"
    next_gate: str | None = None
    stop_reason: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GateReceipt":
        receipt = cls(
            work_order_id=_optional_text(payload.get("work_order_id")),
            task_id=_required_text(payload.get("task_id"), "task_id"),
            run_id=_required_text(payload.get("run_id"), "run_id"),
            attempt=int(payload.get("attempt", 0)),
            gate_id=_required_text(payload.get("gate_id"), "gate_id"),
            status=_required_text(payload.get("status"), "status"),
            summary=_required_text(payload.get("summary"), "summary"),
            evidence_refs=_normalize_list(
                payload.get("evidence_refs", []), "evidence_refs"
            ),
            changed_paths=_normalize_list(
                payload.get("changed_paths", []), "changed_paths"
            ),
            adr_impact=str(payload.get("adr_impact", "none")).strip() or "none",
            documentation_impact=(
                str(payload.get("documentation_impact", "none")).strip()
                or "none"
            ),
            next_gate=_optional_text(payload.get("next_gate")),
            stop_reason=_optional_text(payload.get("stop_reason")),
        )
        receipt.validate()
        return receipt

    def validate(self) -> None:
        if self.attempt < 1:
            raise LoopManagerError("gate attempt must be >= 1")
        if self.status not in GATE_STATUS_VALUES:
            raise LoopManagerError(f"invalid gate status: {self.status}")
        if self.adr_impact not in ADR_IMPACT_VALUES:
            raise LoopManagerError(f"invalid adr impact: {self.adr_impact}")
        if self.documentation_impact not in DOCUMENTATION_IMPACT_VALUES:
            raise LoopManagerError(
                f"invalid documentation impact: {self.documentation_impact}"
            )
        if self.stop_reason is not None and self.stop_reason not in STOP_REASON_VALUES:
            raise LoopManagerError(f"invalid stop reason: {self.stop_reason}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(slots=True)
class LoopReceipt:
    task_id: str
    run_id: str
    status: str
    stop_reason: str
    attempts: list[GateReceipt]
    final_summary: str
    validation_summary: str
    changed_paths: list[str]
    evidence_refs: list[str]
    operator_review_required: bool
    follow_up_recommendations: list[str]
    receipt_version: str = RECEIPT_VERSION_V0

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LoopReceipt":
        version = str(payload.get("receipt_version") or RECEIPT_VERSION_V0).strip()
        receipt = cls(
            receipt_version=version,
            task_id=_required_text(payload.get("task_id"), "task_id"),
            run_id=_required_text(payload.get("run_id"), "run_id"),
            status=_required_text(payload.get("status"), "status"),
            stop_reason=_required_text(payload.get("stop_reason"), "stop_reason"),
            attempts=[
                GateReceipt.from_dict(_mapping(item, "attempts[]"))
                for item in _normalize_list_of_mappings(
                    payload.get("attempts", []), "attempts"
                )
            ],
            final_summary=_required_text(
                payload.get("final_summary"), "final_summary"
            ),
            validation_summary=_required_text(
                payload.get("validation_summary"), "validation_summary"
            ),
            changed_paths=_normalize_list(
                payload.get("changed_paths", []), "changed_paths"
            ),
            evidence_refs=_normalize_list(
                payload.get("evidence_refs", []), "evidence_refs"
            ),
            operator_review_required=bool(
                payload.get("operator_review_required", False)
            ),
            follow_up_recommendations=_normalize_list(
                payload.get("follow_up_recommendations", []),
                "follow_up_recommendations",
            ),
        )
        receipt.validate()
        return receipt

    def validate(self) -> None:
        if self.receipt_version != RECEIPT_VERSION_V0:
            raise LoopManagerError(
                f"v0 LoopReceipt must use receipt_version={RECEIPT_VERSION_V0}"
            )
        if self.status not in LOOP_STATUS_VALUES:
            raise LoopManagerError(f"invalid loop status: {self.status}")
        if self.stop_reason not in STOP_REASON_VALUES:
            raise LoopManagerError(f"invalid stop reason: {self.stop_reason}")
        for attempt in self.attempts:
            attempt.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["attempts"] = [attempt.to_dict() for attempt in self.attempts]
        return payload


def _normalize_list_of_mappings(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise LoopManagerError(f"{field_name} must be a list")
    return [_mapping(item, f"{field_name}[]") for item in value]


@dataclass(slots=True)
class V1ReceiptIdentity:
    receipt_id: str | None
    task_id: str | None
    work_order_id: str | None
    attempt_id: str | None
    run_id: str | None
    source_repo: str | None
    source_ref: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ReceiptIdentity":
        return cls(
            receipt_id=_optional_text(payload.get("receipt_id")),
            task_id=_optional_text(payload.get("task_id")),
            work_order_id=_optional_text(payload.get("work_order_id")),
            attempt_id=_optional_text(payload.get("attempt_id")),
            run_id=_optional_text(payload.get("run_id")),
            source_repo=_optional_text(payload.get("source_repo")),
            source_ref=_optional_text(payload.get("source_ref")),
        )


@dataclass(slots=True)
class V1ModeTrustActionability:
    receipt_mode: str
    trust_level: str
    actionability: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ModeTrustActionability":
        value = cls(
            receipt_mode=_required_text(payload.get("receipt_mode"), "receipt_mode"),
            trust_level=_required_text(payload.get("trust_level"), "trust_level"),
            actionability=_required_text(payload.get("actionability"), "actionability"),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.receipt_mode not in RECEIPT_MODE_VALUES:
            raise LoopManagerError(f"invalid receipt_mode: {self.receipt_mode}")
        if self.trust_level not in TRUST_LEVEL_VALUES:
            raise LoopManagerError(f"invalid trust_level: {self.trust_level}")
        if self.actionability not in ACTIONABILITY_VALUES:
            raise LoopManagerError(f"invalid actionability: {self.actionability}")


@dataclass(slots=True)
class V1ValidationCommand:
    command: str
    exit_code: int | None
    stdout_ref: str | None
    stderr_ref: str | None
    artifact_ref: str | None
    declared_by: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ValidationCommand":
        value = cls(
            command=_required_text(payload.get("command"), "command"),
            exit_code=(
                None
                if payload.get("exit_code") is None
                else int(payload.get("exit_code"))
            ),
            stdout_ref=_optional_text(payload.get("stdout_ref")),
            stderr_ref=_optional_text(payload.get("stderr_ref")),
            artifact_ref=_optional_text(payload.get("artifact_ref")),
            declared_by=_required_text(payload.get("declared_by"), "declared_by"),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.declared_by not in DECLARED_BY_VALUES:
            raise LoopManagerError(f"invalid declared_by: {self.declared_by}")


@dataclass(slots=True)
class V1AcceptanceCriterion:
    id: str
    text: str
    status: str
    evidence_refs: list[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1AcceptanceCriterion":
        value = cls(
            id=_required_text(payload.get("id"), "id"),
            text=_required_text(payload.get("text"), "text"),
            status=_required_text(payload.get("status"), "status"),
            evidence_refs=_normalize_list(
                payload.get("evidence_refs", []), "evidence_refs"
            ),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.status not in ACCEPTANCE_STATUS_VALUES:
            raise LoopManagerError(f"invalid acceptance status: {self.status}")


@dataclass(slots=True)
class V1ChangedPath:
    path: str
    change_kind: str
    evidence_ref: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ChangedPath":
        value = cls(
            path=_required_text(payload.get("path"), "path"),
            change_kind=_required_text(payload.get("change_kind"), "change_kind"),
            evidence_ref=_optional_text(payload.get("evidence_ref")),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.change_kind not in CHANGE_KIND_VALUES:
            raise LoopManagerError(f"invalid change_kind: {self.change_kind}")


@dataclass(slots=True)
class V1ReviewEnvelope:
    operator_review_required: bool
    review_reasons: list[str]
    reviewer_decision: str | None
    reviewer: str | None
    reviewed_at: str | None
    rationale: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ReviewEnvelope":
        return cls(
            operator_review_required=bool(
                payload.get("operator_review_required", False)
            ),
            review_reasons=_normalize_list(
                payload.get("review_reasons", []), "review_reasons"
            ),
            reviewer_decision=_optional_text(payload.get("reviewer_decision")),
            reviewer=_optional_text(payload.get("reviewer")),
            reviewed_at=_optional_text(payload.get("reviewed_at")),
            rationale=_optional_text(payload.get("rationale")),
        )


@dataclass(slots=True)
class V1LineageEnvelope:
    source_thread_id: str | None
    source_message_id: str | None
    command_run_id: str | None
    guardian_run_id: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1LineageEnvelope":
        return cls(
            source_thread_id=_optional_text(payload.get("source_thread_id")),
            source_message_id=_optional_text(payload.get("source_message_id")),
            command_run_id=_optional_text(payload.get("command_run_id")),
            guardian_run_id=_optional_text(payload.get("guardian_run_id")),
        )


@dataclass(slots=True)
class V1ArtifactsEnvelope:
    receipt_ref: str | None
    gate_receipts_ref: str | None
    handoff_ref: str | None
    validation_refs: list[str]
    plan_ref: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1ArtifactsEnvelope":
        return cls(
            receipt_ref=_optional_text(payload.get("receipt_ref")),
            gate_receipts_ref=_optional_text(payload.get("gate_receipts_ref")),
            handoff_ref=_optional_text(payload.get("handoff_ref")),
            validation_refs=_normalize_list(
                payload.get("validation_refs", []), "validation_refs"
            ),
            plan_ref=_optional_text(payload.get("plan_ref")),
        )


@dataclass(slots=True)
class V1PolicyEnvelope:
    documentation_impact: str
    adr_impact: str
    operator_review_stop: bool
    stop_reason: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1PolicyEnvelope":
        value = cls(
            documentation_impact=(
                _required_text(
                    payload.get("documentation_impact"), "documentation_impact"
                )
            ),
            adr_impact=_required_text(payload.get("adr_impact"), "adr_impact"),
            operator_review_stop=bool(payload.get("operator_review_stop", False)),
            stop_reason=_optional_text(payload.get("stop_reason")),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.documentation_impact not in DOCUMENTATION_IMPACT_VALUES:
            raise LoopManagerError(
                f"invalid documentation impact: {self.documentation_impact}"
            )
        if self.adr_impact not in ADR_IMPACT_VALUES:
            raise LoopManagerError(f"invalid adr impact: {self.adr_impact}")
        if self.stop_reason is not None and self.stop_reason not in STOP_REASON_VALUES:
            raise LoopManagerError(f"invalid stop reason: {self.stop_reason}")


@dataclass(slots=True)
class V1LoopReceipt:
    receipt_version: str
    schema_version: str
    receipt_kind: str
    identity: V1ReceiptIdentity
    mode_trust_actionability: V1ModeTrustActionability
    validation: list[V1ValidationCommand]
    acceptance: list[V1AcceptanceCriterion]
    changes: list[V1ChangedPath]
    review: V1ReviewEnvelope
    lineage: V1LineageEnvelope
    artifacts: V1ArtifactsEnvelope
    policy: V1PolicyEnvelope

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "V1LoopReceipt":
        value = cls(
            receipt_version=_required_text(
                payload.get("receipt_version"), "receipt_version"
            ),
            schema_version=_required_text(
                payload.get("schema_version"), "schema_version"
            ),
            receipt_kind=_required_text(
                payload.get("receipt_kind"), "receipt_kind"
            ),
            identity=V1ReceiptIdentity.from_dict(
                _mapping(payload.get("identity"), "identity")
            ),
            mode_trust_actionability=V1ModeTrustActionability.from_dict(
                _mapping(
                    payload.get("mode_trust_actionability"),
                    "mode_trust_actionability",
                )
            ),
            validation=[
                V1ValidationCommand.from_dict(item)
                for item in _normalize_list_of_mappings(
                    _mapping(payload.get("validation"), "validation").get(
                        "commands", []
                    ),
                    "validation.commands",
                )
            ],
            acceptance=[
                V1AcceptanceCriterion.from_dict(item)
                for item in _normalize_list_of_mappings(
                    _mapping(payload.get("acceptance"), "acceptance").get(
                        "criteria", []
                    ),
                    "acceptance.criteria",
                )
            ],
            changes=[
                V1ChangedPath.from_dict(item)
                for item in _normalize_list_of_mappings(
                    _mapping(payload.get("changes"), "changes").get(
                        "changed_paths", []
                    ),
                    "changes.changed_paths",
                )
            ],
            review=V1ReviewEnvelope.from_dict(
                _mapping(payload.get("review"), "review")
            ),
            lineage=V1LineageEnvelope.from_dict(
                _mapping(payload.get("lineage"), "lineage")
            ),
            artifacts=V1ArtifactsEnvelope.from_dict(
                _mapping(payload.get("artifacts"), "artifacts")
            ),
            policy=V1PolicyEnvelope.from_dict(
                _mapping(payload.get("policy"), "policy")
            ),
        )
        value.validate()
        return value

    def validate(self) -> None:
        if self.receipt_version != RECEIPT_VERSION_V1:
            raise LoopManagerError(
                f"v1 receipt must use receipt_version={RECEIPT_VERSION_V1}"
            )
        if self.receipt_kind != RECEIPT_KIND_V1:
            raise LoopManagerError(f"invalid receipt_kind: {self.receipt_kind}")
        self.mode_trust_actionability.validate()
        self.policy.validate()
        for entry in self.validation:
            entry.validate()
        for entry in self.acceptance:
            entry.validate()
        for entry in self.changes:
            entry.validate()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def trust_level_requires_reviewer_evidence(self) -> bool:
        return self.mode_trust_actionability.trust_level in {
            "operator_reviewed",
            "durable_evidence_ingested",
        }


@dataclass(slots=True)
class ExecutionPacket:
    task: LoopTask
    run_id: str
    attempt: int
    repo_root: Path
    mode: str
    plan_summary: str
    repair_instructions: str | None = None


@dataclass(slots=True)
class ExecutionResult:
    status: str
    summary: str
    proposed_changed_paths: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    repair_hints: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.status not in {"passed", "failed", "blocked", "needs_review"}:
            raise LoopManagerError(f"invalid execution result status: {self.status}")


@dataclass(slots=True)
class ValidationResult:
    status: str
    summary: str
    command_results: list[dict[str, Any]]
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetryPolicyConfig:
    max_plan_revisions: int = 2
    max_execution_attempts: int = 3
    max_validation_repairs: int = 2
    repeated_failure_limit: int = 1


def load_task_spec(task_path: Path) -> LoopTask:
    try:
        payload = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LoopManagerError(f"task file not found: {task_path}") from exc
    if not isinstance(payload, dict):
        raise LoopManagerError("task spec must decode to an object")
    return LoopTask.from_dict(payload)


def load_receipt_payload(receipt_path: Path) -> LoopReceipt | V1LoopReceipt:
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LoopManagerError(f"receipt file not found: {receipt_path}") from exc
    except json.JSONDecodeError as exc:
        raise LoopManagerError(f"invalid receipt JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise LoopManagerError("receipt payload must decode to an object")
    return validate_receipt_payload(payload)


def validate_receipt_payload(
    payload: dict[str, Any],
) -> LoopReceipt | V1LoopReceipt:
    version = str(payload.get("receipt_version") or RECEIPT_VERSION_V0).strip()
    if version == RECEIPT_VERSION_V0:
        return LoopReceipt.from_dict(payload)
    if version == RECEIPT_VERSION_V1:
        return V1LoopReceipt.from_dict(payload)
    raise LoopManagerError(f"unsupported receipt_version: {version}")


def generate_run_id() -> str:
    return f"pi-loop-{uuid.uuid4().hex[:12]}"


def json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
