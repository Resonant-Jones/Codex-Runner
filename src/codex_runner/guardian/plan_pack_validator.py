from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml

REQUIRED_FILES = [
    "README.md",
    "PLAN.md",
    "GOALS.md",
    "BOUNDARIES.md",
    "AUTHORIZATION.md",
    "ESCALATION.md",
    "SESSION_LOG.md",
    "TASK_SPEC.yaml",
]

REQUIRED_TASK_FIELDS = [
    "task_id",
    "title",
    "repo_root",
    "mode",
    "intent",
    "scope",
    "non_goals",
    "allowed_paths",
    "forbidden_paths",
    "allowed_commands",
    "forbidden_commands",
    "validation",
    "acceptance_criteria",
    "expected_artifacts",
    "escalation_triggers",
    "notes",
]

FORBIDDEN_REPO_PATHS = [
    "/Volumes/Dev_SSD/Codexify-main",
    "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core",
]

BOUNDARY_SIGNAL_GROUPS: dict[str, tuple[str, ...]] = {
    "authority is not self-promotable": (
        "authority is not self-promotable",
    ),
    "no Codexify ingestion authorization": (
        "does not authorize codexify ingestion",
        "no plan pack may authorize codexify ingestion",
        "any codexify ingestion behavior",
    ),
    "no durable mutation authorization": (
        "workorder lifecycle mutation",
        "execution ledger mutation",
        "durable state mutation",
        "durable-state mutation",
    ),
    "no provider execution authorization": (
        "provider execution",
    ),
    "no patch application authorization": (
        "patch application",
    ),
    "no dispatch authorization": (
        "dispatch",
    ),
    "no merge automation authorization": (
        "merge automation",
        " merge ",
    ),
    "no automatic reviewer decisions authorization": (
        "reviewer auto-fill",
        "automatic reviewer decisions",
    ),
    "no trust-level auto-promotion authorization": (
        "trust promotion",
        "trust-level auto-promotion",
    ),
}

ESCALATION_BANNER = "FLAG### HUMAN OPERATOR DECISION REQUIRED"

VALID_PASS_REASON = (
    "plan pack is structurally complete enough to be read by Guardian"
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "guardian_operational": False,
    "plan_execution_allowed": False,
    "pi_loop_invocation_allowed": False,
    "codexify_ingestion_allowed": False,
    "durable_mutation_allowed": False,
    "provider_execution_allowed": False,
    "patch_application_allowed": False,
    "dispatch_allowed": False,
    "merge_allowed": False,
}


@dataclass(frozen=True)
class GuardianPlanPackValidationIssue:
    section: str
    message: str


@dataclass(frozen=True)
class GuardianPlanPackReport:
    plan_pack_path: Path
    required_files: dict[str, bool]
    forbidden_path_checks: dict[str, bool]
    boundary_checks: dict[str, bool]
    task_spec_parses: bool
    task_spec_mode_is_dry_run: bool
    task_spec_required_fields_present: bool
    escalation_banner_present: bool
    issues: tuple[GuardianPlanPackValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    @property
    def result(self) -> str:
        return "pass" if self.valid else "fail"

    @property
    def reason(self) -> str:
        if self.valid:
            return VALID_PASS_REASON
        if self.issues:
            return self.issues[0].message
        return "validation failed"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "plan_pack_path": str(self.plan_pack_path),
            "valid": self.valid,
            "result": self.result,
            "required_files": dict(self.required_files),
            "forbidden_path_checks": dict(self.forbidden_path_checks),
            "boundary_checks": dict(self.boundary_checks),
            "task_spec": {
                "yaml_parses": self.task_spec_parses,
                "mode_is_dry_run": self.task_spec_mode_is_dry_run,
                "required_fields_present": self.task_spec_required_fields_present,
            },
            "escalation": {
                "flag_banner_present": self.escalation_banner_present,
            },
            "issues": [
                {"section": issue.section, "message": issue.message}
                for issue in self.issues
            ],
            "reason": self.reason,
            "authority": dict(AUTHORITY_LOCKS),
        }


