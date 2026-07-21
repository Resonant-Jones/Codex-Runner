# Codex Runner Subprocess Output-Return Diagnostic

- Status: Live Diagnostic
- Date and timezone: 2026-07-21 EDT (UTC-04:00); evidence captured 2026-07-21T17:51Z through 2026-07-21T18:05Z
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Runner repository path: `codex-runner-friend-share` (local user-directory prefix redacted)
- Branch and starting HEAD: `main` at `dab2b709cb3039b453c4e29226d88dd244f1a385`
- Final classification: `UNRESOLVED_WITH_BOUNDED_EVIDENCE`
- ADR impact: no new ADR required. Direct CLI use and synthetic controls here are bounded diagnostics, not product authority paths.

## Falsifiable claim

The isolated Codex CLI `0.144.6`, the exact recovered Stage-A prompt, the canonical audit schema, the disposable target repository, the auth-only zero-MCP configuration posture, and the current Runner provider-execution seam were exercised across five matrix rows. Every **live** provider row (file redirect, the documented `--json` control, captured pipes, and the real Runner provider-execution seam) failed **identically and fast** in approximately 4.1 seconds with Codex returning exit `1` and the error `refresh token was revoked` / `token_invalidated`. No row stalled. The Runner seam raised `RunnerError: codex exec failed` promptly on the nonzero exit; the captured-pipe posture did not deadlock; no descendant process survived in any row. The one **non-live** row (synthetic post-process control) completed successfully using the prior known-good schema-valid fixture, proving the Runner's output read, `audit_id` check, and persist path are sound given a valid provider result.

Because valid provider authentication (present on 2026-07-20 when the prior direct Stage-A control succeeded in 56.4 seconds) is **no longer present** on 2026-07-21, the matrix cannot reach the success path that would differentiate the original 2026-07-20 seven-minute MCP stall. The original boundary therefore remains unresolved, bounded by explicit negative evidence.

## Explicit limits

- Direct Codex invocation and the synthetic post-process control are diagnostic controls, not product authority paths.
- One CLI version (0.144.6) does not establish a supported version range.
- This diagnostic does not prove campaign compilation, MCP semantic completion, task-agent execution, execute mode, Claude compatibility, Guardian or Pi integration, or release readiness.
- No release, provider-support, production-readiness, or release-readiness claim changes.
- No Runner, MCP, test, prompt, schema, skill, package, or README file changed.
- The MCP semantic campaign proof remains blocked; this diagnostic did not retry it.
- The authentication invalidation is an environmental change observed during this task; it is reported as evidence, not repaired.

## Active and isolated CLI versions

