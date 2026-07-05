from __future__ import annotations

from pathlib import Path

import pytest

from codex_runner.loop_manager.contracts import (
    GateReceipt,
    LoopManagerError,
    LoopReceipt,
    LoopTask,
    RECEIPT_VERSION_V0,
    RECEIPT_VERSION_V1,
    V1LoopReceipt,
    load_task_spec,
    validate_receipt_payload,
)
from codex_runner.loop_manager.receipts import (
    build_gate_receipt,
    build_loop_receipt,
)


def test_load_task_spec_and_validate(tmp_path: Path) -> None:
    task_path = tmp_path / "task.yaml"
    task_path.write_text(
        """
id: task-1
objective: Prove the loop can load a task.
repo_root: .
max_attempts: 2
allowed_paths:
  - docs/handoffs/**
forbidden_paths:
  - README.md
acceptance_criteria:
  - Receipt emitted
validation_commands:
  - python3 -c "print('ok')"
operator_review_required_for:
  - ui_ux_changes
context_docs:
  - README.md
""".strip()
        + "\n",
        encoding="utf-8",
    )

    task = load_task_spec(task_path)

    assert isinstance(task, LoopTask)
    assert task.id == "task-1"
    assert task.allowed_paths == ["docs/handoffs/**"]


def test_load_task_spec_rejects_missing_fields(tmp_path: Path) -> None:
    task_path = tmp_path / "task.yaml"
    task_path.write_text("id: only-id\n", encoding="utf-8")

    with pytest.raises(LoopManagerError, match="missing required fields"):
        load_task_spec(task_path)


def test_gate_receipt_generation() -> None:
    receipt = build_gate_receipt(
        work_order_id=None,
        task_id="task-1",
        run_id="run-1",
        attempt=1,
        gate_id="planner",
        status="passed",
        summary="ok",
    )

    assert isinstance(receipt, GateReceipt)
    assert receipt.to_dict()["status"] == "passed"


def test_loop_receipt_generation() -> None:
    gate = GateReceipt(
        work_order_id=None,
        task_id="task-1",
        run_id="run-1",
        attempt=1,
        gate_id="planner",
        status="passed",
        summary="ok",
    )
    receipt = build_loop_receipt(
        task_id="task-1",
        run_id="run-1",
        status="passed",
        stop_reason="goal_satisfied",
        attempts=[gate],
        final_summary="done",
        validation_summary="passed",
        changed_paths=[],
        evidence_refs=[],
        operator_review_required=False,
        follow_up_recommendations=[],
    )

    assert isinstance(receipt, LoopReceipt)
    assert receipt.to_dict()["stop_reason"] == "goal_satisfied"
    assert receipt.to_dict()["receipt_version"] == RECEIPT_VERSION_V0


def test_v0_fixture_receipt_validates() -> None:
    fixture = (
        Path(__file__).resolve().parent / "fixtures" / "loop_receipt_v0.json"
    )
    payload = validate_receipt_payload(
        __import__("json").loads(fixture.read_text(encoding="utf-8"))
    )

    assert isinstance(payload, LoopReceipt)
    assert payload.receipt_version == RECEIPT_VERSION_V0


def test_v1_fixture_receipt_validates_as_proposed_envelope() -> None:
    fixture = (
        Path(__file__).resolve().parent / "fixtures" / "loop_receipt_v1.json"
    )
    payload = validate_receipt_payload(
        __import__("json").loads(fixture.read_text(encoding="utf-8"))
    )

    assert isinstance(payload, V1LoopReceipt)
    assert payload.receipt_version == RECEIPT_VERSION_V1
    assert payload.mode_trust_actionability.trust_level == "validation_captured"
