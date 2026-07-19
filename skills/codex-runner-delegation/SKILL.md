---
name: codex-runner-delegation
description: Experimental transport for requesting Deterministic Campaign Runner dry-run orchestration through the codex_runner_campaign_dry_run MCP tool. Use only to produce Runner-owned dry-run campaign artifacts for review; it does not authorize implementation, autonomous execution, Pi Loop, or Guardian operations.
---

# Codex Runner Campaign Dry Run

> **Experimental status — prototype. Do not advertise or release.**

Use `codex_runner_campaign_dry_run` only for Deterministic Campaign Runner
dry-run orchestration. The adapter validates arguments and invokes the public
Runner CLI with `--dry-run`; it does not invoke providers directly.

## Procedure

1. Resolve the exact repository root.
2. Obtain the required audit prompt, audit schema, compiler prompt, and campaign
   set schema paths.
3. Pass only documented tool arguments. Do not attempt to pass `--execute` or
   generic implementation, inspection, or autonomous modes.
4. Call `codex_runner_campaign_dry_run`.
5. Report the process outcome as transport evidence only. Review the referenced
   Runner-generated artifacts for campaign evidence.

The allowlist consists of the required `repo_root`, `audit_prompt_file`,
`audit_schema_file`, `compiler_prompt_file`, and `campaign_set_schema_file`;
plus optional Runner-supported `provider`, `task_result_schema_file`, `passes`,
`base_ref`, branch/discovery/verification/debug controls, provider model
selectors, `codex_config`, and `claude_settings`. The MCP tool schema is the
authoritative argument spelling and type reference.

The tool grants no implementation or mutation authority. Runner dry-run may
produce its normal campaign, state, audit, and receipt artifacts; those
Runner-generated artifacts remain the evidence surface. The MCP adapter creates
no authoritative receipt. A zero process exit is not approval, implementation
success, test success, or execution authorization.
