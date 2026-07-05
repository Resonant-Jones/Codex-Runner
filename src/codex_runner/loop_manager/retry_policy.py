from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import RetryPolicyConfig


@dataclass(slots=True)
class RetryTracker:
    config: RetryPolicyConfig = field(default_factory=RetryPolicyConfig)
    failure_signatures: dict[str, int] = field(default_factory=dict)

    def record_failure(self, signature: str) -> int:
        count = self.failure_signatures.get(signature, 0) + 1
        self.failure_signatures[signature] = count
        return count

    def should_stop_for_repeated_failure(self, signature: str) -> bool:
        return (
            self.failure_signatures.get(signature, 0)
            > self.config.repeated_failure_limit
        )


def retry_budget_exhausted(attempt: int, config: RetryPolicyConfig) -> bool:
    return attempt >= config.max_execution_attempts

