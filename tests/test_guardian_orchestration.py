from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Callable

import pytest

from codex_runner import runner as main_runner
from codex_runner.guardian.plan_pack_validator import validate_plan_pack
from codex_runner.guardian.receipt import write_receipt

REPO_ROOT = Path("/Volumes/Dev_SSD/Codex-Runner")


def sample_plan_pack_path() -> Path:
    return (
        REPO_ROOT
        / "docs"
        / "guardian"
        / "examples"
        / "sample-dry-run-plan-pack"
    )


def make_plan_pack_copy(target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    src = sample_plan_pack_path()
    for path in src.iterdir():
        if path.is_file():
            (target / path.name).write_bytes(path.read_bytes())
    return target


def make_receipt(plan_pack: Path, receipts_dir: Path) -> Path:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    report = validate_plan_pack(plan_pack)
    return write_receipt(
        report,
        command="codexrun guardian validate-plan-pack --write-receipt",
        receipts_dir=receipts_dir,
    )


def _mutate_receipt(receipt_path: Path, fn: Callable[[dict], None]) -> None:
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    fn(data)
    receipt_path.write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )


@pytest.fixture
def repo_local_tmp() -> Path:
    base = REPO_ROOT / ".guardian" / "_orchestration_tests"
    base.mkdir(parents=True, exist_ok=True)
    d = base / f"run-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    d.mkdir()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def plan_pack_and_receipt(repo_local_tmp: Path) -> tuple[Path, Path]:
    plan_pack = make_plan_pack_copy(repo_local_tmp / "pack")
    receipts_dir = repo_local_tmp / "receipts"
    receipt = make_receipt(plan_pack, receipts_dir)
    return plan_pack, receipt


def _run(
    plan_pack: Path,
    receipt: Path,
    *,
    extra: list[str] | None = None,
    monkeypatch: pytest.MonkeyPatch | None = None,
    cwd: Path | None = None,
) -> int:
    if monkeypatch is not None and cwd is not None:
        monkeypatch.chdir(cwd)
    args = [
        "guardian",
        "orchestrate-dry-run",
        "--plan-pack",
        str(plan_pack),
        "--require-receipt",
        str(receipt),
    ]
    if extra:
        args.extend(extra)
    return main_runner.main(args)


