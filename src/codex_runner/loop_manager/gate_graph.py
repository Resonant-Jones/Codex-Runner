from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GateDefinition:
    gate_id: str
    role: str
    required_inputs: tuple[str, ...]
    allowed_outputs: tuple[str, ...]
    authority_scope: str
    validation_rule: str


GATE_GRAPH: tuple[GateDefinition, ...] = (
    GateDefinition(
        gate_id="context_curator",
        role="context_curator",
        required_inputs=("task_spec", "repo_root"),
        allowed_outputs=("context_packet", "missing_context"),
        authority_scope="Load declared task context and repo-local references.",
        validation_rule="All declared context docs must exist or gate blocks.",
    ),
    GateDefinition(
        gate_id="architecture_gate",
        role="architecture_gate",
        required_inputs=("context_packet",),
        allowed_outputs=("architecture_posture",),
        authority_scope="Detect architecture-sensitive changes before execution.",
        validation_rule="Fail closed on uncertain architecture-impact signals.",
    ),
    GateDefinition(
        gate_id="adr_gate",
        role="adr_gate",
        required_inputs=("architecture_posture",),
        allowed_outputs=("adr_posture",),
        authority_scope="Classify ADR impact and promotion boundaries.",
        validation_rule="Accepted ADR paths remain read-only.",
    ),
    GateDefinition(
        gate_id="planner",
        role="planner",
        required_inputs=("task_spec", "context_packet"),
        allowed_outputs=("plan_packet",),
        authority_scope="Produce bounded plan and execution packet.",
        validation_rule="Plan must stay within declared task scope.",
    ),
    GateDefinition(
        gate_id="plan_validator",
        role="plan_validator",
        required_inputs=("plan_packet",),
        allowed_outputs=("validated_plan", "repair_request"),
        authority_scope="Reject incomplete or out-of-scope plans.",
        validation_rule="Plan must map to acceptance criteria and path bounds.",
    ),
    GateDefinition(
        gate_id="executor",
        role="executor",
        required_inputs=("validated_plan",),
        allowed_outputs=("execution_result",),
        authority_scope="Invoke provider adapter only through packet interface.",
        validation_rule="Provider may not become task-semantic authority.",
    ),
    GateDefinition(
        gate_id="inspector",
        role="inspector",
        required_inputs=("execution_result",),
        allowed_outputs=("inspection_report",),
        authority_scope="Inspect returned path claims and progress delta.",
        validation_rule="Stop when forbidden paths or zero progress appear.",
    ),
    GateDefinition(
        gate_id="runtime_validator",
        role="runtime_validator",
        required_inputs=("inspection_report", "validation_commands"),
        allowed_outputs=("validation_result",),
        authority_scope="Run declared validation commands and capture evidence.",
        validation_rule="Suggested but unrun validation does not count as proof.",
    ),
    GateDefinition(
        gate_id="documentation_steward",
        role="documentation_steward",
        required_inputs=("inspection_report", "validation_result"),
        allowed_outputs=("documentation_posture",),
        authority_scope="Enforce documentation write authority and review gates.",
        validation_rule="Canonical docs stay read-only unless explicit authority exists.",
    ),
    GateDefinition(
        gate_id="receipt_writer",
        role="receipt_writer",
        required_inputs=("documentation_posture",),
        allowed_outputs=("loop_receipt",),
        authority_scope="Emit honest run receipt and follow-up recommendations.",
        validation_rule="Receipt status must match actual gate evidence.",
    ),
)


def gate_ids() -> list[str]:
    return [gate.gate_id for gate in GATE_GRAPH]

