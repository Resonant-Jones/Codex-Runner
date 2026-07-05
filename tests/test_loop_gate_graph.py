from __future__ import annotations

from codex_runner.loop_manager.gate_graph import GATE_GRAPH, gate_ids


def test_gate_graph_ordering() -> None:
    assert gate_ids() == [
        "context_curator",
        "architecture_gate",
        "adr_gate",
        "planner",
        "plan_validator",
        "executor",
        "inspector",
        "runtime_validator",
        "documentation_steward",
        "receipt_writer",
    ]
    assert GATE_GRAPH[0].role == "context_curator"
    assert GATE_GRAPH[-1].gate_id == "receipt_writer"

