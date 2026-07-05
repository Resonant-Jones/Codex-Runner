from __future__ import annotations

from codex_runner.loop_manager.adr_policy import classify_adr_impact
from codex_runner.loop_manager.contracts import LoopTask


def make_task(objective: str = "docs only") -> LoopTask:
    return LoopTask(
        id="task-1",
        objective=objective,
        repo_root=".",
        max_attempts=1,
        allowed_paths=["docs/handoffs/**"],
        forbidden_paths=["README.md"],
        acceptance_criteria=["receipt"],
        validation_commands=["python3 -c \"print('ok')\""],
        operator_review_required_for=[],
        context_docs=["README.md"],
    )


def test_adr_impact_none_for_docs_only() -> None:
    assert classify_adr_impact(make_task(), ["docs/handoffs/run.md"]) == "none"


def test_adr_impact_fails_closed_for_sensitive_scope() -> None:
    impact = classify_adr_impact(
        make_task("Change provider boundary behavior"),
        ["src/codex_runner/providers/adapter.py"],
    )
    assert impact == "proposal_required"


def test_adr_impact_detects_proposal_created() -> None:
    impact = classify_adr_impact(
        make_task(),
        ["docs/architecture/adr/proposed/pi-loop-manager.md"],
    )
    assert impact == "proposal_created"

