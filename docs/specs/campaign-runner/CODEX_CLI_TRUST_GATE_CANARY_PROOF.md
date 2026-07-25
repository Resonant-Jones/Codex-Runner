# Codex CLI Trust-Gate Canary Proof

- Status: Live Proof
- Date and timezone: 2026-07-24 EDT (UTC-04:00); canary evidence captured 2026-07-24T21:54 EDT
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Repository branch and starting HEAD: `isolated-auth-proof` at `d8281877baa7d856c7b839f23c484b782cd6511e`
- Final Codex-owned classification: `BLOCKED_ENVIRONMENT`
- ADR impact: no new ADR required

## Plain falsifiable claim

A fresh isolated authenticated Codex CLI was run from a disposable committed Git workspace without `--skip-git-repo-check`, a trust bypass, or a dangerous sandbox/approval bypass. The CLI passed its workspace trust gate and reached the provider execution boundary, but the provider returned a workspace-credit availability error before producing schema-constrained output. Therefore restored authentication can pass the trust gate, but successful schema-constrained generation remains unproved.

## Relationship to the prior blocked canary

The prior `BLOCKED_ENVIRONMENT` canary remains unchanged historical evidence: it stopped before provider execution because the temporary directory was not a trusted Git workspace. This proof isolates that boundary by using a committed disposable Git repository. The new failure is later and distinct: provider execution begins, then fails because the workspace is out of credits. It is not an authentication, trust-gate, schema, Runner, or MCP failure.

## Baseline and repository state

The Runner repository began clean on `isolated-auth-proof` at `d8281877baa7d856c7b839f23c484b782cd6511e`.

| Check | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |
| Final Runner worktree | clean except this new proof document before commit |

## Exact trust-check evidence

The prior canary captured this safe stderr:

```text
Not inside a trusted directory and --skip-git-repo-check was not specified.
```

Installed CLI help explicitly documents `--skip-git-repo-check` as allowing execution outside a Git repository. It also documents `--cd <DIR>` for selecting the working root and `--output-schema`, `--json`, and `-o` for the structured-output path. This proof did not use `--skip-git-repo-check`, `--dangerously-bypass-hook-trust`, or any other trust, sandbox, approval, or repository-check bypass. The committed Git workspace is the tested non-bypass posture; the exact requirement beyond “inside a committed Git repository” is not claimed as fully specified by the installed help.

## Isolated authenticated posture

| Surface | Result |
| --- | --- |
| Active CLI | `/opt/homebrew/bin/codex`, `codex-cli 0.36.0` |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex`, `codex-cli 0.144.6` |
| `--output-schema` advertised | yes |
| Authentication status | `Logged in using ChatGPT` |
| Configured MCP servers | zero; `mcp list --json` returned `[]` |
| Fresh isolated home root | `/tmp/codex-isolated-auth-restoration-proof/codex-home` |

Only coarse authentication status was recorded. Authentication-file contents, tokens, cookies, account identifiers, email addresses, and private configuration were not read or recorded.

## Disposable trusted workspace

- Path: `/tmp/codex-cli-trust-gate-canary-proof/workspace`
- Repository root: same path
- Branch: `main`
- Initial commit: `f3952ef` (`proof: initialize trusted canary workspace`)
- Tracked files: only `README.md` and `.gitignore`
- Initial status: `## main`
- Final status: `## main`
- Directory posture: proof root and workspace mode `0700` under `umask 077`
- Workspace integrity: unchanged; `git diff --stat` and `git diff --name-only` were empty, and `git ls-files --others --exclude-standard` returned no paths

## Canary execution

Exactly one provider execution attempt was made. No retry or second provider call occurred.

Redacted command shape:

```text
CODEX_HOME=<fresh-isolated-home> <isolated-codex> exec --json --output-schema <PROOF_ROOT>/schema.json -o <PROOF_ROOT>/output.json <prompt>
```

The process working directory was `<PROOF_ROOT>/workspace`. No bypass flag was present.

- Timeout: 120 seconds
- Start: `2026-07-25T01:54:55.593327+00:00`
- End: `2026-07-25T01:55:04.150906+00:00`
- Duration: 8.557 seconds
- Exit code: 1
- Trust gate: passed
- Provider execution reachability: reached; `thread.started` and `turn.started` events were observed
- JSON-event terminal state: no `turn.completed`; terminal `turn.failed` was observed
- Safe event error: `Your workspace is out of credits. Ask your workspace owner to refill in order to continue.`
- Output file: absent; no output file was created, so file size is not applicable
- JSON parse: not applicable because no output file existed
- Schema validation: not applicable because no output file existed
- Exact safe object: none
- Process cleanup: no process-group members remained after exit

