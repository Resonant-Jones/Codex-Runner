from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

LEGACY_REPO_ROOT = Path("/Volumes/Dev_SSD/Codex-Runner")


def pytest_collection_modifyitems(items) -> None:
    """Normalize legacy orchestration fixtures during portability migration."""

    for item in items:
        module = getattr(item, "module", None)
        if module is None:
            continue
        if getattr(module, "REPO_ROOT", None) == LEGACY_REPO_ROOT:
            module.REPO_ROOT = ROOT
