from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pytest

from codex_runner import mcp_server, runner


def completed(command: list[str], returncode: int, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def test_detects_output_schema_capability(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runner, "shutil_which", lambda binary: "/usr/local/bin/codex")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return completed(command, 0, "codex-cli compatible\n")
        return completed(command, 0, "Options:\n  --output-schema <FILE>\n")

    monkeypatch.setattr(runner, "run_cmd", fake_run)
    capability = runner.inspect_codex_cli_capability(tmp_path)
    assert capability.executable == "/usr/local/bin/codex"
    assert capability.version == "codex-cli compatible"
    assert capability.supports_output_schema is True
    assert capability.inspection_command == ("codex", "exec", "--help")


def test_detects_absent_output_schema_capability(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runner, "shutil_which", lambda binary: "/opt/homebrew/bin/codex")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return completed(command, 0, "codex-cli 0.36.0\n")
        return completed(
            command,
            0,
            "Options:\n  --json\n  --output-last-message <LAST_MESSAGE_FILE>\n",
        )

    monkeypatch.setattr(runner, "run_cmd", fake_run)
    capability = runner.inspect_codex_cli_capability(tmp_path)
    assert capability.version == "codex-cli 0.36.0"
    assert capability.supports_output_schema is False
    assert "--output-last-message" in capability.inspection_output


def test_capability_name_in_prose_is_not_accepted(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runner, "shutil_which", lambda binary: "/bin/codex")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return completed(command, 0, "codex-cli unknown\n")
        return completed(command, 0, "This build does not support --output-schema.\n")

    monkeypatch.setattr(runner, "run_cmd", fake_run)
    capability = runner.inspect_codex_cli_capability(tmp_path)
    assert capability.supports_output_schema is False


@pytest.mark.parametrize(
    "returncode, stdout, stderr",
    [
        (0, "", ""),
        (2, "", "malformed invocation"),
    ],
)
def test_malformed_or_failed_help_fails_closed(
    monkeypatch, tmp_path, returncode, stdout, stderr
) -> None:
    monkeypatch.setattr(runner, "shutil_which", lambda binary: "/bin/codex")

    def fake_run(command, **kwargs):
        if command == ["codex", "--version"]:
            return completed(command, 0, "codex-cli unknown\n")
        return completed(command, returncode, stdout, stderr)

    monkeypatch.setattr(runner, "run_cmd", fake_run)
    capability = runner.inspect_codex_cli_capability(tmp_path)
    assert capability.supports_output_schema is False
    assert capability.inspection_exit_code == returncode


def test_missing_codex_executable_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(runner, "shutil_which", lambda binary: None)
    with pytest.raises(runner.RunnerError) as excinfo:
        runner.inspect_codex_cli_capability(tmp_path)
    message = str(excinfo.value)
    assert "detected_version: unavailable" in message
    assert "missing_required_capability: --output-schema" in message
    assert "capability_inspection_command: codex exec --help" in message
    assert "provider_execution_occurred: false" in message


def test_compatibility_error_contains_required_fields(monkeypatch, tmp_path) -> None:
    capability = runner.CodexCliCapability(
        executable="/opt/homebrew/bin/codex",
        version="codex-cli 0.36.0",
        inspection_command=("codex", "exec", "--help"),
        inspection_exit_code=0,
        supports_output_schema=False,
        inspection_output="--json\n--output-last-message",
    )
    monkeypatch.setattr(runner, "inspect_codex_cli_capability", lambda *args: capability)
    with pytest.raises(runner.RunnerError) as excinfo:
        runner.ensure_codex_cli_compatible(tmp_path)
    message = str(excinfo.value)
    assert "detected_version: codex-cli 0.36.0" in message
    assert "missing_required_capability: --output-schema" in message
    assert "capability_inspection_command: codex exec --help" in message
    assert "capability_inspection_exit_code: 0" in message
    assert "codex --upgrade" in message
    assert "provider_execution_occurred: false" in message


def test_main_stops_before_provider_or_state_transition(monkeypatch, tmp_path) -> None:
    args = argparse.Namespace(
        repo_root=tmp_path,
        debug=False,
        provider="codex",
        base_ref="HEAD",
    )
    events: list[str] = []
    monkeypatch.setattr(runner, "resolve_entry_argv", lambda argv: ["bounded"])
    monkeypatch.setattr(runner, "parse_args", lambda argv: args)
    monkeypatch.setattr(runner, "ensure_repo_root", lambda *args: None)
    monkeypatch.setattr(runner, "ensure_provider_available", lambda *args: "/bin/codex")
    monkeypatch.setattr(
        runner,
        "ensure_codex_cli_compatible",
        lambda *args: (_ for _ in ()).throw(runner.RunnerError("incompatible")),
    )
    monkeypatch.setattr(runner, "git_resolve_ref", lambda *args: events.append("git"))
    monkeypatch.setattr(runner, "run_provider_exec", lambda *args, **kwargs: events.append("provider"))
    monkeypatch.setattr(runner, "append_transition", lambda *args, **kwargs: events.append("transition"))
    monkeypatch.setattr(runner, "run_pass", lambda *args, **kwargs: events.append("pass"))

    with pytest.raises(runner.RunnerError, match="incompatible"):
        runner.main(["bounded"])
    assert events == []
    assert not (tmp_path / runner.STATE_TRANSITIONS_PATH).exists()


def test_codex_command_uses_required_schema_capability(monkeypatch, tmp_path) -> None:
    observed: list[list[str]] = []

    def fake_run(command, **kwargs):
        observed.append(command)
        return completed(command, 0)

    monkeypatch.setattr(runner, "run_cmd", fake_run)
    runner.run_codex_exec(
        tmp_path,
        prompt_text="prompt",
        output_schema=tmp_path / "schema.json",
        output_path=tmp_path / "output.json",
        model="model-id",
        configs=["reasoning=high"],
        debug=False,
    )
    assert observed == [
        [
            "codex",
            "--model",
            "model-id",
            "--config",
            "reasoning=high",
            "exec",
            "--output-schema",
            str(tmp_path / "schema.json"),
            "-o",
            str(tmp_path / "output.json"),
            "prompt",
        ]
    ]


def test_invalid_structured_task_output_does_not_return_result(monkeypatch, tmp_path) -> None:
    def fake_provider(*args, **kwargs):
        kwargs["output_path"].write_text(
            '{"status":"success","summary":"missing tests"}\n', encoding="utf-8"
        )

    monkeypatch.setattr(runner, "run_provider_exec", fake_provider)
    with pytest.raises(runner.RunnerError, match="tests_ran must be array"):
        runner.run_task_agent(
            repo_root=tmp_path,
            prompt_text="bounded task-agent compatibility test prompt",
            task={"id": "task-1", "activation_prompt": "prompt"},
            task_result_schema_file=tmp_path / "task.schema.json",
            provider="codex",
            model=None,
            settings=[],
            debug=False,
        )


def test_mcp_runner_command_remains_forced_dry_run(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(mcp_server.shutil, "which", lambda binary: "/bin/codexrun")
    command = mcp_server._runner_command(
        {
            "repo_root": str(tmp_path),
            "audit_prompt_file": "audit.md",
            "audit_schema_file": "audit.schema.json",
            "compiler_prompt_file": "compiler.md",
            "campaign_set_schema_file": "campaign.schema.json",
        },
        tmp_path,
    )
    assert command[0] == "/bin/codexrun"
    assert "--dry-run" in command
    assert "--execute" not in command
