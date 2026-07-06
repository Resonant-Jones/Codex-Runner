from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from codex_runner import runner as main_runner
from codex_runner.guardian.plan_pack_validator import (
    AUTHORITY_LOCKS,
    render_report,
    validate_plan_pack,
)
from codex_runner.guardian.session_log import write_session_log
from codex_runner.guardian.receipt import write_receipt


def sample_plan_pack_path() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "guardian"
        / "examples"
        / "sample-dry-run-plan-pack"
    )


def copy_plan_pack(tmp_path: Path) -> Path:
    source = sample_plan_pack_path()
    target = tmp_path / "plan-pack"
    target.mkdir()
    for path in source.iterdir():
        if path.is_file():
            (target / path.name).write_text(
                path.read_text(encoding="utf-8"), encoding="utf-8"
            )
    return target


def fixture_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / name


def snapshot_payload(name: str) -> dict[str, object]:
    return json.loads(fixture_path(name).read_text(encoding="utf-8"))


def normalize_plan_pack_path(payload: dict[str, object]) -> dict[str, object]:
    normalized = dict(payload)
    path = normalized.get("plan_pack_path")
    if isinstance(path, str):
        normalized["plan_pack_path"] = Path(path).name
    return normalized


def test_sample_plan_pack_validates_successfully() -> None:
    report = validate_plan_pack(sample_plan_pack_path())

    assert report.valid is True
    assert report.task_spec_parses is True
    assert report.task_spec_mode_is_dry_run is True
    assert report.task_spec_required_fields_present is True
    assert report.escalation_banner_present is True


def test_missing_required_file_fails_validation(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "GOALS.md").unlink()

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.required_files["GOALS.md"] is False
    assert any("GOALS.md" in issue.message for issue in report.issues)


