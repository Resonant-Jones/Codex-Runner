# Codex Stage-A Provider Runtime Diagnostic

- Status: Live Diagnostic
- Date and timezone: 2026-07-20 EDT (UTC-04:00)
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Runner repository: `codex-runner-friend-share` (local user-directory prefix redacted)
- Branch and starting HEAD: `main` at `fb4cd3393bda9eb058818fafc889d7463d959bba`
- Classification: `STAGE_A_COMPLETED_DIRECTLY`
- ADR impact: no new ADR required. Direct CLI use here is a bounded diagnostic control, not a product authority path.

## Falsifiable claim

In the isolated-clean environment, the exact recovered Stage-A prompt and canonical audit schema completed directly through Codex CLI `0.144.6` in 56.4 seconds, exited zero, and wrote schema-valid audit JSON. The previous MCP semantic proof therefore remains blocked at an unproved Runner subprocess/output-return seam, not at the direct provider, authentication, isolated configuration, canonical-schema, or direct Stage-A-workload boundary.

This does not prove MCP semantic campaign completion or campaign compilation.

## Explicit limits

- Direct Codex invocation is a diagnostic control, not a product authority path.
- One CLI version does not establish a supported version range.
- No release, provider-support, production-readiness, or release-readiness claim changes.
- No Runner implementation changed.
- This does not prove execute mode, task-agent execution, cross-process locking, Claude compatibility, Guardian or Pi integration, or campaign quality outside the fixture.
- The direct Stage-A run used documented `--json` event output for telemetry; Runner's prior invocation did not. That difference prevents attributing a single root cause to Runner without a focused follow-up.

## Baseline and environment

The clean Runner checkout passed before diagnostic calls:

| Command | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |

| Surface | Evidence |
| --- | --- |
| Active CLI | `/opt/homebrew/bin/codex`, `codex-cli 0.36.0`; unchanged and incompatible because local help does not expose `--output-schema` |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex`, `codex-cli 0.144.6` |
| Package | `@openai/codex@0.144.6`; reused, not upgraded or reinstalled |
| Capability | Isolated `codex exec --help` advertised exact `--output-schema <FILE>` |
| Clean config home | `/tmp/codex-stage-a-provider-diagnostic/clean-home` |
| Authentication posture | Minimum authentication material available; contents neither printed nor committed |
| Config posture | No `config.toml`, zero configured MCP servers, and no copied tool configuration |
| Model/config arguments | None passed in the recovered Runner command or direct Stage-A control; CLI default model selection was used |

No normal operator configuration, credential value, account identifier, cookie, or private MCP configuration was read into this report.

## Recovered workload

| Input | Evidence |
| --- | --- |
| Source Stage-A prompt | Prior semantic-proof audit artifact; copied as a non-secret temporary diagnostic input |
| Diagnostic prompt | `/tmp/codex-stage-a-provider-diagnostic/stage-a-prompt.md` |
| Prompt size | 1,158 bytes; 29 lines |
| Canonical schema | `src/codex_runner/schemas/mega_audit_output.schema.json` |
| Schema size | 7,278 bytes; 322 lines |
| Schema root required fields | `audit_id`, `repo`, `generated_at`, `agent`, `reports`, `runner_ready_findings`, `campaign_derivation_rules`, `derived_campaigns` |
| Disposable target | Prior semantic fixture repository; 4 tracked files, 1,183 tracked bytes |

The recovered Runner command shape was a positional prompt argument with `--output-schema <canonical schema>` and `-o <output>`, running in the disposable target repository. It had no explicit model or config flags. The direct diagnostic command was the same shape with the installed CLI's documented `--json` event output enabled:

```text
CODEX_HOME="$DIAG_ROOT/clean-home" PATH="$ISOLATED_BIN:$NODE_BIN:..." \
  "$PROOF_CODEX" exec --json \
  --output-schema "$RUNNER_ROOT/src/codex_runner/schemas/mega_audit_output.schema.json" \
  -o "$DIAG_ROOT/stage-a-output.json" \
  "$(< "$DIAG_ROOT/stage-a-prompt.md")"
