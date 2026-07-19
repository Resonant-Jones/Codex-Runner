"""EXPERIMENTAL STATUS — PROTOTYPE.

This MCP adapter invokes the Deterministic Campaign Runner public CLI in
dry-run mode. It is transport only, creates no authoritative receipt, and must
not be advertised or released as a supported integration without further
review and proof.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

SERVER_NAME = "codex-runner"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2025-06-18"
TOOL_NAME = "codex_runner_campaign_dry_run"
OUTPUT_LIMIT = 4_000
ARTIFACT_LIMIT = 100
ARTIFACT_ROOTS = (
    Path("docs/_audits"),
    Path("docs/_campaign_runs"),
    Path("docs/Campaign"),
    Path("docs/tasks"),
)

REQUIRED_PATH_ARGUMENTS = (
    "audit_prompt_file",
    "audit_schema_file",
    "compiler_prompt_file",
    "campaign_set_schema_file",
)
OPTIONAL_PATH_ARGUMENTS = ("task_result_schema_file",)
MODEL_ARGUMENTS = (
    "codex_model",
    "codex_model_audit",
    "codex_model_compiler",
    "codex_model_task",
    "claude_model",
    "claude_model_audit",
    "claude_model_compiler",
    "claude_model_task",
)
BOOLEAN_ARGUMENTS = (
    "branch_per_campaign",
    "allow_discovery_fallback",
    "verify",
    "debug",
)
LIST_ARGUMENTS = ("codex_config", "claude_settings")
ALLOWED_ARGUMENTS = {
    "repo_root",
    "provider",
    "passes",
    "base_ref",
    *REQUIRED_PATH_ARGUMENTS,
    *OPTIONAL_PATH_ARGUMENTS,
    *MODEL_ARGUMENTS,
    *BOOLEAN_ARGUMENTS,
    *LIST_ARGUMENTS,
}

_active_repo_roots: set[Path] = set()
_active_repo_roots_lock = threading.Lock()


def _tool_definitions() -> list[dict[str, Any]]:
    string_property = {"type": "string", "minLength": 1}
    properties: dict[str, Any] = {
        "repo_root": {
            **string_property,
            "description": "Exact repository root passed to Codex Runner.",
        },
        "provider": {"type": "string", "enum": ["codex", "claude"]},
        "passes": {"type": "integer", "minimum": 1, "maximum": 100},
        "base_ref": string_property,
        "branch_per_campaign": {"type": "boolean"},
        "allow_discovery_fallback": {"type": "boolean"},
        "verify": {"type": "boolean"},
        "debug": {"type": "boolean"},
        "codex_config": {
            "type": "array",
            "items": string_property,
            "maxItems": 50,
        },
        "claude_settings": {
            "type": "array",
            "items": string_property,
            "maxItems": 50,
        },
    }
    for name in (*REQUIRED_PATH_ARGUMENTS, *OPTIONAL_PATH_ARGUMENTS, *MODEL_ARGUMENTS):
        properties[name] = string_property
    return [
        {
            "name": TOOL_NAME,
            "description": (
                "Experimentally invoke the Deterministic Campaign Runner CLI "
                "in forced dry-run mode. Runner artifacts are evidence, not approval."
            ),
            "inputSchema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["repo_root", *REQUIRED_PATH_ARGUMENTS],
                "properties": properties,
            },
        }
    ]


def _jsonrpc(result: Any, request_id: Any = None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(code: int, message: str, request_id: Any = None) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _required_string(arguments: dict[str, Any], name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _validate_arguments(arguments: Any) -> tuple[dict[str, Any], Path]:
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    unsupported = sorted(set(arguments) - ALLOWED_ARGUMENTS)
    if unsupported:
        raise ValueError(f"unsupported arguments: {', '.join(unsupported)}")

    repo_root = Path(_required_string(arguments, "repo_root")).expanduser().resolve()
    if not repo_root.is_dir():
        raise ValueError(f"repo_root is not a directory: {repo_root}")
    for name in REQUIRED_PATH_ARGUMENTS:
        _required_string(arguments, name)
    for name in OPTIONAL_PATH_ARGUMENTS + MODEL_ARGUMENTS:
        if name in arguments:
            _required_string(arguments, name)

    provider = arguments.get("provider", "codex")
    if provider not in {"codex", "claude"}:
        raise ValueError("provider must be codex or claude")
    passes = arguments.get("passes", 1)
    if isinstance(passes, bool) or not isinstance(passes, int) or not 1 <= passes <= 100:
        raise ValueError("passes must be an integer from 1 through 100")
    if "base_ref" in arguments:
        _required_string(arguments, "base_ref")
    for name in BOOLEAN_ARGUMENTS:
        if name in arguments and not isinstance(arguments[name], bool):
            raise ValueError(f"{name} must be a boolean")
    for name in LIST_ARGUMENTS:
        if name not in arguments:
            continue
        value = arguments[name]
        if not isinstance(value, list) or len(value) > 50:
            raise ValueError(f"{name} must be an array with at most 50 entries")
        if any(not isinstance(item, str) or not item.strip() for item in value):
            raise ValueError(f"{name} entries must be non-empty strings")
    return dict(arguments), repo_root


def _runner_command(arguments: dict[str, Any], repo_root: Path) -> list[str]:
    executable = shutil.which("codexrun")
    command = [executable] if executable else [sys.executable, "-m", "codex_runner"]
    command.extend(["--repo-root", str(repo_root), "--dry-run"])
    for name in REQUIRED_PATH_ARGUMENTS + OPTIONAL_PATH_ARGUMENTS:
        if name in arguments:
            command.extend([f"--{name.replace('_', '-')}", _required_string(arguments, name)])
    command.extend(["--provider", str(arguments.get("provider", "codex"))])
    if "passes" in arguments:
        command.extend(["--passes", str(arguments["passes"])])
    if "base_ref" in arguments:
        command.extend(["--base-ref", _required_string(arguments, "base_ref")])
    for name in MODEL_ARGUMENTS:
        if name in arguments:
            command.extend([f"--{name.replace('_', '-')}", _required_string(arguments, name)])
    for name in LIST_ARGUMENTS:
        for value in arguments.get(name, []):
            command.extend([f"--{name.replace('_', '-')}", value.strip()])
    if "branch_per_campaign" in arguments:
        command.append(
            "--branch-per-campaign"
            if arguments["branch_per_campaign"]
            else "--no-branch-per-campaign"
        )
    if arguments.get("allow_discovery_fallback"):
        command.append("--allow-discovery-fallback")
    if "verify" in arguments:
        command.append("--verify" if arguments["verify"] else "--no-verify")
    if arguments.get("debug"):
        command.append("--debug")
    return command


def _artifact_snapshot(repo_root: Path) -> dict[str, tuple[int, int]]:
    snapshot: dict[str, tuple[int, int]] = {}
    for relative_root in ARTIFACT_ROOTS:
        root = repo_root / relative_root
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            snapshot[path.relative_to(repo_root).as_posix()] = (
                stat.st_mtime_ns,
                stat.st_size,
            )
    return snapshot


def _artifact_references(
    before: dict[str, tuple[int, int]], after: dict[str, tuple[int, int]]
) -> tuple[list[str], bool]:
    discovered = sorted(path for path, metadata in after.items() if before.get(path) != metadata)
    return discovered[:ARTIFACT_LIMIT], len(discovered) > ARTIFACT_LIMIT


def _bounded(text: str | None) -> dict[str, Any]:
    value = text or ""
    return {
        "text": value[:OUTPUT_LIMIT],
        "truncated": len(value) > OUTPUT_LIMIT,
        "original_characters": len(value),
    }


def _campaign_dry_run(arguments: Any) -> dict[str, Any]:
    validated, repo_root = _validate_arguments(arguments)
    with _active_repo_roots_lock:
        if repo_root in _active_repo_roots:
            raise ValueError(f"campaign dry-run already active for repository: {repo_root}")
        _active_repo_roots.add(repo_root)

    try:
        before = _artifact_snapshot(repo_root)
        command = _runner_command(validated, repo_root)
        completed = subprocess.run(
            command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            check=False,
        )
        after = _artifact_snapshot(repo_root)
        artifact_references, artifact_references_truncated = _artifact_references(
            before, after
        )
        return {
            "classification": "success" if completed.returncode == 0 else "failure",
            "exit_code": completed.returncode,
            "repo_root": str(repo_root),
            "mode": "dry-run",
            "stdout_summary": _bounded(completed.stdout),
            "stderr_summary": _bounded(completed.stderr),
            "runner_artifact_references": artifact_references,
            "runner_artifact_references_truncated": artifact_references_truncated,
            "authoritative_receipt_created_by_adapter": False,
            "authority_statement": (
                "Process outcome only; this is not approval, implementation success, "
                "test success, or execution authorization. The MCP adapter created no "
                "authoritative receipt."
            ),
        }
    finally:
        with _active_repo_roots_lock:
            _active_repo_roots.discard(repo_root)


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if request_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None
    if method == "initialize":
        return _jsonrpc(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
            request_id,
        )
    if method == "tools/list":
        return _jsonrpc({"tools": _tool_definitions()}, request_id)
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        if name != TOOL_NAME:
            return _error(-32602, f"unknown tool: {name}", request_id)
        try:
            value = _campaign_dry_run(
                params["arguments"] if "arguments" in params else {}
            )
            return _jsonrpc(
                {
                    "content": [{"type": "text", "text": json.dumps(value, indent=2)}],
                    "structuredContent": value,
                },
                request_id,
            )
        except (OSError, ValueError) as exc:
            return _jsonrpc(
                {
                    "isError": True,
                    "content": [{"type": "text", "text": str(exc)}],
                },
                request_id,
            )
    if method == "ping":
        return _jsonrpc({}, request_id)
    return _error(-32601, f"method not found: {method}", request_id)


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = handle(json.loads(line))
        except json.JSONDecodeError as exc:
            response = _error(-32700, str(exc))
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