def test_missing_escalation_banner_fails_validation(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    escalation = plan_pack / "ESCALATION.md"
    escalation.write_text(
        escalation.read_text(encoding="utf-8").replace(
            "FLAG### HUMAN OPERATOR DECISION REQUIRED",
            "HUMAN OPERATOR DECISION REQUIRED",
        ),
        encoding="utf-8",
    )

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.escalation_banner_present is False


def test_task_spec_must_parse(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "TASK_SPEC.yaml").write_text("task_id: [\n", encoding="utf-8")

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.task_spec_parses is False


def test_task_spec_must_include_required_fields(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    payload = yaml.safe_load((plan_pack / "TASK_SPEC.yaml").read_text(encoding="utf-8"))
    payload.pop("expected_artifacts")
    (plan_pack / "TASK_SPEC.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.task_spec_required_fields_present is False
    assert any("expected_artifacts" in issue.message for issue in report.issues)


def test_mode_other_than_dry_run_fails_validation(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    payload = yaml.safe_load((plan_pack / "TASK_SPEC.yaml").read_text(encoding="utf-8"))
    payload["mode"] = "execute"
    (plan_pack / "TASK_SPEC.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.task_spec_mode_is_dry_run is False


def test_missing_forbidden_codexify_main_path_fails_validation(
    tmp_path: Path,
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    boundaries = plan_pack / "BOUNDARIES.md"
    boundaries.write_text(
        boundaries.read_text(encoding="utf-8").replace(
            "/Volumes/Dev_SSD/Codexify-main", "/Volumes/Dev_SSD/Codexify-main-removed"
        ),
        encoding="utf-8",
    )
    task_spec = plan_pack / "TASK_SPEC.yaml"
    task_spec.write_text(
        task_spec.read_text(encoding="utf-8").replace(
            "/Volumes/Dev_SSD/Codexify-main", "/Volumes/Dev_SSD/Codexify-main-removed"
        ),
        encoding="utf-8",
    )

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert report.forbidden_path_checks["/Volumes/Dev_SSD/Codexify-main"] is False


def test_missing_forbidden_codexify_core_path_fails_validation(
    tmp_path: Path,
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    boundaries = plan_pack / "BOUNDARIES.md"
    boundaries.write_text(
        boundaries.read_text(encoding="utf-8").replace(
            "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core",
            "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core-removed",
        ),
        encoding="utf-8",
    )
    task_spec = plan_pack / "TASK_SPEC.yaml"
    task_spec.write_text(
        task_spec.read_text(encoding="utf-8").replace(
            "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core",
            "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core-removed",
        ),
        encoding="utf-8",
    )

    report = validate_plan_pack(plan_pack)

    assert report.valid is False
    assert (
        report.forbidden_path_checks[
            "/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core"
        ]
        is False
    )


def test_validation_command_exits_zero_for_valid_sample_pack(capsys) -> None:
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Guardian Plan Pack Validation Report" in captured.out
    assert "Result:" in captured.out
    assert "  pass" in captured.out


def test_validation_command_exits_one_for_invalid_pack(
    tmp_path: Path, capsys
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "README.md").unlink()

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "README.md: missing" in captured.out
    assert "  fail" in captured.out


def test_validator_does_not_mutate_plan_pack_files(tmp_path: Path) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    before = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    report = validate_plan_pack(plan_pack)
    rendered = render_report(report)
    after = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    assert report.valid is True
    assert "Guardian Plan Pack Validation Report" in rendered
    assert before == after


def test_json_dict_for_valid_sample_pack() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    assert payload["valid"] is True
    assert payload["result"] == "pass"
    assert str(sample_plan_pack_path()) == payload["plan_pack_path"]


def test_json_dict_required_file_statuses_present() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    required_files = payload["required_files"]
    assert isinstance(required_files, dict)
    assert set(required_files.keys()) == {
        "README.md",
        "PLAN.md",
        "GOALS.md",
        "BOUNDARIES.md",
        "AUTHORIZATION.md",
        "ESCALATION.md",
        "SESSION_LOG.md",
        "TASK_SPEC.yaml",
    }
    assert all(required_files.values())


def test_json_dict_boundary_checks_present() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    boundary_checks = payload["boundary_checks"]
    assert isinstance(boundary_checks, dict)
    assert all(boundary_checks.values())
    forbidden_path_checks = payload["forbidden_path_checks"]
    assert all(forbidden_path_checks.values())


def test_json_dict_task_spec_checks_present() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    task_spec = payload["task_spec"]
    assert task_spec["yaml_parses"] is True
    assert task_spec["mode_is_dry_run"] is True
    assert task_spec["required_fields_present"] is True


def test_json_dict_escalation_banner_check_present() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    assert payload["escalation"]["flag_banner_present"] is True


def test_json_dict_all_authority_locks_are_false() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    payload = report.to_json_dict()

    authority = payload["authority"]
    assert set(authority.keys()) == set(AUTHORITY_LOCKS.keys())
    assert all(value is False for value in authority.values())


def test_json_cli_dispatch_emits_valid_json_for_sample_pack(capsys) -> None:
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["valid"] is True
    assert payload["result"] == "pass"
    assert payload["plan_pack_path"].endswith("sample-dry-run-plan-pack")


def test_json_cli_dispatch_emits_valid_json_for_invalid_pack(
    tmp_path: Path, capsys
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "README.md").unlink()

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["valid"] is False
    assert payload["result"] == "fail"
    assert "README.md" in payload["reason"]
    assert payload["required_files"]["README.md"] is False
    assert payload["issues"][0]["section"] == "Required files"


def test_json_cli_does_not_mutate_plan_pack_files(tmp_path: Path, capsys) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    before = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--json",
        ]
    )
    _ = capsys.readouterr()
    after = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    assert exit_code == 0
    assert before == after


def test_human_readable_output_still_works_for_sample_pack(capsys) -> None:
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Guardian Plan Pack Validation Report" in captured.out
    assert "  pass" in captured.out


def test_valid_sample_pack_json_matches_snapshot_fixture() -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    raw = report.to_json_dict()
    expected = snapshot_payload(
        "guardian_plan_pack_validator_json_valid.json"
    )

    assert raw["plan_pack_path"] != expected["plan_pack_path"]
    actual = normalize_plan_pack_path(raw)

    assert actual == expected
    assert actual["valid"] is True
    assert actual["result"] == "pass"
    assert set(actual["authority"].keys()) == set(AUTHORITY_LOCKS.keys())
    assert all(value is False for value in actual["authority"].values())


def test_invalid_sample_pack_json_matches_snapshot_fixture(
    tmp_path: Path,
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    escalation = plan_pack / "ESCALATION.md"
    escalation.write_text(
        escalation.read_text(encoding="utf-8").replace(
            "FLAG### HUMAN OPERATOR DECISION REQUIRED",
            "HUMAN OPERATOR DECISION REQUIRED",
        ),
        encoding="utf-8",
    )

    report = validate_plan_pack(plan_pack)
    raw = report.to_json_dict()
    expected = snapshot_payload(
        "guardian_plan_pack_validator_json_invalid.json"
    )

    assert raw["plan_pack_path"] != expected["plan_pack_path"]
    actual = normalize_plan_pack_path(raw)

    assert actual == expected
    assert actual["valid"] is False
    assert actual["result"] == "fail"
    assert actual["reason"] == "Missing required escalation FLAG### banner"
    assert actual["escalation"]["flag_banner_present"] is False
    assert set(actual["authority"].keys()) == set(AUTHORITY_LOCKS.keys())
    assert all(value is False for value in actual["authority"].values())


def _read_single_session_log(sessions_dir: Path) -> dict[str, object]:
    logs = sorted(sessions_dir.glob("*.json"))
    assert len(logs) == 1, f"expected exactly one session log, found {len(logs)}"
    return json.loads(logs[0].read_text(encoding="utf-8"))


def test_default_validation_writes_no_session_log(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
        ]
    )

    assert exit_code == 0
    assert not (tmp_path / ".guardian").exists()


def test_write_session_log_creates_exactly_one_log_under_sessions_dir(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-session-log",
        ]
    )
    sessions_dir = tmp_path / ".guardian" / "sessions"
    logs = sorted(sessions_dir.glob("*.json"))

    assert exit_code == 0
    assert len(logs) == 1
    assert logs[0].parent.name == "sessions"


def test_session_log_includes_validation_result_and_command(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-session-log",
        ]
    )
    log = _read_single_session_log(tmp_path / ".guardian" / "sessions")

    assert log["session_type"] == "guardian_plan_pack_validation"
    assert log["schema_version"] == "v0"
    assert log["validation"]["valid"] is True
    assert log["validation"]["result"] == "pass"
    assert isinstance(log["command"], str)
    assert log["command"].startswith("codexrun guardian validate-plan-pack")


def test_session_log_authority_locks_all_false(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-session-log",
        ]
    )
    log = _read_single_session_log(tmp_path / ".guardian" / "sessions")

    assert set(log["authority"].keys()) == set(AUTHORITY_LOCKS.keys())
    assert all(value is False for value in log["authority"].values())


def test_session_log_does_not_mutate_plan_pack(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    before = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }
    monkeypatch.chdir(tmp_path)

    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-session-log",
        ]
    )
    after = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    assert before == after