def _run_json(
    plan_pack: Path,
    receipt: Path,
    capsys,
) -> tuple[int, dict]:
    exit_code = main_runner.main(
        [
            "guardian",
            "orchestrate-dry-run",
            "--plan-pack",
            str(plan_pack),
            "--require-receipt",
            str(receipt),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    return exit_code, json.loads(captured.out)


def test_orchestrate_dry_run_valid_plan_pack_and_receipt_passes(
    plan_pack_and_receipt: tuple[Path, Path],
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    exit_code = _run(plan_pack, receipt)
    assert exit_code == 0


def test_json_emits_valid_json_only(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 0
    assert payload["orchestration_type"] == "guardian_operated_dry_run"
    assert payload["orchestration_version"] == "v0"
    assert payload["result"] == "pass"


def test_default_human_readable_output_is_concise(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    exit_code = _run(plan_pack, receipt)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Guardian dry-run orchestration preflight: PASS" in captured.out
    assert "Hash verification: PASS" in captured.out
    assert "no Pi Loop" in captured.out


def test_write_orchestration_log_writes_exactly_one_log_under_orchestrations(
    plan_pack_and_receipt: tuple[Path, Path],
    repo_local_tmp: Path,
    monkeypatch,
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    exit_code = _run(
        plan_pack,
        receipt,
        extra=["--write-orchestration-log"],
        monkeypatch=monkeypatch,
        cwd=repo_local_tmp,
    )
    orchestrations = list((repo_local_tmp / ".guardian" / "orchestrations").glob("*.json"))

    assert exit_code == 0
    assert len(orchestrations) == 1
    assert orchestrations[0].parent.name == "orchestrations"


def test_default_run_writes_no_orchestration_log(
    plan_pack_and_receipt: tuple[Path, Path],
    repo_local_tmp: Path,
    monkeypatch,
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    _run(plan_pack, receipt, monkeypatch=monkeypatch, cwd=repo_local_tmp)

    assert not (repo_local_tmp / ".guardian" / "orchestrations").exists()


def _assert_fail_precondition(
    plan_pack_and_receipt: tuple[Path, Path],
    mutator: Callable[[dict], None],
    expected_check: str,
    capsys,
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    _mutate_receipt(receipt, mutator)
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["result"] == "fail"
    assert payload["preconditions"][expected_check] is False


def test_invalid_receipt_type_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d.__setitem__("receipt_type", "wrong"),
        "receipt_type_valid",
        capsys,
    )


def test_invalid_receipt_version_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d.__setitem__("receipt_version", "v9"),
        "receipt_version_valid",
        capsys,
    )


def test_receipt_validation_valid_false_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["validation"].__setitem__("valid", False),
        "receipt_validation_passed",
        capsys,
    )


def test_any_authority_lock_true_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["authority"].__setitem__("plan_execution_allowed", True),
        "authority_locks_false",
        capsys,
    )


def test_approval_granted_true_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["evidence"].__setitem__("approval_granted", True),
        "evidence_flags_non_authoritative",
        capsys,
    )


def test_execution_performed_true_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["evidence"].__setitem__("execution_performed", True),
        "evidence_flags_non_authoritative",
        capsys,
    )


def test_codexify_ingestion_performed_true_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["evidence"].__setitem__("codexify_ingestion_performed", True),
        "evidence_flags_non_authoritative",
        capsys,
    )


def test_durable_mutation_performed_true_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    _assert_fail_precondition(
        plan_pack_and_receipt,
        lambda d: d["evidence"].__setitem__("durable_mutation_performed", True),
        "evidence_flags_non_authoritative",
        capsys,
    )


def test_manifest_hash_mismatch_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    (plan_pack / "README.md").write_text("tampered content\n", encoding="utf-8")
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["preconditions"]["manifest_hashes_match"] is False
    readme = payload["receipt_hash_verification"]["files"]["README.md"]
    assert readme["matches"] is False
    assert readme["actual_sha256"] != readme["expected_sha256"]


def test_missing_required_plan_pack_file_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    (plan_pack / "README.md").unlink()
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["preconditions"]["manifest_hashes_match"] is False
    assert payload["receipt_hash_verification"]["files"]["README.md"]["actual_sha256"] is None


def test_missing_authorization_phrase_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    auth = plan_pack / "AUTHORIZATION.md"
    auth.write_text(
        auth.read_text(encoding="utf-8").replace(
            "dry-run orchestration preparation allowed",
            "dry-run orchestration preparation removed",
        ),
        encoding="utf-8",
    )
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["preconditions"]["authorization_allows_dry_run_orchestration"] is False


def test_boundary_conflict_phrase_fails(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    (plan_pack / "BOUNDARIES.md").write_text(
        "orchestration forbidden\n", encoding="utf-8"
    )
    exit_code, payload = _run_json(plan_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["preconditions"]["boundaries_allow_dry_run_orchestration"] is False


def test_path_outside_repo_boundary_fails(
    plan_pack_and_receipt: tuple[Path, Path], tmp_path: Path, capsys
) -> None:
    _, receipt = plan_pack_and_receipt
    outside_pack = tmp_path / "outside-pack"
    outside_pack.mkdir()
    exit_code, payload = _run_json(outside_pack, receipt, capsys)

    assert exit_code == 1
    assert payload["preconditions"]["repo_boundary_valid"] is False


def test_failure_with_write_orchestration_log_writes_failure_log(
    plan_pack_and_receipt: tuple[Path, Path],
    repo_local_tmp: Path,
    monkeypatch,
    capsys,
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    (plan_pack / "README.md").write_text("tampered\n", encoding="utf-8")
    exit_code = _run(
        plan_pack,
        receipt,
        extra=["--write-orchestration-log", "--json"],
        monkeypatch=monkeypatch,
        cwd=repo_local_tmp,
    )
    _ = capsys.readouterr()
    logs = list((repo_local_tmp / ".guardian" / "orchestrations").glob("*.json"))

    assert exit_code == 1
    assert len(logs) == 1
    record = json.loads(logs[0].read_text(encoding="utf-8"))
    assert record["result"] == "fail"


def test_authority_locks_false_in_pass_and_fail_results(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    _, pass_payload = _run_json(plan_pack, receipt, capsys)

    _mutate_receipt(receipt, lambda d: d["validation"].__setitem__("valid", False))
    _, fail_payload = _run_json(plan_pack, receipt, capsys)

    for payload in (pass_payload, fail_payload):
        assert all(value is False for value in payload["authority"].values())


def test_evidence_says_no_execution_no_piloop_no_codexify_no_mutation(
    plan_pack_and_receipt: tuple[Path, Path], capsys
) -> None:
    plan_pack, receipt = plan_pack_and_receipt
    _, payload = _run_json(plan_pack, receipt, capsys)
    evidence = payload["evidence"]

    assert evidence["execution_performed"] is False
    assert evidence["pi_loop_invoked"] is False
    assert evidence["codexify_ingestion_performed"] is False
    assert evidence["durable_mutation_performed"] is False
    assert evidence["source_mutation_performed"] is False
    assert evidence["approval_granted"] is False
    assert evidence["orchestration_record_only"] is True


def test_gitignore_contains_guardian_orchestrations() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".guardian/orchestrations/" in gitignore