The bounded launcher invoked an argument array, captured stdout and stderr, used a separate process group, removed API-token environment variables, enforced the timeout, and checked workspace status before and after execution.

## Classification

`BLOCKED_ENVIRONMENT` is the only truthful classification. The trust gate passed, the provider accepted the request far enough to emit `thread.started` and `turn.started`, and the turn then failed on a post-auth workspace-credit limit. This is not `PASS_TRUST_GATE_CANARY` because there was no terminal completion, output file, JSON parse, schema validation, exact object, or successful provider result. It is not `TRUST_GATE_REJECTED` because the workspace was accepted. It is not `AUTHENTICATION_REJECTED` because no authentication rejection occurred. It is not `PROCESS_TIMEOUT` because the process exited in 8.557 seconds.

## Security, redaction, and limits

- No trust or repository-check bypass was used.
- No authentication file or credential content was inspected, copied, modified, or committed.
- No MCP server was configured.
- DeepSeek received only the sanitized proof context, not credentials, authentication state, private configuration, or the isolated home.
- No Runner, MCP, test, prompt, schema, skill, README, package, or production file changed.
- Direct Codex execution is a bounded proof control, not Runner authority.
- This does not prove Stage-A execution, Runner subprocess behavior under successful generation, MCP semantic completion, campaign compilation, or any supported CLI version range.
- No production or release claim changes.

## Warnings separated from failures

- Warning: installed help documents the skip option and working-root option, but does not fully define the trust policy beyond the observed Git-repository boundary.
- Failure boundary: the authenticated provider execution reached the service boundary but was unavailable because the workspace was out of credits.
- The disposable workspace remained clean, so no source or receipt mutation occurred.
- This is a single canary sample; no persistence or repeatability claim is made. A second provider attempt was expressly outside this task's one-call budget.
- The active CLI is `0.36.0` while the isolated proof CLI is `0.144.6`; this proof makes no compatibility or supported-version inference from that difference.

## Remaining unproved surfaces and next task

The remaining prerequisite is workspace/provider-credit availability for one future explicitly authorized canary. Runner instrumentation remains blocked. The semantic MCP campaign must not be rerun.

Remaining unproved surfaces include successful schema-constrained generation, exact output validation under the restored authentication, Stage-A execution, successful Runner subprocess lifecycle, MCP semantic completion, campaign compilation, and a supported CLI version range.

Only a future `PASS_TRUST_GATE_CANARY` would authorize: “Add temporary read-only event and process instrumentation around the current Runner provider seam, then execute one successful Stage-A invocation outside MCP.” This proof did not reach that classification.

## Reproduction commands without credentials

```bash
CODEX_BIN=/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex
CODEX_HOME=/tmp/codex-isolated-auth-restoration-proof/codex-home
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" --version
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" login status
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" mcp list --json
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" exec --help
git -C /tmp/codex-cli-trust-gate-canary-proof/workspace status --short --branch --untracked-files=all
```

Do not rerun the provider command without a new explicit one-call authorization and restored provider availability.

## DeepSeek delegation receipt

- Mode: `review`
- Preflight: passed; explicit `CODEX_DEEPSEEK_EXTERNAL_PROVIDER_ACK=1` was present
- Selected model: not exposed by the delegation result
- Result artifact path: `/var/folders/kj/mnb6b7ds2sq__bjhmglf5xyh0000gn/T//pi-deepseek-result.7fU9MN`
- Accepted findings: output-file wording clarified; single-sample limitation recorded without retry; CLI-version gap called out; post-auth credit classification boundary made explicit; workspace diff and untracked-file checks recorded
- Rejected findings: no second canary/repeatability run, because the task authorizes exactly one provider attempt
- Already covered: no trust bypass, process cleanup, timeout boundary, and negative Runner/MCP/campaign claims were already explicit
- Codex verification: independently checked the result against `run-summary.json`, captured stdout/stderr, output-file absence, clean workspace status, empty diff/untracked checks, and the report constraints. No DeepSeek finding changed the Codex-owned classification.
- Remaining uncertainty: advisory review is not evidence of provider success and cannot change the Codex-owned classification

DeepSeek may review only sanitized evidence. It may not edit files, inspect credentials, run provider commands, or authorize the next task.

## Repository integrity

Exactly this proof document is authorized for the Runner repository. The two earlier proof documents remain unchanged. Temporary workspace, canary, and review artifacts remain outside Git.
