from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .contracts import ExecutionPacket, ExecutionResult


class ExecutorProvider(Protocol):
    def execute(self, packet: ExecutionPacket) -> ExecutionResult:
        ...


class StubExecutorProvider:
    def execute(self, packet: ExecutionPacket) -> ExecutionResult:
        proposed_paths = [
            path for path in packet.task.allowed_paths if not path.startswith(".pi/runs/")
        ]
        if not proposed_paths:
            proposed_paths = [".pi/runs/**"]
        summary = (
            f"Stub provider produced a deterministic execution result for "
            f"attempt {packet.attempt} in {packet.mode} mode."
        )
        return ExecutionResult(
            status="passed",
            summary=summary,
            proposed_changed_paths=proposed_paths,
            repair_hints=["Narrow scope further if validation fails."],
        )


class ManualPacketProvider:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def execute(self, packet: ExecutionPacket) -> ExecutionResult:
        output_path = (
            self.run_dir
            / f"attempt-{packet.attempt}"
            / "manual-provider-request.md"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "# Manual Provider Request\n\n"
            f"Run ID: {packet.run_id}\n"
            f"Attempt: {packet.attempt}\n"
            f"Mode: {packet.mode}\n\n"
            "## Plan Summary\n\n"
            f"{packet.plan_summary}\n\n"
            "## Repair Instructions\n\n"
            f"{packet.repair_instructions or 'None'}\n",
            encoding="utf-8",
        )
        return ExecutionResult(
            status="blocked",
            summary="Manual execution packet written for external operator/provider.",
            evidence_refs=[str(output_path)],
        )

