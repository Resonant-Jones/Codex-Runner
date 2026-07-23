# Codex Isolated Authentication Restoration Proof

- Status: Live Proof
- Date and timezone: 2026-07-23 EDT (UTC-04:00); evidence captured 2026-07-23T19:01Z through 2026-07-23T19:21Z
- Machine: `AxisNode.local`
- Execution lane: architecture-impact
- Task kind: proof
- Repository path: `codex-runner-friend-share` (local user-directory prefix redacted)
- Branch and starting HEAD: `isolated-auth-proof` at `458f30cd8b2aef7f260ba630228368a002e8e5c7`
- Final classification: `BLOCKED_OPERATOR_INTERACTION`
- ADR impact: no new ADR required. Authentication remains an environment/operator responsibility; direct CLI use is a bounded proof control, while product provider execution remains behind Runner.

## Plain falsifiable claim

A fresh auth-only `CODEX_HOME` was created with restrictive permissions and zero MCP servers. The documented `codex login --device-auth` flow was initiated three times against isolated Codex CLI 0.144.6. The operator did not complete the browser-based device-authorization step during any of the three sessions. Therefore, no authenticated provider canary could be run, and the claim that a fresh isolated authentication posture can complete a provider call today remains unproved.

This does **not** prove that fresh authentication is impossible. It proves only that the documented flow requires operator interaction that was not completed during this proof window.

## Explicit limits

- Direct Codex invocation is a proof control, not a product authority path.
- One CLI version does not establish a supported version range.
- This proof does not prove Stage-A execution, Runner subprocess behavior, MCP semantic completion, or campaign compilation.
- No release, provider-support, production-readiness, or release-readiness claim changes.
- No Runner, MCP, test, prompt, schema, skill, package, or README file changed.
- The prior `UNRESOLVED_WITH_BOUNDED_EVIDENCE` classification from the Runner subprocess diagnostic is unchanged.
- `BLOCKED_OPERATOR_INTERACTION` does not imply any technical flaw in the CLI, the authentication flow, the provider, or the network.

## Baseline and CLI evidence

Initial repository state on branch `isolated-auth-proof`:

| Check | Result |
| --- | --- |
| HEAD | `458f30cd8b2aef7f260ba630228368a002e8e5c7` |
| Branch | `isolated-auth-proof` |
| Worktree | clean; no tracked or untracked changes |

Test baseline:

| Command | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |

| Surface | Evidence |
| --- | --- |
| Active CLI (unchanged) | `/opt/homebrew/bin/codex`; `codex-cli 0.36.0` |
| Isolated CLI | `/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex`; `codex-cli 0.144.6` |
| Package | `@openai/codex@0.144.6` (reused from prior proof; not reinstalled or upgraded) |
| `--output-schema` advertised | yes: `--output-schema <FILE>` documented in `codex exec --help` |
| `--json` advertised | yes |
| `--device-auth` advertised | yes: `codex login --help` lists `--device-auth` |
| `--ignore-user-config` advertised | yes |
| Active CLI modified | no; `codex --upgrade` was not run |

## Authentication interface discovery

The installed isolated CLI documents these authentication surfaces:

| Surface | Evidence |
| --- | --- |
| `codex login` | top-level `login` subcommand with `--device-auth`, `--with-api-key`, and `--with-access-token` |
| `codex login status` | documented subcommand for checking login state |
| `codex logout` | documented subcommand for removing stored credentials |

`--with-api-key` and `--with-access-token` read credential values from stdin. These were not used, per the task instruction not to paste credential values into the shell. The only operator-eligible flow is `--device-auth`, which requires browser-based confirmation at `https://auth.openai.com/codex/device` with a one-time code.

## Fresh CODEX_HOME environment

| Dimension | Evidence |
| --- | --- |
| Proof root | `/tmp/codex-isolated-auth-restoration-proof` |
| CODEX_HOME | `/tmp/codex-isolated-auth-restoration-proof/codex-home` |
| Directory permission posture | `umask 077`; both directories mode `0700` (`drwx------`), owner `resonant_jones` |
| Copied from prior auth homes | no; neither the revoked auth-only home (`/tmp/codex-stage-a-provider-diagnostic/clean-home`) nor the operator's normal Codex home nor any other proof root was copied |
| Normal operator configuration | neither read, copied, nor modified |

The only content created under the fresh `CODEX_HOME` after the three login attempts is CLI-generated metadata:

- `log/codex-login.log` (mode `0600`, 252 bytes; contents not inspected)
- `tmp/` directory tree (runtime scratch; no credentials)

No `auth.json`, `config.toml`, or MCP configuration exists.

## Authentication attempts

Three `codex login --device-auth` sessions were initiated against the fresh `CODEX_HOME` using isolated CLI 0.144.6:

| Attempt | Time window | Timeout | Result |
| --- | --- | --- | --- |
| 1 | ~15:01 EDT | 300 s | timed out; operator did not complete browser confirmation |
| 2 | ~15:06 EDT | 900 s | timed out; operator did not complete browser confirmation |
| 3 | ~15:21 EDT | 120 s | timed out; operator did not complete browser confirmation |

Each attempt displayed the canonical device-auth URL (`https://auth.openai.com/codex/device`) and a one-time code valid for 15 minutes. The verification URL and codes are not recorded in this report.

Post-attempt state:

| Check | Result |
| --- | --- |
| `codex login status` | `Not logged in` (exit code 1) |
| `auth.json` | absent |
| `config.toml` | absent |

## Configuration posture verification

