from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from codex_runner.guardian.repo_boundary import (
    REPO_ROOT_ENV,
    RepoBoundaryError,
    resolve_repo_root,
)


def _git_init(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path.resolve()


def test_resolves_git_root_from_nested_working_directory(tmp_path: Path) -> None:
    root = _git_init(tmp_path / "repo")
    nested = root / "a" / "b"
    nested.mkdir(parents=True)

    assert resolve_repo_root(cwd=nested, environ={}) == root


def test_explicit_repo_root_must_be_git_top_level(tmp_path: Path) -> None:
    root = _git_init(tmp_path / "repo")
    nested = root / "nested"
    nested.mkdir()

    with pytest.raises(RepoBoundaryError, match="top-level exactly"):
        resolve_repo_root(nested, cwd=tmp_path, environ={})


def test_environment_repo_root_is_supported(tmp_path: Path) -> None:
    root = _git_init(tmp_path / "repo")

    assert resolve_repo_root(
        cwd=tmp_path,
        environ={REPO_ROOT_ENV: str(root)},
    ) == root


def test_git_environment_cannot_redirect_fallback_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _git_init(tmp_path / "repo")
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    unrelated = _git_init(tmp_path / "unrelated")

    monkeypatch.setenv("GIT_DIR", str(unrelated / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(unrelated))

    assert resolve_repo_root(cwd=nested, environ={}) == root


def test_git_environment_cannot_redirect_configured_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _git_init(tmp_path / "repo")
    unrelated = _git_init(tmp_path / "unrelated")

    monkeypatch.setenv("GIT_DIR", str(unrelated / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(unrelated))

    assert resolve_repo_root(root, cwd=tmp_path, environ={}) == root
