from __future__ import annotations

import fnmatch

from .contracts import ExecutionResult, LoopTask
from .docs_policy import forbidden_doc_paths


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def inspect_execution_result(
    task: LoopTask,
    result: ExecutionResult,
    previous_changed_paths: list[str],
) -> dict[str, object]:
    result.validate()
    changed_paths = sorted(set(result.proposed_changed_paths))
    forbidden_paths = [
        path for path in changed_paths if _matches(path, task.forbidden_paths)
    ]
    forbidden_paths.extend(forbidden_doc_paths(changed_paths))
    progress_delta = [
        path for path in changed_paths if path not in set(previous_changed_paths)
    ]
    no_progress = not progress_delta and bool(previous_changed_paths or changed_paths)
    return {
        "status": result.status,
        "summary": result.summary,
        "changed_paths": changed_paths,
        "forbidden_paths": sorted(set(forbidden_paths)),
        "progress_delta": progress_delta,
        "no_progress": no_progress,
        "evidence_refs": list(result.evidence_refs),
        "repair_hints": list(result.repair_hints),
    }

