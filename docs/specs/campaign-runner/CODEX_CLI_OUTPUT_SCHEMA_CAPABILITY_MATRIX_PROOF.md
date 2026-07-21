# Codex CLI Output-Schema Capability Matrix Proof

- Date and timezone: 2026-07-20 EDT (America/New_York, UTC-04:00)
- Execution lane: architecture-impact
- Task kind: proof
- Repository branch and starting HEAD: `main` at `92fd67c5764df47293548d222ed946b557f39b71`
- ADR impact: no new ADR impact. This proof aligns with the existing provider
  boundary, mandatory schema-constrained generation, fail-closed capability
  rule, and unchanged MCP transport.
- Overall outcome: `PASS_ALL_POSTURES`

## Claim

The isolated current CLI tested here, `@openai/codex` `0.144.6`, advertises the
exact `--output-schema` capability and produced the exact schema-valid object
`{"status": "ok", "value": 7}` under each tested configuration posture.

This proves compatibility of that one isolated executable in this environment
for this small constrained-output request. It does not establish a compatible
version range.

## Environment and package resolution

| Surface | Evidence |
| --- | --- |
| Active CLI | `/opt/homebrew/bin/codex`; `codex-cli 0.36.0` |
| Active CLI capability | `codex exec --help` exposes `--json` and `--output-last-message`, but not `--output-schema`; unchanged by this task |
| Isolated install root | `/tmp/codex-cli-output-schema-proof/codex-install` |
| Isolated executable | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex` |
| Isolated CLI version | `codex-cli 0.144.6` |
| npm resolution | `@openai/codex@0.144.6`, installed with `npm install --prefix "$PROOF_ROOT/codex-install" @openai/codex@latest` |
| Schema validator | temporary-only `jsonschema 4.26.0` at `$PROOF_ROOT/python-packages` |

The isolated command's local help exited zero and included this exact option:

```text
--output-schema <FILE>
    Path to a JSON Schema file describing the model's final response shape
```

The active installation was not upgraded, replaced, or otherwise modified.

## Fixtures and validation rule

All proof fixtures, outputs, stderr/stdout captures, npm files, and validator
files remain outside Git under `/tmp/codex-cli-output-schema-proof`.

- `schema.json` requires exactly `status: "ok"` and `value: 7`, with
  `additionalProperties: false`.
- `prompt.txt` requests only that object and explicitly prohibits repository
  changes.
- Every executable row used the isolated CLI, read-only sandboxing, an
  ephemeral session, and a temporary non-repository working directory.
- Each output was parsed with Python, validated with `jsonschema`, and compared
  for exact equality with `{"status": "ok", "value": 7}`.

## Configuration discovery

The isolated CLI's local `exec --help` documents both of the following:

- `$CODEX_HOME` is the configuration home; absent an override, the documented
  default config is `~/.codex/config.toml`.
- `--ignore-user-config` does not load `$CODEX_HOME/config.toml` while auth
  continues to use `$CODEX_HOME`.

The local help exposes no separate documented switch that independently
disables all tool availability. Row B therefore uses the documented
comprehensive user-configuration bypass, rather than an invented MCP key or
flag. Under the normal configuration, `codex mcp list --json` reported 10
configured MCP servers; names, commands, arguments, and configuration contents
were not recorded.

## Matrix

`PROOF_ROOT` below means `/tmp/codex-cli-output-schema-proof`; redaction uses
only variable names and contains no credentials.

| Row | Configuration posture | Redacted effective command | Exit / output | JSON and schema result | Classification |
| --- | --- | --- | --- | --- | --- |
| Matrix row A | Isolated `$PROOF_ROOT/clean-home`; a temporary permission-restricted copy of existing auth material only; no `config.toml`, MCP definitions, or tool-enabling config | `CODEX_HOME="$PROOF_ROOT/clean-home" "$PROOF_CODEX" exec -C "$PROOF_ROOT/workspace" --sandbox read-only --skip-git-repo-check --ephemeral --color never --output-schema "$PROOF_ROOT/schema.json" -o "$PROOF_ROOT/row-a-output.json" - < "$PROOF_ROOT/prompt.txt"` | `0`; output present (25 bytes) | parse `PASS`; JSON Schema `PASS`; exact object `PASS` | `PASS` |
| Matrix row B | Normal authentication with `CODEX_HOME` unset (documented default); `--ignore-user-config` explicitly bypasses `$CODEX_HOME/config.toml`, including its local MCP/tool configuration | `env -u CODEX_HOME "$PROOF_CODEX" exec -C "$PROOF_ROOT/workspace" --sandbox read-only --skip-git-repo-check --ephemeral --ignore-user-config --color never --output-schema "$PROOF_ROOT/schema.json" -o "$PROOF_ROOT/row-b-output.json" - < "$PROOF_ROOT/prompt.txt"` | `0`; output present (25 bytes) | parse `PASS`; JSON Schema `PASS`; exact object `PASS` | `PASS` |
| Matrix row C | Normal operator configuration: default configuration home, normal auth, and 10 locally configured MCP servers in aggregate; configuration was not read into this report or modified | `env -u CODEX_HOME "$PROOF_CODEX" exec -C "$PROOF_ROOT/workspace" --sandbox read-only --skip-git-repo-check --ephemeral --color never --output-schema "$PROOF_ROOT/schema.json" -o "$PROOF_ROOT/row-c-output.json" - < "$PROOF_ROOT/prompt.txt"` | `0`; output present (25 bytes) | parse `PASS`; JSON Schema `PASS`; exact object `PASS` | `PASS` |

All three validated outputs were exactly:

```json
{"status": "ok", "value": 7}
```

## Bounded diagnostics and warnings

Captured stdout for each row was the 26-byte JSON object above. Captured stderr
was bounded and was not committed. It contained CLI runtime metadata and the
non-sensitive prompt echo; no credential, API-key, auth-token, account, MCP
command, or MCP argument value was included in this report.

Warnings observed separately from failures:

- The first sandboxed row-A transport attempt could not resolve the provider
  host. The final matrix executions used the approved host network and all
  completed successfully.
- Rows B and C emitted a non-fatal local model-cache compatibility diagnostic.
  Row C also warned that skill descriptions were shortened for context budget.
- Row B emitted a non-fatal MCP transport authentication diagnostic despite the
  documented user-config bypass. No credential value was exposed or committed.
  The flag proves local user configuration bypass, not absence of any
  account-provisioned integration outside that file.

These warnings did not change any exit code, output-file result, JSON parse
result, or schema-validation result. The matrix classification therefore remains
`PASS_ALL_POSTURES`, with the account-provisioned-integration boundary retained
as an explicit limit.

## Repository integrity and redaction

- Initial status: `## main...origin/main` with no tracked or untracked changes.
- Status immediately before adding this report: the same clean status.
- The proof invoked no Runner command, created no Runner artifacts, compiled no
  campaign, and performed no repository mutation.