```

`$RUNNER_ROOT` is deliberately redacted; no command included a secret value.

## Bounded launcher and telemetry

The temporary launcher accepted a command array and working directory; captured stdout and stderr separately; recorded PID, descendants, output-file metadata, and byte growth every five seconds; attempted read-only `ps`, `pgrep`, and `lsof`; and enforced caller-supplied timeout with process-group `SIGTERM`, grace wait, then `SIGKILL` only if required. All three calls exited normally; no provider process remained after the diagnostic.

`lsof` was not installed locally, so destination/socket details were unavailable. This is a telemetry limitation, not evidence of missing network activity.

## Control A: minimal schema canary

The canary used a 269-byte schema requiring exactly `{"status":"ok","value":7}` and a 123-byte no-files prompt. It ran in the clean diagnostic workspace with read-only sandboxing, a 120-second timeout, and the isolated CLI.

| Evidence | Result |
| --- | --- |
| Exit / termination | `0` / completed normally |
| Duration | 10.1 seconds |
| Child observation | One child present at five seconds; none at exit |
| stdout / stderr growth | `0/0` initially; `26/494` bytes at completion |
| Output file | Appeared at completion; 25 bytes |
| JSON parse | PASS |
| JSON Schema validation | PASS |
| Exact object | `{"status":"ok","value":7}` |
| Classification | `PASS` |

Control A re-proves only that this exact environment can authenticate, reach the provider, generate schema-constrained output, and write a result file.

## Control B: canonical schema, bounded synthetic prompt

Control B used the canonical 7,278-byte audit schema with a 346-byte synthetic prompt that requested only the schema's required fields, explicitly prohibited repository inspection, and used empty arrays where permitted. It used the same CLI, clean configuration, output handling, workspace, and a 180-second timeout.

| Evidence | Result |
| --- | --- |
| Exit / termination | `0` / completed normally |
| Duration | 10.2 seconds |
| Child observation | One child present at five seconds; none at exit |
| stdout / stderr growth | `0/0` initially; `384/1,075` bytes at completion |
| Output file | Appeared at completion; 383 bytes |
| JSON parse | PASS |
| Canonical audit-schema validation | PASS |
| Derived campaigns | 0, permitted by this schema-only control |
| Classification | `PASS` |

This rejects canonical-schema parsing or schema-shaped generation as the narrow cause of the prior stall.

## Exact Stage-A direct control

The one direct Stage-A call used the recovered 1,158-byte prompt, canonical schema, disposable target as working directory, no explicit model/config flags, the isolated clean configuration, documented JSON event output, and a 240-second limit.

| Evidence | Result |
| --- | --- |
| Exit / termination | `0` / completed normally; no forced termination |
| Duration | 56.4 seconds |
| Child observation | 4 descendants at 5 seconds; 5 descendants from 10 through 51 seconds; none at exit |
| Event stream | 12 JSON events: `thread.started`, `turn.started`, 4 `item.started`, 5 `item.completed`, and `turn.completed` |
| stdout growth | 101 bytes at 5 seconds; 723 at 10; 1,599 at 15; 6,016 at 20; 12,706 at 25; 16,382 at completion |
| stderr growth | 410 bytes at 5 seconds; unchanged thereafter |
| Output file | Absent through 51 seconds; appeared at completion with 3,236 bytes |
| JSON parse | PASS |
| Canonical audit-schema validation | PASS |
| Audit findings | 2 |
| Derived campaigns | 2 |
| Classification | `PASS` |

The audit identified the documented `normalize_name` contract gap and referenced `README.md`, `name_service.py`, and `test_name_service.py`. It also produced two audit-derived campaign identifiers. This is schema-valid Stage-A audit evidence only, not campaign compilation proof.

The disposable fixture remained at its original commit. Its source and test files have no diff; only the pre-existing Runner audit-input artifacts from the prior semantic proof remain untracked.

## Comparison

| Dimension | Control A | Control B | Exact Stage A |
| --- | --- | --- | --- |
| CLI path/version | isolated / 0.144.6 | isolated / 0.144.6 | isolated / 0.144.6 |
| Config posture | auth-only, zero MCP servers | same | same |
| Working directory | temporary workspace | temporary workspace | disposable fixture |
| Prompt bytes | 123 | 346 | 1,158 |
| Schema bytes | 269 | 7,278 | 7,278 |
| Timeout | 120 s | 180 s | 240 s |
| Provider/event activity | CLI output progressed | CLI output progressed | 12 JSON events through `turn.completed` |
| stdout/stderr | 26 / 494 bytes | 384 / 1,075 bytes | 16,382 / 410 bytes |
| Output file | 25 bytes | 383 bytes | 3,236 bytes |
| Exit / signal | 0 / none | 0 / none | 0 / none |
| Schema validation | PASS | PASS | PASS |
| Classification | PASS | PASS | PASS |

## Diagnosed boundary

`STAGE_A_COMPLETED_DIRECTLY` is the narrow supported classification. Controls A and B reject an environment-wide provider, authentication, isolated configuration, or canonical-schema failure. The exact direct workload rejects a direct repository-inspection workload stall. The prior semantic proof remains blocked because its Runner-owned child process did not return through the subprocess/MCP boundary before it was stopped.

Rejected hypotheses:

- Environment-wide provider failure, authentication failure, and isolated-clean configuration failure: Control A passed.
- Canonical schema complexity as the narrow blocker: Control B passed.
- Direct Stage-A prompt or repository-workload stall: exact Stage A passed.
- Direct CLI process lifecycle failure: exact Stage A produced its file and exited zero.

Unresolved hypotheses:

- Runner subprocess capture, output drain, or lifecycle behavior under its wrapper.
- The effect of Runner's absence of `--json` relative to this telemetry control.
- Cross-process interaction from the prior proof's unexpectedly persistent client/server trees.
- Network destination details, because `lsof` was unavailable.

## One authorized next seam

The only authorized next task is a **Runner subprocess lifecycle and output-return diagnostic**. It must compare Runner-owned subprocess invocation and output capture against this direct control without weakening schema enforcement, bypassing Runner authority, changing MCP permissions, or retrying campaign compilation.

## Security, reproducibility, and remaining proof

All temporary prompts, telemetry, event output, and outputs remain under `/tmp/codex-stage-a-provider-diagnostic/`. The report contains no credential, token, cookie, account identifier, normal configuration content, or user-directory path. No active CLI, Runner, MCP, test, prompt, schema, skill, package, or README file changed.

Reproducibility requires a fresh temporary auth-only configuration home, the exact isolated 0.144.6 executable, the temporary `run_bounded_codex.py` launcher, the recovered prompt copy, and the three command arrays under the diagnostic root. Do not replay the direct Stage-A provider call without a new explicit call budget.

Semantic campaign proof remains blocked. This diagnostic does not prove campaign compilation, MCP response return, task execution, or release readiness.
