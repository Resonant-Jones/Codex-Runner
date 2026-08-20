---
name: codex-runner-delegation
description: Use the Codex Runner MCP tool for deterministic campaign dry-run orchestration. This produces Runner-owned evidence for review and does not authorize implementation, autonomous execution, Pi Loop, Guardian operations, or source mutation.
---

# Codex Runner Campaign Dry Run

Use `codex_runner_campaign_dry_run` only when the user wants a Deterministic
Campaign Runner campaign compiled or inspected in dry-run mode.

Required inputs are the exact target `repo_root`, `audit_prompt_file`,
`audit_schema_file`, `compiler_prompt_file`, and `campaign_set_schema_file`.
Pass only arguments accepted by the tool schema. The MCP adapter forces the
Runner CLI into `--dry-run` mode and does not invoke providers directly.

Treat the returned process classification and artifact references as evidence
only. A successful call is not approval, implementation success, test success,
execution authorization, Pi Loop invocation, Guardian authorization, or a
canonical receipt. Review the Runner-generated artifacts before discussing any
next action.