- The normal Codex configuration and active `/opt/homebrew/bin/codex` remained
  unchanged.
- Temporary auth material was copied only to the isolated temporary home with
  restrictive permissions; its contents were never printed or committed.
- A credential-pattern scan was run over candidate output/log files and the
  final report. A generic authentication-header label in a non-fatal temporary
  diagnostic was redacted from this artifact; no credential value was found.

## Repository validation

| Command | Result |
| --- | --- |
| `test -f docs/specs/campaign-runner/CODEX_CLI_OUTPUT_SCHEMA_CAPABILITY_MATRIX_PROOF.md` | `PASS` |
| Required outcome, matrix-row, and JSON-Schema `grep -E` checks | `PASS` |
| Secret-pattern scan over this report | `PASS`; no credential value matched |
| `git diff --check` | `PASS` |
| `pytest -q tests/test_mcp_server.py` | `PASS`: 13 passed |
| `pytest -q tests/test_codex_cli_compatibility.py` | `FAIL`: 10 passed, 1 failed. The committed test calls `run_task_agent()` without its currently required `prompt_text` keyword, so it raises `TypeError` before the asserted schema-validation path. No Runner code was changed in this proof task. |
| `pytest -q` | `FAIL`: 170 passed, 1 skipped, 1 failed; the same compatibility-test signature mismatch was the only remaining failure when rerun with the filesystem permission needed by Guardian tests. |

The test failure is reported as a pre-existing repository validation failure,
not as evidence against the live output-schema matrix. It is outside this
proof-only task's authorized scope and was not repaired here.

## Decision consequence

`PASS_ALL_POSTURES` authorizes a separate, disposable full Codex Runner MCP
campaign dry-run proof. It does not authorize execute mode, a release-readiness
change, a provider contract change, or a compatibility-range claim.

## Explicit limits and remaining unproved surfaces

- One tested version does not establish a version range.
- Schema-valid output does not prove semantic campaign quality.
- This task does not prove MCP campaign execution.
- This task does not prove Claude compatibility.
- This task does not implement execute mode.
- This task does not change release readiness.
- The tested request is a single small object, not a full audit, campaign, task
  result, receipt, or state-transition flow.
- Row B proves the documented local user-configuration bypass. It does not
  prove that remote or account-provisioned integrations cannot exist outside
  `$CODEX_HOME/config.toml`.
