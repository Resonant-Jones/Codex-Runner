from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT_ENV = "CODEX_RUNNER_REPO_ROOT"


class RepoBoundaryError(RuntimeError):
    """Raised when Guardian cannot establish a trusted repository boundary."""


def _resolved(path: Path) -> Path:
    try:
        return path.expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise RepoBoundaryError(f"unable to resolve repository path: {path}") from exc


def _git_subprocess_env() -> dict[str, str]:
    """Return an environment that cannot redirect git away from cwd."""

    return {
        name: value
        for name, value in os.environ.items()
        if not name.startswith("GIT_")
    }


def _git_toplevel(start: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start),
            env=_git_subprocess_env(),
            text=True,
            capture_output=True,
            check=False,
        )
    except (FileNotFoundError, OSError) as exc:
        raise RepoBoundaryError("git is required to resolve the repository boundary") from exc

    if result.returncode != 0 or not result.stdout.strip():
        detail = (result.stderr or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RepoBoundaryError(
            f"unable to resolve a git repository from {start}{suffix}"
        )
    root = _resolved(Path(result.stdout.strip()))
    resolved_start = _resolved(start)
    try:
        resolved_start.relative_to(root)
    except ValueError as exc:
        raise RepoBoundaryError(
            f"git repository boundary {root} does not contain {resolved_start}"
        ) from exc
    return root


def resolve_repo_root(
    explicit: Path | None = None,
    *,
    cwd: Path | None = None,
    environ: dict[str, str] | None = None,
) -> Path:
    """Resolve one trusted repo root from CLI, environment, or current checkout.

    Precedence is explicit CLI value, CODEX_RUNNER_REPO_ROOT, then the git root
    containing the current working directory. Explicit and environment values
    must name the repository top-level exactly.
    """

    env = os.environ if environ is None else environ
    working_dir = _resolved(cwd or Path.cwd())

    configured: Path | None = explicit
    source = "--repo-root"
    if configured is None:
        raw_env = env.get(REPO_ROOT_ENV, "").strip()
        if raw_env:
            configured = Path(raw_env)
            source = REPO_ROOT_ENV

    if configured is None:
        return _git_toplevel(working_dir)

    candidate = _resolved(configured)
    if not candidate.is_dir():
        raise RepoBoundaryError(f"{source} is not a directory: {candidate}")

    discovered = _git_toplevel(candidate)
    if candidate != discovered:
        raise RepoBoundaryError(
            f"{source} must name the git repository top-level exactly: "
            f"expected {discovered}, got {candidate}"
        )
    return discovered
