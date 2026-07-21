# Runner MCP Semantic Campaign Proof

- Proof status: Live
- Date and time: 2026-07-20 22:52:01 EDT (UTC-04:00)
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Codex Runner repository: `codex-runner-friend-share` (local user-directory prefix redacted)
- Branch and starting HEAD: `main` at `ababbc24d1bc6757df32c2827994e8d46356f373`
- Disposable repository: `/tmp/codex-runner-mcp-semantic-proof/target-repo`
- Disposable repository starting HEAD: `2ad5111581a529b61f03c141568f08eb35d9e53e`
- ADR impact: no new ADR required. MCP remains transport-only; the Runner owns provider execution and artifacts; schema-constrained output remains mandatory; human approval remains final.
- Overall outcome: `BLOCKED_ENVIRONMENT`

## Falsifiable claim

The real MCP client reached the authoritative Runner and the Runner launched the isolated Codex `0.144.6` executable with `--output-schema` for Stage A. Neither the sandboxed attempt nor the one allowed host-network retry returned a provider result, audit JSON, campaign JSON, or bounded MCP tool response. Therefore this task does **not** prove schema-constrained campaign compilation through the MCP boundary.

## Exact limits

This proof does not establish execute mode, implementation success, task-agent execution, cross-process locking, Claude compatibility, Codex CLI version-range compatibility, campaign quality outside this fixture, production readiness, release readiness, Guardian integration, or Pi integration. It also does not establish a successful MCP `tools/call` result: the client reached the provider stage but was waiting for it when each attempt was stopped.

## CLI and configuration evidence

| Surface | Evidence |
| --- | --- |
| Active machine-wide CLI | `/opt/homebrew/bin/codex`, `codex-cli 0.36.0`; unchanged and incompatible because local help lacks `--output-schema` |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex`, `codex-cli 0.144.6` |
| Package evidence | `@openai/codex@0.144.6`; reused from the committed capability-matrix proof, not reinstalled or upgraded |
| Capability evidence | Local `codex exec --help` includes exact `--output-schema <FILE>` |
| Isolated-clean posture | `$PROOF_ROOT/clean-home` contained only a permission-restricted temporary authentication file before startup; no `config.toml`, MCP definitions, or other copied configuration |
| Server PATH posture | Isolated Codex and its Node runtime preceded machine-wide paths; `command -v codex` resolved to the isolated executable and `codex --version` returned `0.144.6` |

No normal Codex configuration was read, copied, printed, or modified. No credential content was recorded in this report.

## Green baseline

Before the live proof, the clean Runner checkout passed:

| Command | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |

## Disposable fixture

The fixture committed `README.md`, `AGENTS.md`, `name_service.py`, and `test_name_service.py` on `main` at `2ad5111`. Its documented contract requires `normalize_name(value)` to trim leading and trailing whitespace and reject whitespace-only input with `ValueError`. The intentionally incomplete implementation returns `value` unchanged.

Before and after the live attempt, `python3 -m pytest -q` reported the same two expected failures:

1. `normalize_name(" Ada ")` returned `" Ada "` rather than `"Ada"`.
2. `normalize_name("   ")` did not raise `ValueError`.

This fixture failure was not repaired.

## MCP session and request

The temporary-only client was `temporary-semantic-proof-client` version `1.0.0`, using standards-compliant line-delimited JSON-RPC over one long-lived stdio server process per attempt. The server command was:

```text
/opt/homebrew/bin/python3 -m codex_runner.mcp_server
```

The client sent, in order, `initialize`, `notifications/initialized`, `tools/list`, and one `tools/call`. It performs those operations sequentially, so the observed advance to the provider call proves that initialization and tool discovery completed. The raw initialize and discovery response lines were not persisted because the client was still blocked on the provider call when the environment process was stopped.

The discovered tool list was exactly:

```text
["codex_runner_campaign_dry_run"]
```

The server protocol is `2025-06-18`. The one redacted request used these arguments, with `$RUNNER_ROOT` denoting the local Runner root:

```json
{
  "repo_root": "/tmp/codex-runner-mcp-semantic-proof/target-repo",
  "audit_prompt_file": "$RUNNER_ROOT/src/codex_runner/prompts/mega_audit.md",
  "audit_schema_file": "$RUNNER_ROOT/src/codex_runner/schemas/mega_audit_output.schema.json",
  "compiler_prompt_file": "$RUNNER_ROOT/src/codex_runner/prompts/audit_report_to_campaign_runner.md",
  "campaign_set_schema_file": "$RUNNER_ROOT/src/codex_runner/schemas/campaign_set.schema.json",
  "task_result_schema_file": "$RUNNER_ROOT/src/codex_runner/schemas/task_result.schema.json",
  "provider": "codex",
  "passes": 1,
  "base_ref": "HEAD",
  "verify": false,
  "debug": true
}
```

No execute, autonomous, implementation, generic delegation, Pi, Guardian, or unsupported setting was sent.

## Authoritative execution evidence

The adapter's effective Runner command was the module fallback because `codexrun` was absent:

```text
/opt/homebrew/bin/python3 -m codex_runner \
  --repo-root /tmp/codex-runner-mcp-semantic-proof/target-repo \
  --dry-run \
  --audit-prompt-file $RUNNER_ROOT/src/codex_runner/prompts/mega_audit.md \
  --audit-schema-file $RUNNER_ROOT/src/codex_runner/schemas/mega_audit_output.schema.json \
  --compiler-prompt-file $RUNNER_ROOT/src/codex_runner/prompts/audit_report_to_campaign_runner.md \
  --campaign-set-schema-file $RUNNER_ROOT/src/codex_runner/schemas/campaign_set.schema.json \
  --task-result-schema-file $RUNNER_ROOT/src/codex_runner/schemas/task_result.schema.json \
  --provider codex --passes 1 --base-ref HEAD --no-verify --debug
