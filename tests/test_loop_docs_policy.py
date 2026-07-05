from __future__ import annotations

from codex_runner.loop_manager.docs_policy import (
    classify_doc_path,
    documentation_impact_for_paths,
    forbidden_doc_paths,
    operator_review_required,
)


def test_documentation_authority_classification() -> None:
    assert classify_doc_path("docs/handoffs/run.md") == "free_write"
    assert classify_doc_path("docs/architecture/proposed/adr.md") == "proposal_only"
    assert classify_doc_path("README.md") == "read_only"


def test_forbidden_path_detection() -> None:
    forbidden = forbidden_doc_paths(["README.md", "docs/handoffs/run.md"])
    assert forbidden == ["README.md"]


def test_documentation_impact_values() -> None:
    assert documentation_impact_for_paths(["docs/handoffs/run.md"]) == "handoff_only"
    assert (
        documentation_impact_for_paths(["docs/architecture/proposed/adr.md"])
        == "proposal_created"
    )
    assert documentation_impact_for_paths(["README.md"]) == "canonical_change_required"


def test_ui_operator_review_detection() -> None:
    assert operator_review_required(
        changed_paths=["src/app/components/Button.tsx"],
        objective="Refine UI layout behavior",
        requested_review_flags=["ui_ux_changes"],
    )

