from __future__ import annotations

import json
from pathlib import Path

from codex_runner.loop_manager import runner as loop_runner
from codex_runner.loop_manager.receipt_report import (
    classify_receipt,
    render_report,
)


def fixture_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / name


def snapshot_payload(name: str) -> dict[str, object]:
    return json.loads(fixture_path(name).read_text(encoding="utf-8"))


def normalize_receipt_path(payload: dict[str, object], expected_name: str) -> dict[str, object]:
    normalized = dict(payload)
    receipt_path = normalized.get("receipt_path")
    if isinstance(receipt_path, str):
        normalized["receipt_path"] = Path(receipt_path).name
    expected = dict(snapshot_payload(expected_name))
    expected_path = expected.get("receipt_path")
    if isinstance(expected_path, str):
        expected["receipt_path"] = Path(expected_path).name
    return {"actual": normalized, "expected": expected}


def test_valid_v0_fixture_reports_blocked_ingestion_readiness() -> None:
    report = classify_receipt(fixture_path("loop_receipt_v0.json"))

    assert report.schema_valid is True
    assert report.version == "v0"
    assert report.codexify_ingestion_readiness == "blocked"
    assert report.evidence_posture == "attached_evidence"
    text = render_report(report)
    assert "version: v0" in text
    assert "structured validation outputs" in text


def test_valid_v1_fixture_reports_review_required_or_blocked() -> None:
    report = classify_receipt(fixture_path("loop_receipt_v1.json"))

    assert report.schema_valid is True
    assert report.version == "v1"
    assert report.evidence_posture == "proof_envelope_candidate"
    assert report.codexify_ingestion_readiness == "blocked"
    assert "work_order_id" in report.missing_proof_fields


def test_malformed_receipt_reports_schema_invalid(tmp_path: Path) -> None:
    receipt = tmp_path / "bad.json"
    receipt.write_text("{not-json}\n", encoding="utf-8")

    try:
        classify_receipt(receipt)
    except Exception as exc:  # pragma: no cover - defensive
        raise AssertionError(f"classify_receipt should not raise: {exc}") from exc

    exit_code = loop_runner.main(["report", "--receipt", str(receipt)])
    assert exit_code == 1


def test_missing_receipt_version_reports_unknown_invalid(tmp_path: Path) -> None:
    receipt = tmp_path / "missing-version.json"
    payload = json.loads(fixture_path("loop_receipt_v0.json").read_text(encoding="utf-8"))
    payload.pop("receipt_version")
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = classify_receipt(receipt)

    assert report.schema_valid is False
    assert report.version == "unknown"
    assert "receipt_version" in report.missing_proof_fields


def test_elevated_trust_level_without_reviewer_evidence_is_flagged(
    tmp_path: Path,
) -> None:
    receipt = tmp_path / "v1-elevated.json"
    payload = json.loads(fixture_path("loop_receipt_v1.json").read_text(encoding="utf-8"))
    payload["identity"]["work_order_id"] = "wo-123"
    payload["mode_trust_actionability"]["trust_level"] = "operator_reviewed"
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = classify_receipt(receipt)

    assert report.schema_valid is True
    assert any(
        "trust_level=operator_reviewed requires reviewer, reviewed_at, and reviewer_decision."
        == warning
        for warning in report.authority_warnings
    )
    assert report.codexify_ingestion_readiness == "blocked"


def test_report_command_does_not_mutate_receipt_file(tmp_path: Path) -> None:
    receipt = tmp_path / "copy.json"
    original = fixture_path("loop_receipt_v0.json").read_text(encoding="utf-8")
    receipt.write_text(original, encoding="utf-8")

    before = receipt.read_text(encoding="utf-8")
    exit_code = loop_runner.main(["report", "--receipt", str(receipt)])
    after = receipt.read_text(encoding="utf-8")

    assert exit_code == 0
    assert before == after


def test_report_command_supports_v1_fixture() -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v1.json"))]
    )
    assert exit_code == 0


def test_human_readable_report_still_works(capsys) -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v0.json"))]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pi Loop Receipt Compatibility Report" in captured.out
    assert "version: v0" in captured.out


def test_json_report_for_v0_fixture(capsys) -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v0.json")), "--json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["receipt_version"] == "v0"
    assert payload["schema_valid"] is True
    assert payload["codexify_ingestion_readiness"] == "blocked"
    assert payload["durable_action_allowed"] is False
    assert payload["lifecycle_mutation_allowed"] is False
    assert payload["ingestion_performed"] is False
    assert payload["receipt_path"].endswith("loop_receipt_v0.json")


def test_json_report_for_v1_fixture(capsys) -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v1.json")), "--json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["receipt_version"] == "v1"
    assert payload["schema_valid"] is True
    assert payload["durable_action_allowed"] is False
    assert payload["lifecycle_mutation_allowed"] is False
    assert payload["ingestion_performed"] is False
    assert payload["receipt_path"].endswith("loop_receipt_v1.json")


def test_json_report_does_not_mutate_receipt_file(tmp_path: Path, capsys) -> None:
    receipt = tmp_path / "copy.json"
    original = fixture_path("loop_receipt_v1.json").read_text(encoding="utf-8")
    receipt.write_text(original, encoding="utf-8")

    before = receipt.read_text(encoding="utf-8")
    exit_code = loop_runner.main(["report", "--receipt", str(receipt), "--json"])
    _ = capsys.readouterr()
    after = receipt.read_text(encoding="utf-8")

    assert exit_code == 0
    assert before == after


def test_v0_json_report_matches_snapshot_fixture(capsys) -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v0.json")), "--json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    normalized = normalize_receipt_path(payload, "receipt_report_json_v0.json")

    assert exit_code == 0
    assert normalized["actual"] == normalized["expected"]


def test_v1_json_report_matches_snapshot_fixture(capsys) -> None:
    exit_code = loop_runner.main(
        ["report", "--receipt", str(fixture_path("loop_receipt_v1.json")), "--json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    normalized = normalize_receipt_path(payload, "receipt_report_json_v1.json")

    assert exit_code == 0
    assert normalized["actual"] == normalized["expected"]