| Dimension | Evidence |
| --- | --- |
| `codex mcp list --json` | `[]` |
| Configured MCP servers | zero |
| `config.toml` | absent |
| Manually added tool configuration | none |
| Copied normal configuration | none |
| Contents inspected | only directory listings, file permissions, and login-status boolean; no file content was printed |

## Provider canary

No provider canary was run, because no authenticated session was established. The schema (`status: "ok"`, `value: 7`), prompt (`{"status":"ok","value":7}` only, no files, no commands), output path, and bounded launcher were prepared but never invoked against a live authenticated provider.

## Process cleanup

No Codex process was observed running after the three login attempts timed out. A post-sweep `pgrep` for `codex` returned no matches in the proof's process space.

## One authorized next task

Classification `BLOCKED_OPERATOR_INTERACTION` maps to no authorized advancement. The specific prerequisite that remains unresolved is:

> Operator completion of the documented `codex login --device-auth` browser-based device-authorization flow against a fresh `CODEX_HOME`.

Runner instrumentation remains blocked. The semantic campaign retry is not authorized. The original seven-minute stall remains classified `UNRESOLVED_WITH_BOUNDED_EVIDENCE`.

No alternative authentication mechanism was identified in the installed CLI help beyond `--with-api-key` and `--with-access-token`, both of which require pasting credential values into stdin and were not used per the task's credential-handling invariants.

## Security and redaction confirmation

- No credential, token, cookie, API key, authorization header, account identifier, authentication-file content, or private user-directory path is present in this report.
- The device-auth verification URL (`https://auth.openai.com/codex/device`) is a public endpoint and is recorded only as the documented flow target.
- One-time verification codes were displayed during each login attempt but are not recorded in this report.
- The login log file under `$CODEX_HOME/log/` was not inspected; its size is recorded as metadata only.
- A credential-pattern scan over this report returned no match.
- The active CLI was not upgraded, replaced, or modified.
- Normal operator configuration was neither read nor modified.

## Warnings (separated from failures)

- **Warning (environmental, not a code failure):** the documented device-auth flow requires real-time browser interaction and could not complete within any of the three proof sessions. This is a proof-session constraint, not evidence that the flow is broken.
- **Warning:** no alternative non-interactive authentication flow is documented by the installed CLI 0.144.6 beyond stdin-based API key or access token submission, both of which were excluded by the task's credential-handling invariants.

## Remaining unproved surfaces

- Fresh isolated authentication posture (blocked at operator interaction)
- Provider call under fresh authentication
- Schema-constrained generation under fresh authentication
- The original 2026-07-20 seven-minute MCP-path stall root cause
- Runner behavior under a successful long-running provider call
- Semantic campaign compilation
- MCP response return above the Runner boundary
- Codex CLI compatible version range beyond 0.144.6

## Required report statements

- Authentication files that would be created upon successful login are temporary and uncommitted.
- No credential contents were inspected or recorded.
- Direct Codex invocation is a proof control, not the Runner authority path.
- This proof does not prove Stage-A execution.
- This proof does not prove Runner subprocess behavior.
- This proof does not prove MCP semantic completion.
- This proof does not prove campaign compilation.
- One CLI version does not establish a supported range.
- No release claim changes.
- No production implementation changed.

## Reproducibility commands

Commands that do not contain credentials:

```bash
# Create fresh secure CODEX_HOME
PROOF_ROOT=/tmp/codex-isolated-auth-restoration-proof
rm -rf "$PROOF_ROOT"
umask 077
mkdir -p "$PROOF_ROOT/codex-home"

# Isolated CLI
PROOF_CODEX=/tmp/codex-cli-output-schema-proof/codex-install/node_modules/.bin/codex
CODEX_BIN_DIR=$(dirname "$PROOF_CODEX")

# Initiate device-auth flow
CODEX_HOME="$PROOF_ROOT/codex-home" PATH="$CODEX_BIN_DIR:$PATH" \
  "$PROOF_CODEX" login --device-auth

# Check status after browser confirmation
CODEX_HOME="$PROOF_ROOT/codex-home" PATH="$CODEX_BIN_DIR:$PATH" \
  "$PROOF_CODEX" login status

# Verify MCP posture
CODEX_HOME="$PROOF_ROOT/codex-home" PATH="$CODEX_BIN_DIR:$PATH" \
  "$PROOF_CODEX" mcp list --json

# After successful authentication, run the canary:
# CODEX_HOME="$PROOF_ROOT/codex-home" PATH="$CODEX_BIN_DIR:$PATH" \
#   "$PROOF_CODEX" exec --json --sandbox read-only --skip-git-repo-check --ephemeral \
#   --ignore-user-config --color never --output-schema "$PROOF_ROOT/schema.json" \
#   -o "$PROOF_ROOT/canary-output.json" - < "$PROOF_ROOT/prompt.txt"
```

## Repository integrity

Initial and final `git status --short --branch` on `isolated-auth-proof`: clean; no tracked or untracked changes except this report file.

| Command | Result |
| --- | --- |
| `pytest -q tests/test_codex_cli_compatibility.py` | 11 passed |
| `pytest -q tests/test_mcp_server.py` | 13 passed |
| `pytest -q` | 171 passed, 1 skipped |
| `git diff --check` | PASS |
| Report credential-pattern and identity/account/private-path review | PASS |
| Final status | exactly one modified report file staged |

Warnings separate from failures:

- The documented authentication flow could not complete because it requires operator browser interaction that did not occur during the proof sessions.
