from __future__ import annotations

import json
import subprocess
from pathlib import Path

from codex_runner import runner as main_runner
from codex_runner.loop_manager.executor import StubExecutorProvider
from codex_runner.loop_manager.runner import build_parser, run_loop


def init_git_repo(repo_root: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "loop@example.com"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Loop Tester"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def write_task(task_path: Path, command: str) -> None:
    task_path.write_text(
        f"""
id: loop-runner-smoke
objective: Verify Pi Loop Manager can plan, inspect, validate, and emit receipt for a docs-only task.
repo_root: .
max_attempts: 3
allowed_paths:
  - docs/handoffs/**
  - .pi/runs/**
forbidden_paths:
  - docs/architecture/adr/accepted/**
  - docs/architecture/00-current-state.md
  - docs/design/tokens/**
acceptance_criteria:
  - A loop receipt is emitted.
  - Gate receipts are emitted for every executed gate.
validation_commands:
  - {command}
operator_review_required_for: []
context_docs:
  - README.md
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_stub_provider_execution() -> None:
    provider = StubExecutorProvider()
    assert provider is not None


def test_validation_command_capture_and_dry_run(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / "README.md").write_text("hello\n", encoding="utf-8")
    (repo_root / "docs" / "handoffs").mkdir(parents=True)

    task_path = repo_root / "task.yaml"
    write_task(task_path, "python3 -c \"print('validated')\"")

    args = build_parser().parse_args(
        [
            "--task",
            str(task_path),
            "--repo-root",
            str(repo_root),
            "--dry-run",
        ]
    )
    receipt = run_loop(args)

    assert receipt.status == "passed"
    run_dir = repo_root / ".pi" / "runs" / receipt.run_id
    receipt_path = run_dir / "receipt.json"
    validation_log = run_dir / "attempt-1" / "validation.log"
    gate_receipts = run_dir / "attempt-1" / "gate-receipts.json"
    assert receipt_path.exists()
    assert validation_log.exists()
    assert gate_receipts.exists()
    assert "validated" in validation_log.read_text(encoding="utf-8")
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["receipt_version"] == "v0"
    assert payload["task_id"] == "loop-runner-smoke"
    assert "docs/handoffs/**" in payload["changed_paths"]
    assert not (repo_root / "docs" / "architecture").exists()


def test_runner_stops_on_forbidden_path(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    init_git_repo(repo_root)
    (repo_root / "README.md").write_text("hello\n", encoding="utf-8")

    task_path = repo_root / "task.yaml"
    write_task(task_path, "python3 -c \"print('validated')\"")
    task_text = task_path.read_text(encoding="utf-8")
    task_text = task_text.replace("docs/handoffs/**", "README.md")
    task_path.write_text(task_text, encoding="utf-8")

    args = build_parser().parse_args(
        [
            "--task",
            str(task_path),
            "--repo-root",
            str(repo_root),
            "--dry-run",
        ]
    )
    receipt = run_loop(args)

    assert receipt.status == "failed"
    assert receipt.stop_reason == "forbidden_path_touched"


def test_runner_dispatches_loop_subcommand(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "README.md").write_text("hello\n", encoding="utf-8")
    task_path = repo_root / "task.yaml"
    write_task(task_path, "python3 -c \"print('validated')\"")

    exit_code = main_runner.main(
        [
            "loop",
            "--task",
            str(task_path),
            "--repo-root",
            str(repo_root),
            "--dry-run",
        ]
    )

    assert exit_code == 0
