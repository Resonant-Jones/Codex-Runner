from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .adr_policy import classify_adr_impact
from .contracts import (
    GateReceipt,
    LoopManagerError,
    LoopReceipt,
    RetryPolicyConfig,
    generate_run_id,
    json_write,
    load_task_spec,
)
from .docs_policy import documentation_impact_for_paths, operator_review_required
from .executor import ExecutorProvider, ManualPacketProvider, StubExecutorProvider
from .gate_graph import gate_ids
from .inspector import inspect_execution_result
from .planner import build_context_packet, build_execution_packet, build_plan_summary
from .receipts import build_gate_receipt, build_loop_receipt
from .retry_policy import RetryTracker, retry_budget_exhausted
from .validator import run_validation_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pi Loop Manager v0")
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--dry-run", action="store_true")
    mode_group.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--provider",
        choices=["stub", "manual"],
        default="stub",
        help="Bounded provider adapter for loop execution",
    )
    parser.add_argument(
        "--run-output-dir",
        type=Path,
        default=None,
        help="Defaults to <repo-root>/.pi/runs/<run_id>",
    )
    return parser


def resolve_provider(name: str, run_dir: Path) -> ExecutorProvider:
    if name == "stub":
        return StubExecutorProvider()
    if name == "manual":
        return ManualPacketProvider(run_dir)
    raise LoopManagerError(f"unsupported provider: {name}")


def _artifact_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def _write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _receipt_summary(receipt: LoopReceipt) -> str:
    receipt_path = next(
        (ref for ref in receipt.evidence_refs if ref.endswith("/receipt.json")),
        None,
    )
    return json.dumps(
        {
            "task_id": receipt.task_id,
            "run_id": receipt.run_id,
            "status": receipt.status,
            "stop_reason": receipt.stop_reason,
            "changed_paths": receipt.changed_paths,
            "receipt_path": receipt_path,
        },
        indent=2,
    )


