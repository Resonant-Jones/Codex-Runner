from __future__ import annotations

import fnmatch

from .contracts import LoopTask

ADR_SENSITIVE_PATTERNS = (
    "src/**/providers/**",
    "src/**/broker/**",
    "src/**/queue/**",
    "src/**/worker/**",
    "src/**/identity/**",
    "src/**/memory/**",
    "src/**/persona/**",
    "src/**/schema/**",
    "src/**/migrations/**",
    "docs/architecture/**",
    "docs/design/tokens/**",
)
ADR_SENSITIVE_TERMS = (
    "architecture",
    "state machine",
    "provider",
    "broker",
    "queue",
    "worker",
    "identity",
    "memory",
    "persona",
    "schema",
    "persistence",
    "release-readiness",
)


def classify_adr_impact(task: LoopTask, changed_paths: list[str]) -> str:
    if any(
        fnmatch.fnmatchcase(path, "docs/architecture/adr/proposed/**")
        or fnmatch.fnmatchcase(path, "docs/architecture/proposed/**")
        for path in changed_paths
    ):
        return "proposal_created"
    if any(
        fnmatch.fnmatchcase(path, "docs/architecture/adr/accepted/**")
        for path in changed_paths
    ):
        return "operator_required"
    if any(
        any(fnmatch.fnmatchcase(path, pattern) for pattern in ADR_SENSITIVE_PATTERNS)
        for path in changed_paths
    ):
        return "proposal_required"
    lowered = task.objective.lower()
    if any(term in lowered for term in ADR_SENSITIVE_TERMS):
        return "proposal_required"
    if any("adr" in path.lower() for path in changed_paths):
        return "operator_required"
    return "none"

