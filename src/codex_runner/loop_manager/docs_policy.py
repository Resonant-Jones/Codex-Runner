from __future__ import annotations

import fnmatch

FREE_WRITE_PATTERNS = (
    ".pi/runs/**",
    "docs/handoffs/**",
    "docs/agent-runs/**",
    "docs/implementation-notes/**",
)
PROPOSAL_ONLY_PATTERNS = (
    "docs/architecture/adr/proposed/**",
    "docs/architecture/proposed/**",
    "docs/design/proposed/**",
)
READ_ONLY_PATTERNS = (
    "docs/architecture/adr/accepted/**",
    "docs/architecture/00-current-state.md",
    "docs/design/tokens/**",
    "README.md",
)
UI_REVIEW_PATTERNS = (
    "src/**/ui/**",
    "src/**/components/**",
    "src/**/styles/**",
    "src/**/tokens/**",
    "docs/design/**",
    "README.md",
)
UI_REVIEW_KEYWORDS = (
    "ui",
    "ux",
    "layout",
    "visual",
    "style",
    "token",
    "copy",
    "brand",
    "interaction",
)


def _matches(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def classify_doc_path(path: str) -> str:
    if _matches(path, READ_ONLY_PATTERNS):
        return "read_only"
    if _matches(path, PROPOSAL_ONLY_PATTERNS):
        return "proposal_only"
    if _matches(path, FREE_WRITE_PATTERNS):
        return "free_write"
    return "non_doc"


def documentation_impact_for_paths(paths: list[str]) -> str:
    if not paths:
        return "none"
    if any(classify_doc_path(path) == "read_only" for path in paths):
        return "canonical_change_required"
    if any(classify_doc_path(path) == "proposal_only" for path in paths):
        return "proposal_created"
    if any(classify_doc_path(path) == "free_write" for path in paths):
        return "handoff_only"
    return "none"


def forbidden_doc_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if classify_doc_path(path) == "read_only"]


def operator_review_required(
    *,
    changed_paths: list[str],
    objective: str,
    requested_review_flags: list[str],
) -> bool:
    text = objective.lower()
    keyword_hit = any(keyword in text for keyword in UI_REVIEW_KEYWORDS)
    path_hit = any(_matches(path, UI_REVIEW_PATTERNS) for path in changed_paths)
    if not (keyword_hit or path_hit):
        return False
    review_flags = {flag.lower() for flag in requested_review_flags}
    if not review_flags:
        return True
    return bool(
        {"ui_ux_changes", "design_token_changes", "public_copy_changes"}
        & review_flags
    )
