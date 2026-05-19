from __future__ import annotations

from pathlib import Path

from codex_runner.runner import materialize_campaign_artifacts


def _campaign(seq: str, task_slug: str = "fix_widget") -> dict[str, object]:
    return {
        "campaign_date": "2026-03-12",
        "campaign_slug": "alpha",
        "campaign_seq": seq,
        "campaign_markdown": "# Campaign\n",
        "tasks": {
            f"{seq}-task": {
                "id": f"{seq}-task",
                "slug": task_slug,
                "task_artifact_markdown": f"# Task {seq}\n",
            }
        },
        "materialized": {"task_artifact_paths": {}},
    }


def test_materialize_campaign_artifacts_includes_campaign_seq(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path

    first = _campaign("001")
    second = _campaign("002")

    first_paths = materialize_campaign_artifacts(repo_root, first)
    second_paths = materialize_campaign_artifacts(repo_root, second)

    assert (
        repo_root
        / "docs/tasks/alpha_2026_03_12_001/TASK_fix_widget_2026_03_12.md"
    ).exists()
    assert (
        repo_root
        / "docs/tasks/alpha_2026_03_12_002/TASK_fix_widget_2026_03_12.md"
    ).exists()
    assert first["materialized"]["task_artifact_paths"]["001-task"] == (
        "docs/tasks/alpha_2026_03_12_001/TASK_fix_widget_2026_03_12.md"
    )
    assert second["materialized"]["task_artifact_paths"]["002-task"] == (
        "docs/tasks/alpha_2026_03_12_002/TASK_fix_widget_2026_03_12.md"
    )
    assert first_paths != second_paths