def test_json_with_write_session_log_emits_valid_json(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--json",
            "--write-session-log",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["valid"] is True
    assert (
        len(list((tmp_path / ".guardian" / "sessions").glob("*.json"))) == 1
    )


def test_invalid_pack_with_session_log_exits_one_and_writes_failure_log(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "README.md").unlink()
    monkeypatch.chdir(tmp_path)

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-session-log",
        ]
    )
    log = _read_single_session_log(tmp_path / ".guardian" / "sessions")

    assert exit_code == 1
    assert log["validation"]["valid"] is False
    assert log["validation"]["result"] == "fail"
    assert "README.md" in log["validation"]["reason"]
    assert all(value is False for value in log["authority"].values())


def test_write_session_log_module_writes_to_specified_dir(
    tmp_path: Path,
) -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    sessions_dir = tmp_path / ".guardian" / "sessions"

    path = write_session_log(
        report,
        command="codexrun guardian validate-plan-pack",
        sessions_dir=sessions_dir,
    )

    assert path.parent == sessions_dir
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["session_type"] == "guardian_plan_pack_validation"
    assert payload["validation"]["valid"] is True


def test_gitignore_contains_guardian_sessions() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")

    assert ".guardian/sessions/" in gitignore


def _read_single_receipt(receipts_dir: Path) -> dict[str, object]:
    logs = sorted(receipts_dir.glob("*.json"))
    assert len(logs) == 1, f"expected exactly one receipt, found {len(logs)}"
    return json.loads(logs[0].read_text(encoding="utf-8"))