```

Live process inspection observed this chain:

```text
temporary JSON-RPC client
-> python -m codex_runner.mcp_server
-> python -m codex_runner --dry-run
-> isolated codex exec --output-schema <canonical audit schema>
```

The observed child command was the isolated `0.144.6` executable and used the canonical audit schema. That proves the Runner compatibility preflight did not fail closed before provider invocation. The MCP client did not invoke Codex or any Runner provider function directly.

No completed process exit code, MCP classification, stdout summary, stderr summary, truncation flags, or returned artifact-reference list exists: both attempts remained blocked in the provider audit call. Consequently no success classification is claimed.

## Generated artifacts and semantic inspection

The only final target-repository artifacts were:

```text
docs/_audits/2026-07-21/AUDIT_a10ebe38457c/audit_input_prompt.md
docs/_audits/2026-07-21/AUDIT_a10ebe38457c/run_inputs.json
```

`run_inputs.json` records `provider: codex`, `pass_index: 1`, and `execute_mode: dry-run`. No audit structured output, compiler input, campaign structured output, campaign document, task document, state artifact, or Runner receipt was created.

| Requirement | Result |
| --- | --- |
| Audit JSON parses and validates against `mega_audit_output.schema.json` | Not run: no audit JSON was produced |
| Campaign JSON parses and validates against `campaign_set.schema.json` | Not run: no campaign JSON was produced |
| Campaign count / task count | Not available: no campaign-set output |
| Fixture-path references in generated campaign | Not available: no campaign artifact |
| Normalization-contract gap identified by generated output | Not available: no generated structured output |
| MCP result classification | Not available: no `tools/call` response |

The adapter created no authoritative receipt: no MCP-owned receipt path was found, and the adapter did not return a result that could claim one.

## Repository boundary

Initial disposable status was clean at `## main`. Final status remains on `main` with only the two untracked Runner-generated audit-input artifacts listed above. `README.md`, `AGENTS.md`, `name_service.py`, and `test_name_service.py` have no diff. The fixture `HEAD` remains `2ad5111`; the dry-run created no commit.

## Attempts, warnings, and failure classification

Warnings, kept separate from the environmental block:

- The first sandboxed attempt advanced to audit-input generation but did not return before the execution harness stopped waiting. Its partial artifacts were preserved under `$PROOF_ROOT/attempt-1-incomplete/` before the fixture's generated-artifact directory was reset.
- The one approved host-network retry used the same isolated executable, auth-only configuration, MCP client, target, inputs, and request. It remained in `codex exec --output-schema` for more than seven minutes without an audit output or MCP response, then was terminated to avoid an unbounded live run.
- The execution harness left both subprocess trees alive after it stopped waiting. The sandbox attempt was terminated before inspecting the host retry, restoring a single active run; no additional provider call was issued.

Failure classification: `BLOCKED_ENVIRONMENT`. The provider stage was unavailable to the proof within its bounded execution window. This is not a schema-validation failure, an empty-campaign failure, or evidence that schema enforcement should be weakened. No repair was implemented.

## Consequence and remaining work

No semantic campaign promotion is authorized. A separate environment/runtime diagnostic task may investigate why the isolated `0.144.6` provider call does not complete after the Runner launches it; it must not weaken the compatibility guard, bypass Runner authority, or alter MCP permissions. A new semantic proof would require a fresh disposable fixture and an explicit new provider-call budget.
