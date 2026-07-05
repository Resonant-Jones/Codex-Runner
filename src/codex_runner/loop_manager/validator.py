from __future__ import annotations

import subprocess
from pathlib import Path

from .contracts import ValidationResult


def run_validation_commands(
    *,
    commands: list[str],
    repo_root: Path,
    log_path: Path,
) -> ValidationResult:
    command_results: list[dict[str, object]] = []
    logs: list[str] = []
    overall_ok = True
    for command in commands:
        result = subprocess.run(
            command,
            cwd=str(repo_root),
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        command_results.append(
            {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        logs.append(f"$ {command}\n")
        if result.stdout:
            logs.append(result.stdout)
            if not result.stdout.endswith("\n"):
                logs.append("\n")
        if result.stderr:
            logs.append(result.stderr)
            if not result.stderr.endswith("\n"):
                logs.append("\n")
        overall_ok = overall_ok and result.returncode == 0

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("".join(logs), encoding="utf-8")
    summary = (
        "All validation commands passed."
        if overall_ok
        else "One or more validation commands failed."
    )
    return ValidationResult(
        status="passed" if overall_ok else "failed",
        summary=summary,
        command_results=command_results,
        evidence_refs=[str(log_path)],
    )