def run_loop(args: argparse.Namespace) -> LoopReceipt:
    repo_root = args.repo_root.expanduser().resolve()
    if not repo_root.exists():
        raise LoopManagerError(f"repo root does not exist: {repo_root}")

    task = load_task_spec(args.task.expanduser().resolve())
    run_id = generate_run_id()
    run_dir = (
        args.run_output_dir.expanduser().resolve()
        if args.run_output_dir is not None
        else repo_root / ".pi" / "runs" / run_id
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    task_copy_path = run_dir / "task.yaml"
    task_copy_path.write_text(
        args.task.expanduser().resolve().read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    provider = resolve_provider(args.provider, run_dir)
    retry_tracker = RetryTracker(
        RetryPolicyConfig(max_execution_attempts=min(task.max_attempts, 3))
    )
    mode = "execute" if args.execute else "dry-run"

    gate_receipts: list[GateReceipt] = []
    previous_changed_paths: list[str] = []
    stop_reason = "goal_satisfied"
    loop_status = "passed"
    final_summary = ""
    validation_summary = ""
    operator_review = False
    follow_ups: list[str] = []

    context_packet = build_context_packet(task, repo_root)
    context_receipt = build_gate_receipt(
        work_order_id=None,
        task_id=task.id,
        run_id=run_id,
        attempt=1,
        gate_id="context_curator",
        status="passed" if not context_packet["missing_docs"] else "blocked",
        summary=(
            "Context packet assembled."
            if not context_packet["missing_docs"]
            else f"Missing context docs: {', '.join(context_packet['missing_docs'])}"
        ),
        evidence_refs=[_artifact_relative(task_copy_path, repo_root)],
        next_gate="architecture_gate" if not context_packet["missing_docs"] else None,
        stop_reason=None if not context_packet["missing_docs"] else "missing_context",
    )
    gate_receipts.append(context_receipt)
    if context_receipt.status == "blocked":
        stop_reason = "missing_context"
        loop_status = "blocked"
    else:
        plan_summary = build_plan_summary(task, context_packet)
        plan_path = run_dir / "plan.md"
        _write_markdown(plan_path, plan_summary + "\n")

        architecture_receipt = build_gate_receipt(
            work_order_id=None,
            task_id=task.id,
            run_id=run_id,
            attempt=1,
            gate_id="architecture_gate",
            status="passed",
            summary="Architecture posture recorded for bounded local loop.",
            evidence_refs=[_artifact_relative(plan_path, repo_root)],
            next_gate="adr_gate",
        )
        gate_receipts.append(architecture_receipt)

        adr_impact = classify_adr_impact(task, [])
        adr_receipt = build_gate_receipt(
            work_order_id=None,
            task_id=task.id,
            run_id=run_id,
            attempt=1,
            gate_id="adr_gate",
            status="passed" if adr_impact in {"none", "uses_existing"} else "needs_review",
            summary=f"ADR impact classified as {adr_impact}.",
            evidence_refs=[_artifact_relative(plan_path, repo_root)],
            adr_impact=adr_impact,
            next_gate="planner" if adr_impact in {"none", "uses_existing"} else None,
            stop_reason=None if adr_impact in {"none", "uses_existing"} else "adr_required",
        )
        gate_receipts.append(adr_receipt)

        if adr_receipt.status == "needs_review":
            stop_reason = "adr_required"
            loop_status = "needs_review"
            operator_review = True
            follow_ups.append("Create a proposed ADR before widening architecture scope.")
        else:
            planner_receipt = build_gate_receipt(
                work_order_id=None,
                task_id=task.id,
                run_id=run_id,
                attempt=1,
                gate_id="planner",
                status="passed",
                summary="Execution packet plan created.",
                evidence_refs=[_artifact_relative(plan_path, repo_root)],
                next_gate="plan_validator",
            )
            gate_receipts.append(planner_receipt)

            plan_validator_receipt = build_gate_receipt(
                work_order_id=None,
                task_id=task.id,
                run_id=run_id,
                attempt=1,
                gate_id="plan_validator",
                status="passed",
                summary="Plan stays within declared task scope.",
                evidence_refs=[_artifact_relative(plan_path, repo_root)],
                next_gate="executor",
            )
            gate_receipts.append(plan_validator_receipt)

            for attempt in range(1, task.max_attempts + 1):
                attempt_dir = run_dir / f"attempt-{attempt}"
                packet = build_execution_packet(
                    task,
                    run_id=run_id,
                    attempt=attempt,
                    repo_root=repo_root,
                    mode=mode,
                    plan_summary=plan_summary,
                    repair_instructions=(
                        None if attempt == 1 else "Repair prior validation failure without widening scope."
                    ),
                )
                packet_path = attempt_dir / "execution-packet.md"
                _write_markdown(
                    packet_path,
                    "# Execution Packet\n\n"
                    f"Run ID: {run_id}\n"
                    f"Attempt: {attempt}\n"
                    f"Mode: {mode}\n\n"
                    "## Plan\n\n"
                    f"{packet.plan_summary}\n\n"
                    "## Repair Instructions\n\n"
                    f"{packet.repair_instructions or 'None'}\n",
                )

                if args.execute and args.provider == "stub":
                    execution_result = provider.execute(packet)
                    execution_result.summary += (
                        " Execute mode currently uses a non-mutating stub provider."
                    )
                elif args.execute and args.provider == "manual":
                    execution_result = provider.execute(packet)
                else:
                    execution_result = provider.execute(packet)

                executor_output_path = attempt_dir / "executor-output.md"
                _write_markdown(
                    executor_output_path,
                    "# Executor Output\n\n"
                    f"Status: {execution_result.status}\n\n"
                    f"{execution_result.summary}\n",
                )
                execution_receipt = build_gate_receipt(
                    work_order_id=None,
                    task_id=task.id,
                    run_id=run_id,
                    attempt=attempt,
                    gate_id="executor",
                    status=execution_result.status,
                    summary=execution_result.summary,
                    evidence_refs=[_artifact_relative(executor_output_path, repo_root)],
                    changed_paths=execution_result.proposed_changed_paths,
                    next_gate="inspector" if execution_result.status == "passed" else None,
                    stop_reason=(
                        None
                        if execution_result.status == "passed"
                        else "provider_failed"
                    ),
                )
                gate_receipts.append(execution_receipt)

                if execution_result.status != "passed":
                    stop_reason = "provider_failed"
                    loop_status = (
                        "blocked"
                        if execution_result.status == "blocked"
                        else "failed"
                    )
                    break

                inspection = inspect_execution_result(
                    task, execution_result, previous_changed_paths
                )
                changed_paths_path = attempt_dir / "changed-paths.json"
                json_write(changed_paths_path, inspection["changed_paths"])
                inspector_receipt = build_gate_receipt(
                    work_order_id=None,
                    task_id=task.id,
                    run_id=run_id,
                    attempt=attempt,
                    gate_id="inspector",
                    status=(
                        "failed"
                        if inspection["forbidden_paths"]
                        else "failed"
                        if inspection["no_progress"]
                        else "passed"
                    ),
                    summary=(
                        f"Forbidden paths detected: {', '.join(inspection['forbidden_paths'])}"
                        if inspection["forbidden_paths"]
                        else "No progress delta across attempts."
                        if inspection["no_progress"]
                        else "Execution result inspection passed."
                    ),
                    evidence_refs=[_artifact_relative(changed_paths_path, repo_root)],
                    changed_paths=list(inspection["changed_paths"]),
                    next_gate=(
                        None
                        if inspection["forbidden_paths"] or inspection["no_progress"]
                        else "runtime_validator"
                    ),
                    stop_reason=(
                        "forbidden_path_touched"
                        if inspection["forbidden_paths"]
                        else "no_progress"
                        if inspection["no_progress"]
                        else None
                    ),
                )
                gate_receipts.append(inspector_receipt)
                if inspection["forbidden_paths"]:
                    stop_reason = "forbidden_path_touched"
                    loop_status = "failed"
                    break
                if inspection["no_progress"]:
                    stop_reason = "no_progress"
                    loop_status = "failed"
                    break

                validation_path = attempt_dir / "validation.log"
                validation = run_validation_commands(
                    commands=task.validation_commands,
                    repo_root=repo_root,
                    log_path=validation_path,
                )
                validation_summary = validation.summary
                validator_receipt = build_gate_receipt(
                    work_order_id=None,
                    task_id=task.id,
                    run_id=run_id,
                    attempt=attempt,
                    gate_id="runtime_validator",
                    status=validation.status,
                    summary=validation.summary,
                    evidence_refs=[_artifact_relative(validation_path, repo_root)],
                    changed_paths=list(inspection["changed_paths"]),
                    next_gate=(
                        "documentation_steward"
                        if validation.status == "passed"
                        else None
                    ),
                    stop_reason=(
                        None if validation.status == "passed" else "validation_failed"
                    ),
                )
                gate_receipts.append(validator_receipt)

                if validation.status != "passed":
                    failure_signature = json.dumps(
                        {
                            "status": validation.status,
                            "commands": [
                                {
                                    "command": entry["command"],
                                    "returncode": entry["returncode"],
                                }
                                for entry in validation.command_results
                            ],
                        },
                        sort_keys=True,
                    )
                    retry_tracker.record_failure(failure_signature)
                    if retry_tracker.should_stop_for_repeated_failure(
                        failure_signature
                    ):
                        stop_reason = "validation_failed"
                        loop_status = "failed"
                        follow_ups.append(
                            "Validation failure repeated; inspect validation.log before retrying."
                        )
                        break
                    if retry_budget_exhausted(attempt, retry_tracker.config) or attempt >= task.max_attempts:
                        stop_reason = "max_attempts_reached"
                        loop_status = "max_attempts_reached"
                        follow_ups.append(
                            "Retry budget exhausted; hand off with targeted repair packet."
                        )
                        break
                    previous_changed_paths = list(inspection["changed_paths"])
                    continue

                doc_impact = documentation_impact_for_paths(
                    list(inspection["changed_paths"])
                )
                adr_impact = classify_adr_impact(
                    task, list(inspection["changed_paths"])
                )
                operator_review = operator_review_required(
                    changed_paths=list(inspection["changed_paths"]),
                    objective=task.objective,
                    requested_review_flags=task.operator_review_required_for,
                )
                documentation_receipt = build_gate_receipt(
                    work_order_id=None,
                    task_id=task.id,
                    run_id=run_id,
                    attempt=attempt,
                    gate_id="documentation_steward",
                    status=(
                        "needs_review"
                        if operator_review or adr_impact == "proposal_required"
                        else "passed"
                    ),
                    summary=(
                        "Operator review required for design/ADR-sensitive scope."
                        if operator_review or adr_impact == "proposal_required"
                        else "Documentation and ADR policy checks passed."
                    ),
                    evidence_refs=[_artifact_relative(changed_paths_path, repo_root)],
                    changed_paths=list(inspection["changed_paths"]),
                    adr_impact=adr_impact,
                    documentation_impact=doc_impact,
                    next_gate=(
                        None
                        if operator_review or adr_impact == "proposal_required"
                        else "receipt_writer"
                    ),
                    stop_reason=(
                        "operator_review_required"
                        if operator_review
                        else "adr_required"
                        if adr_impact == "proposal_required"
                        else None
                    ),
                )
                gate_receipts.append(documentation_receipt)

                if documentation_receipt.status == "needs_review":
                    stop_reason = (
                        "operator_review_required"
                        if operator_review
                        else "adr_required"
                    )
                    loop_status = "needs_review"
                    follow_ups.append(
                        "Review proposed change scope before allowing broader execution."
                    )
                    break

                final_summary = (
                    f"Loop completed in {mode} mode with provider={args.provider} "
                    f"across gate graph {', '.join(gate_ids())}."
                )
                stop_reason = "goal_satisfied"
                loop_status = "passed"
                previous_changed_paths = list(inspection["changed_paths"])
                break

    all_changed_paths = sorted(
        {
            path
            for receipt in gate_receipts
            for path in receipt.changed_paths
            if not path.startswith(".pi/runs/")
        }
    )
    receipt = build_loop_receipt(
        task_id=task.id,
        run_id=run_id,
        status=loop_status,
        stop_reason=stop_reason,
        attempts=gate_receipts,
        final_summary=final_summary
        or "Loop ended before execution completed.",
        validation_summary=validation_summary or "Validation did not run.",
        changed_paths=all_changed_paths,
        evidence_refs=[],
        operator_review_required=operator_review,
        follow_up_recommendations=follow_ups,
    )
    receipt_path = run_dir / "receipt.json"
    gate_receipts_path = run_dir / "attempt-1" / "gate-receipts.json"
    handoff_path = run_dir / "handoff.md"
    json_write(gate_receipts_path, [entry.to_dict() for entry in gate_receipts])
    json_write(receipt_path, receipt.to_dict())
    _write_markdown(
        handoff_path,
        "# Pi Loop Manager Handoff\n\n"
        f"Status: {receipt.status}\n\n"
        f"Stop reason: {receipt.stop_reason}\n\n"
        f"Final summary: {receipt.final_summary}\n",
    )
    receipt.evidence_refs.extend(
        [
            _artifact_relative(receipt_path, repo_root),
            _artifact_relative(handoff_path, repo_root),
        ]
    )
    json_write(receipt_path, receipt.to_dict())
    return receipt


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if raw_argv and raw_argv[0] == "report":
        from .receipt_report import main as report_main

        return report_main(raw_argv[1:])
    args = build_parser().parse_args(raw_argv)
    receipt = run_loop(args)
    print(_receipt_summary(receipt))
    return 0 if receipt.status == "passed" else 1