def _read_if_present(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _normalized_text(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def _contains_declared_path(text: str, path: str) -> bool:
    normalized_text = text.lower()
    pattern = re.compile(rf"{re.escape(path.lower())}(?![-a-z0-9_])")
    return bool(pattern.search(normalized_text))


def validate_plan_pack(plan_pack_path: Path) -> GuardianPlanPackReport:
    plan_pack_path = plan_pack_path.expanduser().resolve()
    issues: list[GuardianPlanPackValidationIssue] = []

    required_files = {
        name: (plan_pack_path / name).is_file() for name in REQUIRED_FILES
    }
    for name, present in required_files.items():
        if not present:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Required files", f"Missing required file: {name}"
                )
            )

    texts = {
        name: _read_if_present(plan_pack_path / name) for name in REQUIRED_FILES
    }
    combined_text = _normalized_text("\n".join(texts.values()))

    boundary_text = _normalized_text(
        "\n".join(
            [
                texts.get("BOUNDARIES.md", ""),
                texts.get("TASK_SPEC.yaml", ""),
            ]
        )
    )
    forbidden_path_checks = {
        path: _contains_declared_path(boundary_text, path)
        for path in FORBIDDEN_REPO_PATHS
    }
    for path, present in forbidden_path_checks.items():
        if not present:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Boundary checks",
                    f"Missing forbidden repo path declaration: {path}",
                )
            )

    boundary_checks = {
        label: _contains_any(combined_text, phrases)
        for label, phrases in BOUNDARY_SIGNAL_GROUPS.items()
    }
    for label, present in boundary_checks.items():
        if not present:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Boundary checks",
                    f"Missing required boundary signal: {label}",
                )
            )

    escalation_banner_present = ESCALATION_BANNER.lower() in combined_text.lower()
    if not escalation_banner_present:
        issues.append(
            GuardianPlanPackValidationIssue(
                "Escalation", "Missing required escalation FLAG### banner"
            )
        )

    task_spec_parses = False
    task_spec_mode_is_dry_run = False
    task_spec_required_fields_present = False
    task_payload: object | None = None
    task_spec_path = plan_pack_path / "TASK_SPEC.yaml"
    if task_spec_path.is_file():
        try:
            task_payload = yaml.safe_load(task_spec_path.read_text(encoding="utf-8"))
            task_spec_parses = isinstance(task_payload, dict)
            if not task_spec_parses:
                issues.append(
                    GuardianPlanPackValidationIssue(
                        "Task spec",
                        "TASK_SPEC.yaml must parse to a YAML mapping",
                    )
                )
        except yaml.YAMLError as exc:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Task spec", f"TASK_SPEC.yaml failed to parse: {exc}"
                )
            )

    if isinstance(task_payload, dict):
        missing_fields = [
            field for field in REQUIRED_TASK_FIELDS if field not in task_payload
        ]
        task_spec_required_fields_present = not missing_fields
        if missing_fields:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Task spec",
                    "TASK_SPEC.yaml missing required fields: "
                    + ", ".join(missing_fields),
                )
            )
        task_spec_mode_is_dry_run = task_payload.get("mode") == "dry_run"
        if not task_spec_mode_is_dry_run:
            issues.append(
                GuardianPlanPackValidationIssue(
                    "Task spec",
                    "TASK_SPEC.yaml mode must be dry_run for this validator",
                )
            )

    return GuardianPlanPackReport(
        plan_pack_path=plan_pack_path,
        required_files=required_files,
        forbidden_path_checks=forbidden_path_checks,
        boundary_checks=boundary_checks,
        task_spec_parses=task_spec_parses,
        task_spec_mode_is_dry_run=task_spec_mode_is_dry_run,
        task_spec_required_fields_present=task_spec_required_fields_present,
        escalation_banner_present=escalation_banner_present,
        issues=tuple(issues),
    )


def render_report(report: GuardianPlanPackReport) -> str:
    valid_text = "true" if report.valid else "false"
    lines = [
        "Guardian Plan Pack Validation Report",
        "",
        "Plan pack:",
        f"  path: {report.plan_pack_path}",
        f"  valid: {valid_text}",
        "",
        "Required files:",
    ]
    for name in REQUIRED_FILES:
        status = "present" if report.required_files[name] else "missing"
        lines.append(f"  {name}: {status}")

    lines.extend(
        [
            "",
            "Boundary checks:",
            "  forbidden Codexify-main path declared: "
            + str(report.forbidden_path_checks[FORBIDDEN_REPO_PATHS[0]]).lower(),
            "  forbidden Codexify-Core path declared: "
            + str(report.forbidden_path_checks[FORBIDDEN_REPO_PATHS[1]]).lower(),
            "  authority is not self-promotable: "
            + str(report.boundary_checks["authority is not self-promotable"]).lower(),
            "  no Codexify ingestion authorization: "
            + str(
                report.boundary_checks[
                    "no Codexify ingestion authorization"
                ]
            ).lower(),
            "  no durable mutation authorization: "
            + str(
                report.boundary_checks[
                    "no durable mutation authorization"
                ]
            ).lower(),
            "  no provider execution authorization: "
            + str(
                report.boundary_checks[
                    "no provider execution authorization"
                ]
            ).lower(),
            "  no patch application authorization: "
            + str(
                report.boundary_checks[
                    "no patch application authorization"
                ]
            ).lower(),
            "  no dispatch authorization: "
            + str(
                report.boundary_checks["no dispatch authorization"]
            ).lower(),
            "  no merge automation authorization: "
            + str(
                report.boundary_checks[
                    "no merge automation authorization"
                ]
            ).lower(),
            "  no automatic reviewer decisions authorization: "
            + str(
                report.boundary_checks[
                    "no automatic reviewer decisions authorization"
                ]
            ).lower(),
            "  no trust-level auto-promotion authorization: "
            + str(
                report.boundary_checks[
                    "no trust-level auto-promotion authorization"
                ]
            ).lower(),
            "",
            "Task spec:",
            f"  yaml parses: {str(report.task_spec_parses).lower()}",
            "  mode is dry_run: "
            + str(report.task_spec_mode_is_dry_run).lower(),
            "  required fields present: "
            + str(report.task_spec_required_fields_present).lower(),
            "",
            "Escalation:",
            "  FLAG### banner present: "
            + str(report.escalation_banner_present).lower(),
            "",
            "Result:",
            f"  {report.result}",
            "",
            "Reason:",
        ]
    )
    lines.append(f"  {report.reason}")
    if not report.valid and len(report.issues) > 1:
        lines.append("")
        lines.append("Issues:")
        for issue in report.issues:
            lines.append(f"  - [{issue.section}] {issue.message}")
    return "\n".join(lines) + "\n"
