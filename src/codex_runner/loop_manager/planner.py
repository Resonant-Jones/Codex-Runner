from __future__ import annotations

from pathlib import Path

from .contracts import ExecutionPacket, LoopTask


def build_context_packet(task: LoopTask, repo_root: Path) -> dict[str, object]:
    existing_docs: list[str] = []
    missing_docs: list[str] = []
    for rel_path in task.context_docs:
        if (repo_root / rel_path).exists():
            existing_docs.append(rel_path)
        else:
            missing_docs.append(rel_path)
    return {
        "task_id": task.id,
        "objective": task.objective,
        "repo_root": str(repo_root),
        "context_docs": existing_docs,
        "missing_docs": missing_docs,
        "acceptance_criteria": task.acceptance_criteria,
        "allowed_paths": task.allowed_paths,
        "forbidden_paths": task.forbidden_paths,
    }


def build_plan_summary(task: LoopTask, context_packet: dict[str, object]) -> str:
    doc_refs = ", ".join(context_packet["context_docs"]) or "none"
    criteria = "; ".join(task.acceptance_criteria)
    allowed = ", ".join(task.allowed_paths)
    return (
        f"Objective: {task.objective}\n"
        f"Acceptance criteria: {criteria}\n"
        f"Allowed paths: {allowed}\n"
        f"Context docs: {doc_refs}\n"
        "Execution posture: bounded dry-run loop with provider adapter."
    )


def build_execution_packet(
    task: LoopTask,
    *,
    run_id: str,
    attempt: int,
    repo_root: Path,
    mode: str,
    plan_summary: str,
    repair_instructions: str | None = None,
) -> ExecutionPacket:
    return ExecutionPacket(
        task=task,
        run_id=run_id,
        attempt=attempt,
        repo_root=repo_root,
        mode=mode,
        plan_summary=plan_summary,
        repair_instructions=repair_instructions,
    )

