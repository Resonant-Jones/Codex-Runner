from __future__ import annotations

from codex_runner.loop_manager.contracts import RetryPolicyConfig
from codex_runner.loop_manager.retry_policy import (
    RetryTracker,
    retry_budget_exhausted,
)


def test_retry_budget_exhaustion() -> None:
    config = RetryPolicyConfig(max_execution_attempts=2)
    assert retry_budget_exhausted(2, config) is True
    assert retry_budget_exhausted(1, config) is False


def test_repeated_failure_stop() -> None:
    tracker = RetryTracker(RetryPolicyConfig(repeated_failure_limit=1))
    tracker.record_failure("same")
    assert tracker.should_stop_for_repeated_failure("same") is False
    tracker.record_failure("same")
    assert tracker.should_stop_for_repeated_failure("same") is True