| Surface | Path | Version | `--output-schema` advertised |
| --- | --- | --- | --- |
| Active CLI (unchanged) | `/opt/homebrew/bin/codex` | `codex-cli 0.36.0` | no |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex` | `codex-cli 0.144.6` | yes (`--output-schema <FILE>` and `--json` both advertised in `codex exec --help`) |

The active machine-wide Codex CLI was not modified. `codex --upgrade` was not run.

## Runner subprocess implementation snapshot

Snapshot taken from `src/codex_runner/runner.py` at HEAD `dab2b70`. Behavior is recorded from code, not inferred from names.

- Command-construction function: `run_codex_exec` (lines 1163-1189). It builds:
  ```
  ["codex", ["--model", model], ["--config", config]..., "exec", "--output-schema", <schema>, "-o", <output>, <prompt_text>]
  ```
  The command does **not** include `--json`. The prompt is passed as a positional argument after `-o`. The executable is the bare string `"codex"` (resolved by the OS through `PATH`), not a pre-resolved absolute path.
- Provider-execution function: `run_codex_exec(repo_root, *, prompt_text, output_schema, output_path, model, configs, debug) -> None`.
- Dispatch wrapper: `run_provider_exec` (lines 1243-1276) routes `provider="codex"` to `run_codex_exec`.
- Underlying subprocess layer: `run_cmd` (lines 139-164) calls exactly one layer of `subprocess.run`:
  ```python
  subprocess.run(args, cwd=str(cwd), text=True, capture_output=capture_output, check=False)
  ```
- Working-directory selection: `repo_root` (the audited repository).
- Environment construction: inherited from the parent process; no `env=` argument is passed, so the child sees the harness environment unchanged.
- Executable resolution: `ensure_provider_available("codex")` in `main()` confirms `codex` exists via a PATH walk, but the actual invocation uses the bare name `"codex"`.
- Prompt delivery: positional command argument (the rendered prompt text).
- Output-schema argument: `--output-schema <path>` (present).
- Output-file argument: `-o <path>` (present).
- stdout / stderr handling: `capture_output=True`, which is equivalent to `stdout=PIPE, stderr=PIPE`.
- text vs binary: `text=True` (text mode, default UTF-8).
- Timeout behavior: **none.** No `timeout=` argument is passed. `subprocess.run` blocks until the child exits.
- Process-group / session behavior: **none.** No `start_new_session=True`, no `preexec_fn=os.setsid`, no `process_group=0`. The child shares the parent's process group and session.
- Cancellation behavior: **none.** No signal handling and no external cancellation path.
- Return-code handling: `run_codex_exec` raises `RunnerError("codex exec failed" + STDERR/STDOUT)` when `result.returncode != 0`; on zero it returns `None`.
- Output-file read timing: performed by `run_pass` **after** `run_provider_exec` returns, via `audit_payload = json_read(stage_a_output_path)` (line 1577), inside the surrounding `tempfile.TemporaryDirectory()` block.
- JSON-parse timing: inside `json_read` (lines 107-117) after subprocess completion.
- Schema-validation timing: the Runner does **not** independently validate Stage-A output against the schema in code; it relies on `--output-schema` for provider-side constraint and checks only `audit_id` via `ensure_audit_id` (lines 1503-1508). No `jsonschema` call exists in the Stage-A path.
- Retry behavior: **none.**
- Wrapper inventory: a single `subprocess.run` layer inside `run_cmd`, invoked directly by `run_codex_exec`. The MCP adapter (`src/codex_runner/mcp_server.py`, lines 252-258) adds a second outer `subprocess.run(..., capture_output=True, text=True)` with no timeout around the entire `codexrun --dry-run` CLI; that outer layer is above the Runner provider boundary and was not exercised in this task (the prior semantic proof remains the evidence for it).

## Exact shared environment posture

All rows shared the following recovered posture. Diagnostic root: `/tmp/codex-runner-subprocess-output-diagnostic/`.

| Dimension | Value |
| --- | --- |
| Isolated Codex | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex` (0.144.6) |
| Config home (`CODEX_HOME`) | `/tmp/codex-stage-a-provider-diagnostic/clean-home` (auth-only, reused unchanged from prior proof; contents not printed) |
| MCP servers configured | zero (`clean-mcp-list.json` reports `[]`) |
| `config.toml` | none |
| Copied tool configuration | none |
| Model / config flags | none (CLI default model selection; `--model`/`--config` omitted) |
| Working directory | `/tmp/codex-runner-mcp-semantic-proof/target-repo` (resolves to `/private/tmp/...`, matching the prompt's hardcoded `repo.path`) |
| Authentication posture | minimum authentication material available; `auth.json` present at the `CODEX_HOME` root; contents neither printed nor committed |
| Codex `PATH` order | isolated CLI bin dir prepended so `codex` resolves to 0.144.6 |
| `CODEX_MCP_CONFIG` | unset |

## Input hashes (SHA-256)

| Input | SHA-256 | Size |
| --- | --- | --- |
| Stage-A prompt (`stage-a-prompt.md`) | `63fe53364c5b2a299ff47249a2a2f2611d227a3cceb45836e72c03dc3d4b6c83` | 1,158 bytes |
| Canonical schema (`mega_audit_output.schema.json`) | `9ee2fd69035fcf1a5489d49fceb470ba1478386a19a2fda3bab0d962986a2ee7` | 7,278 bytes |
| Prior successful Stage-A output / Row D fixture | `c295976caa0a830719abdec96ec5162a2a4cb4a7bd4a14057cae3b693489334c` | 3,236 bytes (independently schema-validated before reuse) |

Disposable target repository tracked tree (commit `2ad5111581a529b61f03c141568f08eb35d9e53e`, unchanged across all rows):

```
AGENTS.md          b05b960dfc221e08502fbc99a935d86ecb249257
README.md          e48cae22d5b014eddb8aeb9fa76783d1e68fb920
name_service.py    1fdd21d9dda0deb2b931b9c10d436bdec31d66fe
test_name_service.py dc56d0531ab97f166c38d90b1ab6fd6c5a8c8e70
```

Comparable rows changed only the dimension each row is designed to vary (`--json`, capture mode, or Runner seam). No row mutated the target repository's tracked tree; the only pre-existing untracked entry (`docs/`) was left by the prior semantic proof and was not touched.

## Row A evidence: direct CLI without `--json`, file redirect

| Evidence | Result |
| --- | --- |
| Mode | `codex exec --output-schema <schema> -o <output> <prompt>`; no `--json`; stdout/stderr redirected to ordinary files |
| Working directory | disposable target repository |
| Timeout | 180 s |
| Exit / termination | `1` / completed normally; no forced termination |
| Duration | 4.1 s |
| Descendants observed | 0 at t=0; 0 at t=4.1; none survived |
| stdout growth | 0 bytes throughout |
| stderr growth | 0 bytes at t=0; 5,073 bytes at completion |
| Output file | never created |
| Failure mode | Codex returned 401 / `token_invalidated` / `refresh_token was revoked` |
| JSON parse | n/a (no output file) |
| Schema validation | n/a |
| Process group alive after | no |
| Classification | `FAIL` (provider auth failure, not a stall) |

Representative stderr (error-message prose and an error code only; no credential value):
```
ERROR codex_models_manager::manager: failed to refresh available models:
  ... 401 Unauthorized: Your authentication token has been invalidated ...
ERROR: Your access token could not be refreshed because your refresh token
  was revoked. Please log out and sign in again.
```

## Row A' evidence: `--json` control (direct, exact prior-successful shape)

Run as a comparison control to isolate the `--json` variable from the auth variable.

| Evidence | Result |
| --- | --- |
| Mode | `codex exec --json --output-schema <schema> -o <output> <prompt>` (exact prior-successful shape) |
| Working directory | disposable target repository |
| Timeout | 60 s |
| Exit / termination | `1` / completed normally |
| Duration | ~4 s |
| stderr | 401 / `refresh_token_invalidated` |
| Event stream emitted | `thread.started`, `turn.started`, `error` (`refresh token was revoked`), `turn.failed` |
| Output file | never created |
| Classification | `FAIL` (same auth failure as Row A; `--json` does not change the outcome today) |

The prior direct Stage-A control (2026-07-20) completed in 56.4 seconds and produced schema-valid audit JSON using this exact command. The same command on 2026-07-21 fails in ~4 seconds with auth revoked. This is decisive: the precondition that made the prior proof's direct control pass is no longer present, and `--json` is not the differentiator of the current failure.

## Row B evidence: direct CLI without `--json`, captured pipes

| Evidence | Result |
| --- | --- |
| Mode | same command as Row A; `stdout=PIPE, stderr=PIPE, text=True`, drained by concurrent reader threads reproducing `subprocess.run(capture_output=True, text=True)` / `Popen.communicate()` semantics |
| Working directory | disposable target repository |
| Timeout | 180 s |
| Exit / termination | `1` / completed normally; no forced termination |
| Duration | 4.1 s |
| Descendants observed | 0 throughout |
| stdout growth | 0 bytes throughout |
| stderr growth | 0 bytes at t=0; 5,073 bytes at completion |
| Output file | never created |
| Failure mode | identical 401 / `token_invalidated` auth failure |
| Process group alive after | no |
| Classification | `FAIL` (auth failure; captured-pipe posture does not stall and does not deadlock) |

Interpretation: Row B reproduces Row A's capture behavior through Python pipes and fails identically and fast. This rejects pipe-capture/drain deadlock as the cause of the auth-failure path. (It does not, and cannot, test pipe-capture behavior under a successful long-running call while auth is revoked.)

## Row C evidence: current Runner provider-execution seam

The harness imported the unmodified `codex_runner.runner` module and invoked the real `run_codex_exec` (the narrow provider-execution function) with the exact Stage-A inputs. `codex` resolved to 0.144.6 through `PATH`.

| Evidence | Result |
| --- | --- |
| Seam invoked | `runner.run_codex_exec(cwd, prompt_text=..., output_schema=..., output_path=..., model=None, configs=[], debug=True)` |
| Underlying call | `runner.run_cmd` -> `subprocess.run(capture_output=True, text=True)`, no timeout, no session isolation |
| Effective provider command | `[codex, exec, --output-schema, <schema>, -o, <output>, <prompt>]` (no `--json`) |
| Timeout (outer harness) | 180 s |
| Codex exit | `1` after ~4 s of auth retries |
| `subprocess.run` return | returned promptly with `returncode=1` (no stall, no pipe deadlock) |
| Runner behavior | `run_codex_exec` raised `RunnerError: codex exec failed` with captured STDERR/STDOUT |
| Worker exit | `1` (RunnerError caught and reported) |
| Duration | 4.1 s |
| Descendants observed | 0 throughout; none survived |
| Output file | never created |
| stdout (worker) | 5,201 bytes (RunnerError message with embedded codex stderr) |
| stderr (worker) | 12,182 bytes (codex stderr passthrough) |
| Process group alive after | no |
| Classification | `FAIL` (auth failure propagated correctly as `RunnerError`; the seam does not stall on nonzero exit) |

This is the key negative evidence for the seam itself: the Runner's `run_cmd` capture posture and `run_codex_exec`'s return-code handling are correct on the failure path. The seam returns control to the caller promptly when the provider exits nonzero.

## Row D evidence: synthetic post-process control (`SYNTHETIC_POST_PROCESS_CONTROL`)

`run_codex_exec` was monkeypatched at runtime (in the diagnostic worker only; no source change) to copy the prior schema-valid fixture to the requested `output_path` and return `None`, simulating a successful provider call. The real `run_provider_exec` dispatch and the real post-provider sequence used by `run_pass` for Stage A (`json_read` -> `ensure_audit_id` -> `json_write`) then executed against that result.

| Evidence | Result |
| --- | --- |
| Live provider launch | no |
| Synthetic result source | prior known-good Stage-A output (SHA-256 `c295976c...`, independently schema-validated before reuse) |
| `run_provider_exec` (real dispatch) | returned normally |
| `json_read(output_path)` | ok |
| `ensure_audit_id(payload, AUDIT_a10ebe38457c)` | ok (audit_id matched) |
| `json_write(persist_path, payload)` | ok |
| Exit | `0` |
| Duration | 2.0 s |
| Output file | created, 3,236 bytes |
| Independent JSON Schema validation of persisted output | PASS |
| Classification | `PASS` (`SYNTHETIC_POST_PROCESS_CONTROL`; not live provider proof) |

This row proves the Runner's Stage-A output read, `audit_id` enforcement, and persist path succeed given a valid provider result. It isolates post-provider handling from provider execution.

## Row E: skipped (explicit reason)

Row E (Runner seam with documented `--json`) was **not run**. Row A' already exercised the exact prior-successful `--json` command directly and failed identically to Row A on auth revocation. Running Row E would reproduce the same auth failure through the Runner seam and would add no new discriminating evidence. `--json` is not the unresolved variable; valid auth is the blocking precondition. This skip is consistent with the instruction to run Row E only when `--json` remains the single unresolved variable.

## Process-tree timeline (combined)

- Every live row (A, A', B, C) spawned the Codex CLI as a single process with zero observed descendant PIDs at every telemetry sample (2-second cadence). No subprocess fan-out was observed before the auth failure surfaced.
- Each live row's process group was confirmed empty (`process_group_alive_after_kill = false`) after exit; no orphaned Codex, node, or worker process survived.
- Row D spawned only the Python worker; zero Codex descendants; clean exit.
- No forced termination (`SIGTERM`/`SIGKILL`) was required in any row. All rows exited on their own within the configured timeout.
- A post-run sweep (`pgrep` for `codex exec`, `run_subprocess_matrix`, `row_c_worker`, `row_d_worker`) returned no matches.

## stdout / stderr / output-file growth

| Row | stdout final | stderr final | output file |
| --- | --- | --- | --- |
| A (file redirect) | 0 B | 5,073 B | never created |
| A' (`--json` control) | 0 B | 5,073 B | never created |
| B (captured pipes) | 0 B | 5,073 B | never created |
| C (Runner seam) | 5,201 B (RunnerError) | 12,182 B (codex stderr) | never created |
| D (synthetic control) | 357 B | 0 B | 3,236 B (schema-valid) |

In all live rows stderr appeared only at completion (auth failure emitted after the CLI's internal retries); stdout remained empty because the provider never produced model output. Row D's output file matched the fixture byte-for-byte.

## Exit and termination behavior

- No row timed out. Every configured timeout (30-180 s) exceeded the actual runtime by a wide margin.
- No row required `SIGTERM` or `SIGKILL`.
- Every process group was confirmed empty after exit.
- The active `/opt/homebrew/bin/codex` (0.36.0) was not invoked by any row and remains unchanged.

## JSON parse and schema-validation results

| Row | Output file present | JSON parse | Canonical schema validation |
| --- | --- | --- | --- |
| A | no | n/a | n/a |
| A' | no | n/a | n/a |
| B | no | n/a | n/a |
| C | no | n/a | n/a |
| D | yes | PASS | PASS (independent `jsonschema` Draft 2020-12 validation) |

Validation used `jsonschema` 4.26.0 (read-only, from `/tmp/codex-cli-output-schema-proof/python-packages`) against `src/codex_runner/schemas/mega_audit_output.schema.json`. No live row reached a state where validation could apply.

## Lifecycle comparison matrix

| Dimension | A: file redirect | A': `--json` control | B: captured pipes | C: Runner seam | D: post-process control | E: Runner + `--json` |
| --- | --- | --- | --- | --- | --- | --- |
| Live provider | yes | yes | yes | yes | no | skipped |
| `--json` | no | yes | no | current Runner value (no) | n/a | n/a |
| Command hash (shape) | `exec --output-schema -o <prompt>` | `exec --json --output-schema -o <prompt>` | same as A | same as A via Runner | synthetic | n/a |
| Working directory | target-repo | target-repo | target-repo | target-repo | target-repo | n/a |
| Config posture | auth-only, zero MCP | same | same | same | same | n/a |
| Capture mode | file redirect | file redirect | PIPE / text | PIPE / text (Runner `run_cmd`) | synthetic | n/a |
| Child PID observed | 0 | 0 | 0 | 0 | 0 | n/a |
| Child exited | yes | yes | yes | yes | n/a (no live child) | n/a |
| Parent exited | yes | yes | yes | yes | yes | n/a |
| stdout bytes | 0 | 0 | 0 | 5,201 | 357 | n/a |
| stderr bytes | 5,073 | 5,073 | 5,073 | 12,182 | 0 | n/a |
| Output file created | no | no | no | no | supplied (3,236 B) | n/a |
| Output schema-valid | n/a | n/a | n/a | n/a | yes | n/a |
| Duration | 4.1 s | ~4 s | 4.1 s | 4.1 s | 2.0 s | n/a |
| Classification | FAIL (auth) | FAIL (auth) | FAIL (auth) | FAIL (auth -> RunnerError) | PASS (synthetic) | skipped |

## Rejected hypotheses

- **Pipe-capture or drain deadlock on failure**: Row B fails identically and fast to Row A; captured pipes do not stall and do not deadlock when the provider exits nonzero.
- **Runner provider wrapper stall on nonzero exit**: Row C shows `run_codex_exec` -> `run_cmd` -> `subprocess.run(capture_output=True)` returns promptly on exit `1` and raises `RunnerError`; the seam is correct on the failure path.
- **Runner post-provider handling failure**: Row D passes; `json_read`, `ensure_audit_id`, and `json_write` succeed given a valid provider result.
- **`--json` as the differentiator of the current failure**: Row A' (exact prior-successful `--json` command) fails identically to Row A; `--json` is not the cause of today's failure.
- **Process-tree or pipe lifecycle failure**: every row exited on its own with zero descendants and an empty process group; no surviving child, undrained descriptor, or waiting parent was observed.
- **Environment-wide provider or configuration failure unrelated to auth**: the configuration posture (isolated CLI 0.144.6, auth-only zero-MCP `CODEX_HOME`, disposable target) is identical to the prior passing proof; the only changed precondition is credential validity.

## Remaining hypotheses

- The original 2026-07-20 seven-minute MCP-path stall was one of: non-JSON CLI mode under a **successful** long-running call; pipe capture or output draining under a successful long-running call; the Runner wrapper under a successful long-running call; MCP synchronous tool-call waiting above the Runner boundary; or cross-process interaction from the prior proof's persistent client/server trees. None of these can be isolated while provider authentication is revoked, because no live row can reach the success path.
- Network destination details for the 2026-07-20 stall remain unknown (`lsof` was unavailable in the prior proof as well).
- Whether the Runner's missing independent schema validation of Stage-A output should be a separate contract concern is out of scope here; it is noted as an observation, not a finding.

## Exactly one authorized next task

Classification `UNRESOLVED_WITH_BOUNDED_EVIDENCE` maps to exactly one next task:

> Add temporary read-only event and process instrumentation around the current Runner provider seam.

Precondition gate (must be satisfied before that task can produce useful evidence): valid provider authentication must be restored in a fresh auth-only `CODEX_HOME`, because the present matrix is blocked at the auth gate and cannot reach the success path that would discriminate the remaining hypotheses. The instrumentation task must not repair, widen, or change the Runner seam, MCP, provider command, timeout, process-group ownership, or receipt truth; it only observes.

## Security and redaction confirmation

- No credential, token, cookie, account identifier, or `auth.json` content is present in this report.
- The only authentication-related strings in the diagnostic logs are Codex error-message prose and the error code `token_invalidated` / `refresh_token_invalidated`; no secret value, `Bearer` token, or long credential-shaped string appears in any telemetry or log file under the diagnostic root.
- Telemetry records environment variable names; sensitive-named values are redacted (`<redacted:len=N>`). `CODEX_HOME` and `PATH` are recorded as paths only.
- All raw output, telemetry, and logs remain under `/tmp/codex-runner-subprocess-output-diagnostic/`; none is committed to the repository.
- Prior proof roots were read but not modified.

## Warnings (separated from failures)

- **Warning (environmental, not a code failure)**: the auth-only configuration that succeeded on 2026-07-20 is no longer authenticated on 2026-07-21 (`refresh_token was revoked`). This is reported as observed evidence; it was not repaired and no credential was touched.
- **Warning**: the Runner Stage-A path performs no independent schema validation in code (it relies on `--output-schema` for provider-side constraint and checks only `audit_id`). This is an observation about current behavior, not a failure found by this diagnostic.
- **Warning**: the Runner's `run_cmd` provides no timeout and no process-group isolation; this was not exercised under a stall condition because no live row reached the success path, and it is not changed here.

## Reproducibility commands

The harness and workers are standard-library Python under `/tmp/codex-runner-subprocess-output-diagnostic/`:

```
run_subprocess_matrix.py   # bounded harness (file / pipe / runner / synth modes)
row_c_worker.py            # imports codex_runner.runner, calls run_codex_exec
row_d_worker.py            # monkeypatches run_codex_exec, exercises post-provider path
```

Representative invocations (secrets never passed on the command line; `CODEX_HOME` points at an auth-only home):

```bash
# Row A
python3 run_subprocess_matrix.py --mode file \
  --runner-src <repo>/src --cwd <target-repo> \
  --prompt stage-a-prompt.md \
  --schema <repo>/src/codex_runner/schemas/mega_audit_output.schema.json \
  --output outputs/row-a-output.json \
  --codex-home <auth-only-home> \
  --codex-bin <isolated-0.144.6>/codex \
  --node-bin-dir <isolated-0.144.6> \
  --stdout-log logs/row-a-stdout.log --stderr-log logs/row-a-stderr.log \
  --timeout 180 --label ROW_A --result-json telemetry/row-a-result.json

# Row C (Runner seam)
python3 run_subprocess_matrix.py --mode runner ... --label ROW_C ...

# Row D (synthetic post-process)
python3 run_subprocess_matrix.py --mode synth ... --fixture-output row-d-fixture-output.json --label ROW_D ...
```

Independent schema validation:

```bash
PYTHONPATH=<jsonschema-packages> python3 -c \
  "import json, jsonschema; s=json.load(open('<schema>')); d=json.load(open('<output>')); \
   jsonschema.Draft202012Validator(s).validate(d); print('VALID')"
```

Reproducibility requires a freshly authenticated auth-only `CODEX_HOME`; the present auth-only home is no longer authenticated and will reproduce the auth failure rather than the original workload.

## Remaining unproved surfaces

- The original 2026-07-20 seven-minute MCP-path stall root cause remains unisolated.
- Semantic campaign compilation remains unproved.
- MCP response return above the Runner boundary remains unproved.
- Task-agent execution and execute mode remain unproved.
- Runner behavior under a successful long-running provider call (where timeout absence and process-group absence would actually matter) remains unproved.
- Codex CLI compatible version range beyond 0.144.6 remains unclaimed.

## Required report statements

- Direct provider controls do not replace the authoritative Runner path.
- The synthetic post-process control (Row D) is not live provider proof.
- One CLI version does not establish a compatible version range.
- This diagnostic does not prove campaign compilation.
- This diagnostic does not prove MCP semantic completion.
- No release claim changes.
- No Runner implementation changed.
