from __future__ import annotations

import subprocess
import threading
from pathlib import Path

import pytest

from codex_runner import mcp_server


def call(arguments: object, request_id: int = 1) -> dict:
    return mcp_server.handle(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": "codex_runner_campaign_dry_run",
                "arguments": arguments,
            },
        }
    )


def valid_arguments(repo_root: Path) -> dict[str, object]:
    return {
        "repo_root": str(repo_root),
        "audit_prompt_file": "audit.md",
        "audit_schema_file": "audit.schema.json",
        "compiler_prompt_file": "compiler.md",
        "campaign_set_schema_file": "campaign.schema.json",
    }


def test_initialize_and_tool_listing_expose_only_campaign_dry_run() -> None:
    initialized = mcp_server.handle(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    )
    assert initialized["result"]["serverInfo"]["name"] == "codex-runner"

    listed = mcp_server.handle(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    )
    tools = listed["result"]["tools"]
    assert [tool["name"] for tool in tools] == ["codex_runner_campaign_dry_run"]
    serialized = str(tools).lower()
    assert "codex_runner_delegate" not in serialized
    assert "guardian" not in serialized
    assert "pi loop" not in serialized
    assert tools[0]["inputSchema"]["additionalProperties"] is False


@pytest.mark.parametrize(
    "arguments, message",
    [
        ({}, "repo_root"),
        ([], "arguments must be an object"),
        ({"repo_root": "."}, "audit_prompt_file"),
        ({"repo_root": ".", "unexpected": True}, "unsupported arguments"),
        (
            {
                "repo_root": ".",
                "audit_prompt_file": "a",
                "audit_schema_file": "b",
                "compiler_prompt_file": "c",
                "campaign_set_schema_file": "d",
                "passes": 0,
            },
            "passes",
        ),
    ],
)
def test_malformed_or_unsupported_arguments_are_rejected(arguments, message) -> None:
    response = call(arguments)
    assert response["result"]["isError"] is True
    assert message in response["result"]["content"][0]["text"]


def test_nonexistent_repository_is_rejected(tmp_path) -> None:
    arguments = valid_arguments(tmp_path / "missing")
    response = call(arguments)
    assert response["result"]["isError"] is True
    assert "repo_root is not a directory" in response["result"]["content"][0]["text"]


def test_runner_cli_is_launched_in_forced_dry_run(monkeypatch, tmp_path) -> None:
    observed: list[list[str]] = []

    def fake_run(command, **kwargs):
        observed.append(command)
        return subprocess.CompletedProcess(command, 0, "runner output", "runner warning")

    monkeypatch.setattr(mcp_server.shutil, "which", lambda name: "/bin/codexrun")
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)
    response = call(valid_arguments(tmp_path))
    result = response["result"]["structuredContent"]

    assert observed and observed[0][0] == "/bin/codexrun"
    assert "--dry-run" in observed[0]
    assert "--execute" not in observed[0]
    assert Path(observed[0][0]).name not in {"codex", "claude", "pi"}
    assert result["classification"] == "success"
    assert result["authoritative_receipt_created_by_adapter"] is False
    assert not (tmp_path / ".codex-runner-mcp").exists()


def test_python_module_fallback_is_supported(monkeypatch, tmp_path) -> None:
    observed: list[list[str]] = []

    def fake_run(command, **kwargs):
        observed.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(mcp_server.shutil, "which", lambda name: None)
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)
    call(valid_arguments(tmp_path))
    assert observed[0][:3] == [mcp_server.sys.executable, "-m", "codex_runner"]
    assert "--dry-run" in observed[0]


def test_output_is_bounded_and_nonzero_exit_is_failure(monkeypatch, tmp_path) -> None:
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            9,
            "o" * (mcp_server.OUTPUT_LIMIT + 10),
            "e" * (mcp_server.OUTPUT_LIMIT + 20),
        )

    monkeypatch.setattr(mcp_server.shutil, "which", lambda name: "/bin/codexrun")
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)
    result = call(valid_arguments(tmp_path))["result"]["structuredContent"]
    assert result["classification"] == "failure"
    assert result["exit_code"] == 9
    assert len(result["stdout_summary"]["text"]) == mcp_server.OUTPUT_LIMIT
    assert len(result["stderr_summary"]["text"]) == mcp_server.OUTPUT_LIMIT
    assert result["stdout_summary"]["truncated"] is True
    assert result["stderr_summary"]["truncated"] is True


def test_runner_generated_artifacts_are_referenced(monkeypatch, tmp_path) -> None:
    def fake_run(command, **kwargs):
        artifact = tmp_path / "docs/_campaign_runs/2026-07-19/run_meta.json"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("{}\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(mcp_server.shutil, "which", lambda name: "/bin/codexrun")
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)
    result = call(valid_arguments(tmp_path))["result"]["structuredContent"]
    assert result["runner_artifact_references"] == [
        "docs/_campaign_runs/2026-07-19/run_meta.json"
    ]


def test_concurrent_run_for_same_repository_is_rejected(monkeypatch, tmp_path) -> None:
    entered = threading.Event()
    release = threading.Event()

    def blocking_run(command, **kwargs):
        entered.set()
        assert release.wait(timeout=5)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(mcp_server.shutil, "which", lambda name: "/bin/codexrun")
    monkeypatch.setattr(mcp_server.subprocess, "run", blocking_run)
    first_response: list[dict] = []
    thread = threading.Thread(
        target=lambda: first_response.append(call(valid_arguments(tmp_path), 10))
    )
    thread.start()
    assert entered.wait(timeout=5)
    try:
        second = call(valid_arguments(tmp_path), 11)
        assert second["result"]["isError"] is True
        assert "already active" in second["result"]["content"][0]["text"]
    finally:
        release.set()
        thread.join(timeout=5)
    assert not thread.is_alive()
    assert first_response[0]["result"]["structuredContent"]["classification"] == "success"


def test_unknown_and_removed_tools_are_rejected() -> None:
    for name in ("codex_runner_delegate", "codex_runner_receipt", "pi", "guardian"):
        response = mcp_server.handle(
            {
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {"name": name, "arguments": {}},
            }
        )
        assert response["error"]["code"] == -32602