def test_default_validation_writes_no_receipt(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
        ]
    )

    assert exit_code == 0
    assert not (tmp_path / ".guardian").exists()


def test_write_receipt_creates_exactly_one_under_receipts_dir(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipts_dir = tmp_path / ".guardian" / "receipts"
    receipts = sorted(receipts_dir.glob("*.json"))

    assert exit_code == 0
    assert len(receipts) == 1
    assert receipts[0].parent.name == "receipts"


def test_receipt_type_version_and_validation_result(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")

    assert receipt["receipt_type"] == "guardian_plan_pack_validation"
    assert receipt["receipt_version"] == "v0"
    assert receipt["validation"]["valid"] is True
    assert receipt["validation"]["result"] == "pass"
    assert receipt["command"].startswith("codexrun guardian validate-plan-pack")


def test_receipt_includes_report_fields_from_validator(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    report = receipt["report"]

    assert set(report["required_files"].keys()) == {
        "README.md",
        "PLAN.md",
        "GOALS.md",
        "BOUNDARIES.md",
        "AUTHORIZATION.md",
        "ESCALATION.md",
        "SESSION_LOG.md",
        "TASK_SPEC.yaml",
    }
    assert all(report["required_files"].values())
    assert all(report["boundary_checks"].values())
    assert report["task_spec"]["mode_is_dry_run"] is True
    assert report["escalation"]["flag_banner_present"] is True
    assert report["issues"] == []


def test_receipt_authority_locks_all_false(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")

    assert set(receipt["authority"].keys()) == set(AUTHORITY_LOCKS.keys())
    assert all(value is False for value in receipt["authority"].values())


def test_receipt_evidence_block_is_not_authority(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    evidence = receipt["evidence"]

    assert evidence["source"] == "guardian_plan_pack_validator"
    assert evidence["evidence_not_authority"] is True
    assert evidence["approval_granted"] is False
    assert evidence["execution_performed"] is False
    assert evidence["codexify_ingestion_performed"] is False
    assert evidence["durable_mutation_performed"] is False


def test_receipt_does_not_mutate_plan_pack(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    before = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }
    monkeypatch.chdir(tmp_path)

    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    after = {
        path.name: path.read_text(encoding="utf-8") for path in plan_pack.iterdir()
    }

    assert before == after


def test_json_with_write_receipt_emits_valid_json(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--json",
            "--write-receipt",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["valid"] is True
    assert (
        len(list((tmp_path / ".guardian" / "receipts").glob("*.json"))) == 1
    )


def test_write_session_log_and_write_receipt_both_written(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-session-log",
            "--write-receipt",
        ]
    )
    sessions = sorted((tmp_path / ".guardian" / "sessions").glob("*.json"))
    receipts = sorted((tmp_path / ".guardian" / "receipts").glob("*.json"))

    assert exit_code == 0
    assert len(sessions) == 1
    assert len(receipts) == 1


def test_invalid_pack_with_receipt_exits_one_and_writes_failure_receipt(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "README.md").unlink()
    monkeypatch.chdir(tmp_path)

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")

    assert exit_code == 1
    assert receipt["validation"]["valid"] is False
    assert receipt["validation"]["result"] == "fail"
    assert "README.md" in receipt["validation"]["reason"]
    assert all(value is False for value in receipt["authority"].values())
    assert receipt["evidence"]["approval_granted"] is False


def test_write_receipt_module_writes_to_specified_dir(
    tmp_path: Path,
) -> None:
    report = validate_plan_pack(sample_plan_pack_path())
    receipts_dir = tmp_path / ".guardian" / "receipts"

    path = write_receipt(
        report,
        command="codexrun guardian validate-plan-pack",
        receipts_dir=receipts_dir,
    )

    assert path.parent == receipts_dir
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["receipt_type"] == "guardian_plan_pack_validation"


def test_gitignore_contains_guardian_receipts() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")

    assert ".guardian/receipts/" in gitignore


_REQUIRED_FILE_NAMES = {
    "README.md",
    "PLAN.md",
    "GOALS.md",
    "BOUNDARIES.md",
    "AUTHORIZATION.md",
    "ESCALATION.md",
    "SESSION_LOG.md",
    "TASK_SPEC.yaml",
}
_HEX256 = re.compile(r"^[0-9a-f]{64}$")


def test_receipt_manifest_has_sha256_algorithm_and_required_files(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    manifest = receipt["plan_pack_manifest"]

    assert manifest["hash_algorithm"] == "sha256"
    assert set(manifest["files"].keys()) == _REQUIRED_FILE_NAMES


def test_receipt_manifest_present_files_have_lowercase_hex_and_int_size(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(sample_plan_pack_path()),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    files = receipt["plan_pack_manifest"]["files"]

    for name, entry in files.items():
        assert entry["present"] is True, name
        assert isinstance(entry["sha256"], str), name
        assert _HEX256.fullmatch(entry["sha256"]), name
        assert entry["sha256"] == entry["sha256"].lower(), name
        assert isinstance(entry["size_bytes"], int), name
        assert entry["size_bytes"] >= 0, name


def test_receipt_manifest_hashes_match_independent_sha256(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    monkeypatch.chdir(tmp_path)
    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    files = receipt["plan_pack_manifest"]["files"]

    for name in _REQUIRED_FILE_NAMES:
        data = (plan_pack / name).read_bytes()
        assert files[name]["sha256"] == hashlib.sha256(data).hexdigest(), name
        assert files[name]["size_bytes"] == len(data), name


def test_receipt_manifest_hash_changes_when_file_changes(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    monkeypatch.chdir(tmp_path)

    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    first_receipts = sorted((tmp_path / ".guardian" / "receipts").glob("*.json"))
    first_hash = json.loads(first_receipts[-1].read_text(encoding="utf-8"))[
        "plan_pack_manifest"
    ]["files"]["README.md"]["sha256"]

    (plan_pack / "README.md").write_text(
        "changed content for hash delta\n", encoding="utf-8"
    )

    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    second_receipts = sorted((tmp_path / ".guardian" / "receipts").glob("*.json"))
    second_hash = json.loads(second_receipts[-1].read_text(encoding="utf-8"))[
        "plan_pack_manifest"
    ]["files"]["README.md"]["sha256"]

    assert first_hash != second_hash


def test_invalid_pack_receipt_manifest_hashes_present_files_and_nulls_missing(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    (plan_pack / "README.md").unlink()
    monkeypatch.chdir(tmp_path)

    exit_code = main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    receipt = _read_single_receipt(tmp_path / ".guardian" / "receipts")
    files = receipt["plan_pack_manifest"]["files"]

    assert exit_code == 1
    assert files["README.md"]["present"] is False
    assert files["README.md"]["sha256"] is None
    assert files["README.md"]["size_bytes"] is None
    assert files["PLAN.md"]["present"] is True
    assert _HEX256.fullmatch(files["PLAN.md"]["sha256"])


def test_receipt_writing_does_not_mutate_plan_pack_files(
    tmp_path: Path, monkeypatch
) -> None:
    plan_pack = copy_plan_pack(tmp_path)
    before = {
        path.name: path.read_bytes() for path in plan_pack.iterdir()
    }
    monkeypatch.chdir(tmp_path)

    main_runner.main(
        [
            "guardian",
            "validate-plan-pack",
            "--path",
            str(plan_pack),
            "--write-receipt",
        ]
    )
    after = {path.name: path.read_bytes() for path in plan_pack.iterdir()}

    assert before == after
