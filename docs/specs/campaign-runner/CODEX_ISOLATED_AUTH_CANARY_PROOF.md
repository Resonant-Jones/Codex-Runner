# Restored Isolated Codex Authentication Canary Proof

- Status: Live Proof
- Date and timezone: 2026-07-24 EDT (UTC-04:00); canary evidence captured 2026-07-24T19:45 EDT
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Repository branch: `isolated-auth-proof`
- Starting HEAD: `311e4e6fb8a027598f157e5651553a81958b2c4e`
- Final Codex-owned classification: `BLOCKED_ENVIRONMENT`
- ADR impact: no new ADR required

## Plain falsifiable claim

A fresh isolated `CODEX_HOME` is authenticated through ChatGPT, advertises the required `--output-schema` capability, and has zero configured MCP servers. Exactly one bounded canary invocation was attempted with the documented `--json`, `--output-schema`, and `-o` command shape. The CLI exited before provider execution because it rejected the temporary working directory as untrusted and required an undocumented-to-this-command trust-bypass flag. Therefore restored authentication and schema-constrained provider completion remain unproved.

This result does not invalidate the authenticated login status. It proves only that this one authorized command shape could not reach the provider from the selected temporary working directory, and no second provider call is authorized.

## Relationship to the earlier blocked proof

The earlier `BLOCKED_OPERATOR_INTERACTION` proof remains valid historical evidence for the pre-authorization attempt. The operator subsequently completed device authentication. This proof advances the evidence to authenticated isolated posture, but the single canary was blocked before provider execution by the CLI trust check.

## Baseline and repository state

Initial state was clean on `isolated-auth-proof` at the starting HEAD above. The actual full hash is recorded because the task's expected hash was not a valid full repository revision. Required baselines passed after an approved filesystem-access rerun:

| Check | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |
| Final repository status before staging | one new proof report only |

The first sandboxed full-suite attempt produced 32 permission setup errors because the sandbox could not write Runner-local test directories. That environmental limitation was removed for the approved rerun; no test or production file was changed.

## Isolated posture

| Surface | Result |
| --- | --- |
| Active CLI | `/opt/homebrew/bin/codex`, `codex-cli 0.36.0` |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex`, `codex-cli 0.144.6` |
| `--output-schema` advertised | yes |
| `--json` advertised | yes |
| Authentication status | `Logged in using ChatGPT` |
| Configured MCP servers | zero; `mcp list --json` returned `[]` |
| Fresh isolated home | `/tmp/codex-isolated-auth-restoration-proof/codex-home` |

Only coarse authentication status was recorded. Authentication-file contents, credentials, cookies, account identifiers, and private configuration were not read or recorded.

## Canary execution

Exactly one provider-call attempt was made. No retry or second provider call occurred.

Redacted command shape:

```text
CODEX_HOME=<fresh-isolated-home> <isolated-codex> exec --json --output-schema <CANARY_ROOT>/schema.json -o <CANARY_ROOT>/output.json <prompt>
```

- Timeout: 120 seconds
- Start: `2026-07-24T23:45:00.379144+00:00`
- End: `2026-07-24T23:45:00.724971+00:00`
- Duration: 0.346 seconds
- Exit code: 1
- JSON-event terminal state: `not_observed`; stdout was empty
- Stderr summary: `Reading additional input from stdin...` followed by `Not inside a trusted directory and --skip-git-repo-check was not specified.`
- Output file: absent; no size, JSON, or schema result exists
- Process cleanup: no child process remained after exit

The launcher removed API-token environment variables, captured bounded stdout/stderr, used a separate process group, enforced the timeout, and verified child cleanup. The prompt prohibited repository inspection, file modification, and shell execution.

## Classification

`BLOCKED_ENVIRONMENT` is the only truthful classification. Login was accepted, but the CLI trust check prevented the command from reaching provider execution. This is not `PASS_AUTH_RESTORED`, because no terminal provider completion, output file, JSON parse, or schema validation occurred. It is not `AUTHENTICATION_REJECTED`, because authentication was accepted. It is not `PROCESS_TIMEOUT`, because the process exited in 0.346 seconds.

## Validation and security

- Output-file existence was independently checked and was false.
- JSON parsing and schema validation were not applicable because no output file existed.
- No output was reconstructed from stdout.
- No authentication files were inspected, copied, modified, or committed.
- The isolated home was not modified by the proof beyond CLI runtime behavior.
- No MCP server was configured.
- No Runner, MCP, test, prompt, schema, skill, README, package, or production file was changed.
- Secret-pattern and identity review found no credential values, tokens, cookies, authorization headers, email addresses, or account identifiers in this report or the sanitized review context.

## Warnings separated from failures

- Warning: the exact command shape required by the task is rejected when run from the temporary work directory unless a trust-bypass option is supplied.
- Failure boundary: the canary therefore did not reach provider execution.
- The DeepSeek delegation preflight was attempted and failed because `CODEX_DEEPSEEK_EXTERNAL_PROVIDER_ACK` was absent. The acknowledgement was not set silently, so no delegation occurred.

## Authorized next task and remaining unproved surfaces

No Runner instrumentation is authorized for this classification. The remaining prerequisite is an explicitly authorized, documented command shape that can run from a trusted or approved temporary working directory without violating the one-call budget. The semantic MCP campaign must not be rerun.

Remaining unproved surfaces include schema-constrained generation under the restored authentication, Stage-A execution, Runner subprocess behavior under successful provider execution, MCP semantic completion, campaign compilation, and any supported CLI version range.

## Reproduction commands without credentials

```bash
CODEX_BIN=/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex
CODEX_HOME=/tmp/codex-isolated-auth-restoration-proof/codex-home
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" --version
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" login status
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" mcp list --json
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" exec --help
```

Do not rerun the provider command without resolving the trust-boundary issue and obtaining explicit authorization for any changed command shape.

## DeepSeek delegation receipt

- Delegated task and mode: not run; intended mode was one bounded read-only `review` of sanitized proof evidence.
- Preflight: failed with `explicit external-provider consent is missing`.
- Acknowledgement: absent; not set by Codex.
- Selected model: none
- Result artifact: none
- Accepted findings: none
- Rejected findings: none
- Codex verification: the preflight failure was independently recorded; no DeepSeek claims were accepted or fabricated.
- Remaining uncertainty: no second-model review was available.

DeepSeek was not given credentials, authentication files, private configuration, or the isolated home. Direct Codex execution was a bounded proof control, not Runner authority. This report does not prove Stage-A execution, Runner subprocess behavior, MCP semantic completion, campaign compilation, or release readiness. One CLI version does not establish a supported range, and no production or release claim changes.

## Repository integrity

The final change is exactly this proof document. The earlier blocked proof remains unchanged. Temporary canary artifacts remain outside Git under `/tmp/codex-isolated-auth-restoration-proof/canary/`; authentication material remains temporary and uncommitted.
