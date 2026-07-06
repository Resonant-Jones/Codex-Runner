# Guardian Plan Pack Validator Operator Runbook

## Status

- **Status:** operator runbook
- **Scope:** docs-only interpretation guide for the plan pack validator
- **Runtime impact:** none
- **Intended reader:** Chris (human operator), Axis (architecture voice), and Guardian when it becomes operational
- **Dependency:** `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`

This runbook teaches you how to read the validator.

It does **not** let the validator operate anything.

> The validator checks the bowl. It does not animate Guardian.

---

## 1. Purpose

The Guardian Plan Pack validator is a read-only structural scanner. You point it at a plan pack directory and it tells you:

- whether the plan pack has all required files
- whether the plan pack declares the required boundary signals
- whether `TASK_SPEC.yaml` parses, has its required fields, and is in `dry_run` mode
- whether the required `FLAG###` escalation banner is present
- whether the plan pack is structurally complete enough for Guardian to **read**

The validator never executes a plan, invokes Pi Loop, touches Codexify, mutates files, or grants authority. It only describes structural completeness.

This runbook exists so operators do not misread a structural pass as approval to operate.

---

## 2. When to use the validator

Use the validator when you want to confirm a plan pack is structurally readable without acting on it, for example:

- before handing a plan pack to Guardian for a session
- after editing a plan pack's boundaries, task spec, or escalation section
- when triaging why a plan pack is not ready for Guardian to read
- when explaining to a reviewer what a plan pack is still missing

Do not use the validator to:

- approve a plan for execution
- authorize Guardian to operate
- authorize Pi Loop invocation
- repair a plan pack automatically
- mutate Codexify durable state

If you find yourself wanting the validator to *do* something, stop. It is not built for that. The next slice for any operational action is a separate, explicitly approved task with Chris's sign-off.

---

## 3. Commands

The validator is available through the `codexrun` console script and through the module entrypoint.

### 3.1 Human-readable report (default)

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/
```

Prints a fixed-section text report to stdout.

### 3.2 JSON report

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --json
```

Prints a single JSON object to stdout. Same validation result as the human-readable form.

### 3.3 Module entrypoint

When the `codexrun` console script is not on PATH, the same commands work through the module entrypoint:

```bash
python3 -m codex_runner.runner guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/ --json
```

(Equivalently, `python3 -m codex_runner guardian validate-plan-pack --path <dir> --json` via the package `__main__`. From a raw repo checkout, `python3 -m src.codex_runner.runner guardian ...` also resolves, but `codex_runner.runner` is the canonical module path.)

### 3.4 Exit codes

Both modes share the same exit-code rule, unchanged by `--json`:

- exit `0` when the plan pack passes validation (structurally complete enough to read)
- exit `1` when the plan pack fails validation

A `0` exit means the plan pack is structurally complete enough to read. It does **not** mean the plan is approved, that Guardian may operate, or that Pi Loop may be invoked.

### 3.5 Session logs (`--write-session-log`)

By default the validator writes nothing. Add `--write-session-log` to emit one generated session log that records the validation run outcome:

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --write-session-log
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --json --write-session-log
```

The session log is written under a generated, git-ignored path:

```txt
.guardian/sessions/<timestamp>-validate-plan-pack-<slug>.json
```

Session-log rules:

- A session log records that validation **happened**. It does not approve the plan.
- A session log does not make Guardian operational, authorize Pi Loop invocation, authorize Codexify ingestion, or mutate durable state.
- Session logs are **generated output**, not source authority. `.guardian/sessions/` is listed in `.gitignore` (see `docs/review/CODEX_RUNNER_GENERATED_ARTIFACT_HYGIENE.md`).
- The `authority` block in every session log reuses the validator's nine authority locks and keeps them all `false`.
- `--write-session-log` works with both human-readable and `--json` output. It does not change the exit code: `0` on pass, `1` on fail. A failed validation still writes a session log recording the failure.

Without `--write-session-log`, the validator remains strictly read-only and writes no files.

### 3.6 Validation receipts (`--write-receipt`)

`--write-receipt` writes a stronger, referenceable evidence artifact than a session log:

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --write-receipt
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --json --write-receipt
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --write-session-log --write-receipt
```

The receipt is written under a generated, git-ignored path:

```txt
.guardian/receipts/<timestamp>-plan-pack-validation-<slug>.json
```

Receipt rules:

- A validation receipt records that a plan-pack validation scan happened. It is evidence, **not** approval, **not** durable truth, **not** Codexify ingestion.
- A validation receipt does not make Guardian operational, authorize Pi Loop invocation, authorize Codexify ingestion, or mutate durable state.
- The `evidence` block pins `evidence_not_authority: true`, `approval_granted: false`, `execution_performed: false`, `codexify_ingestion_performed: false`, `durable_mutation_performed: false`.
- The `authority` block reuses the validator's nine authority locks and keeps them all `false`.
- The `report` block serializes from the same validator result used by text/JSON output (no duplicated validation logic).
- The `plan_pack_manifest` block fingerprints the eight required plan-pack files with SHA-256 (`hash_algorithm: sha256`). Each present file records `present: true`, a lowercase-hex `sha256` digest of its bytes exactly as stored, and an integer `size_bytes`. Missing files record `present: false` with `sha256: null` and `size_bytes: null`. Hashes cover **only** the required plan-pack files — never arbitrary repo contents, `.guardian/`, `.pi/`, source, tests, or generated outputs. Symlinks are treated conservatively as not-present.
- Manifest hashes help compare whether the plan pack changed after validation. They are **evidence integrity metadata, not approval**.
- Validation receipts are **generated output**, ignored by git (`.guardian/receipts/` is in `.gitignore`). They are evidence artifacts, not source authority.
- Validation receipts **do not replace** session logs. `--write-session-log` and `--write-receipt` compose and write one of each.
- A failed validation still writes a receipt recording the failure (`valid: false`), and the exit code is unchanged: `0` on pass, `1` on fail.

Without `--write-receipt`, the validator writes no receipt. (Default validation remains strictly read-only unless `--write-session-log` or `--write-receipt` is passed.)

### 3.7 Dry-run orchestration preflight (`orchestrate-dry-run`)

`orchestrate-dry-run` is the first operational stub. It is **preparation-only**: it reads a validated Plan Pack plus a Guardian validation receipt, verifies preconditions and SHA-256 manifest continuity, and may write a local orchestration record. It does **not** invoke Pi Loop, execute the plan, mutate source, touch Codexify, apply patches, dispatch, merge, or promote trust.

```bash
codexrun guardian orchestrate-dry-run \
  --plan-pack <plan-pack-dir> --require-receipt <receipt-path>
codexrun guardian orchestrate-dry-run \
  --plan-pack <plan-pack-dir> --require-receipt <receipt-path> --json
codexrun guardian orchestrate-dry-run \
  --plan-pack <plan-pack-dir> --require-receipt <receipt-path> --write-orchestration-log
```

The orchestration record (only with `--write-orchestration-log`) is written under a generated, git-ignored path:

```txt
.guardian/orchestrations/<timestamp>-guardian-operated-dry-run-<slug>.json
```

`--write-orchestration-receipt` (optional, composes with `--json` and `--write-orchestration-log`) writes a stronger, referenceable orchestration receipt under a separate git-ignored path:

```txt
.guardian/orchestration-receipts/<timestamp>-guardian-operated-dry-run-receipt-<slug>.json
```

The orchestration receipt (`receipt_type: guardian_dry_run_orchestration`, `receipt_version: v0`) wraps the preflight result and adds `inputs.validation_receipt` (SHA-256 + `size_bytes` of the validation receipt file itself) and `inputs.plan_pack_manifest` (the preflight's hash verification). It records that a preflight occurred. It is **not** approval, **not** dispatch, **not** Pi Loop invocation authority, **not** execution proof, and **not** Codexify ingestion. A validation-receipt hash proves receipt file continuity, not correctness. Guardian may prepare a record; Guardian may not execute the dry run.

Preflight rules:

- `orchestrate-dry-run` verifies Plan Pack validation receipt continuity (type/version, `validation.valid`, all authority locks false, all evidence flags non-authoritative, manifest `hash_algorithm: sha256`, and that each required file's current SHA-256 still matches the receipt). It does not execute the plan.
- It requires the Plan Pack's `AUTHORIZATION.md` to contain `dry-run orchestration preparation allowed`, and rejects obvious boundary-conflict phrases in `BOUNDARIES.md`.
- Resolved plan-pack and receipt paths must be inside `/Volumes/Dev_SSD/Codex-Runner` and outside both Codexify repos.
- Exit codes: `0` when all preconditions pass, `1` when any fail. A failure still writes a failure record with `--write-orchestration-log`.
- The `authority` block stays all `false` (including `guardian_operational`, `pi_loop_invocation_allowed`); the `evidence` block pins `execution_performed`, `pi_loop_invoked`, `codexify_ingestion_performed`, `durable_mutation_performed`, `source_mutation_performed`, and `approval_granted` all `false`.
- Orchestration records are generated evidence, not execution, not approval, and not source authority. `.guardian/orchestrations/` is git-ignored.

This stub is governed by `GUARDIAN_OPERATIONAL_CONTRACT_ADDENDUM_V0.md`. It prepares the road; it does not drive.

---

## 4. How to read human-readable output

The text report is organized into fixed sections. Read it top to bottom.

```text
Guardian Plan Pack Validation Report

Plan pack:
  path:                  the plan pack directory scanned
  valid:                 true | false

Required files:
  <name>: present | missing   (one line per required file)

Boundary checks:
  forbidden Codexify-main path declared: true | false
  forbidden Codexify-Core path declared: true | false
  authority is not self-promotable:      true | false
  no Codexify ingestion authorization:   true | false
  no durable mutation authorization:     true | false
  no provider execution authorization:   true | false
  no patch application authorization:    true | false
  no dispatch authorization:             true | false
  no merge automation authorization:     true | false
  no automatic reviewer decisions authorization: true | false
  no trust-level auto-promotion authorization:    true | false

Task spec:
  yaml parses:           true | false
  mode is dry_run:       true | false
  required fields present: true | false

Escalation:
  FLAG### banner present: true | false

Result:
  pass | fail

Reason:
  <one-line explanation, or the first issue if invalid>
```

The `valid` line and the `Result` line always agree. If they ever disagree, treat the report as suspect.

---

## 5. How to read JSON output

The JSON report (`--json`) emits one object. The field set is fixed and is documented in section 6.

When reading JSON programmatically:

- Read `valid` first. If `false`, read `issues` for what failed; do not treat the plan pack as readable.
- Read `result` to confirm `"pass"` or `"fail"`.
- Read the `authority` block. All nine locks **must** be `false`. If any is ever not `false`, stop and treat the output as suspect.
- Read `required_files`, `boundary_checks`, `forbidden_path_checks`, `task_spec`, and `escalation` to see which specific checks passed or failed.

The JSON object is the same validation result as the human-readable form, just shaped for a machine reader. It is **not** permission to operate Guardian, execute a plan, or invoke Pi Loop.

The JSON shape is frozen by snapshot fixtures:
- `tests/fixtures/guardian_plan_pack_validator_json_valid.json`
- `tests/fixtures/guardian_plan_pack_validator_json_invalid.json`

---

## 6. Field meanings

Plain-language meanings for the fields emitted by the JSON report.

### `plan_pack_path`

The resolved absolute path of the plan pack directory you scanned. The validator never writes to this directory.

### `valid`

Whether the plan pack passed all structural and boundary checks.

- `valid: true` means the plan pack is structurally complete enough to read.
- `valid: true` does **not** mean the plan is approved.
- `valid: true` does **not** mean Guardian may operate.
- `valid: true` does **not** mean Pi Loop may be invoked.
- `valid: false` means the plan pack failed structural or boundary checks.
- `valid: false` does **not** authorize automatic repair.

### `required_files`

A mapping of each required file name to whether it is present (`true`) or missing (`false`). The required files are:

```txt
README.md, PLAN.md, GOALS.md, BOUNDARIES.md,
AUTHORIZATION.md, ESCALATION.md, SESSION_LOG.md, TASK_SPEC.yaml
```

`required_files` checks file **presence** only. It does not check file content, correctness, or human authorization.

### `boundary_checks`

A mapping of boundary-signal labels to whether the plan pack declares that boundary (`true`) or not (`false`). The validator scans the normalized text of the required files for conservative signal phrases. The nine boundary signals are:

```txt
authority is not self-promotable
no Codexify ingestion authorization
no durable mutation authorization
no provider execution authorization
no patch application authorization
no dispatch authorization
no merge automation authorization
no automatic reviewer decisions authorization
no trust-level auto-promotion authorization
```

`boundary_checks` are conservative **signals**, not full semantic proof. A `true` means the expected phrase is present; it does not mean the plan pack's intent is safe or fully analyzed.

A companion `forbidden_path_checks` mapping records whether the two out-of-bounds repo paths (`/Volumes/Dev_SSD/Codexify-main`, `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`) are declared as forbidden in the plan pack boundaries and task spec.

### `task_spec`

Three checks against `TASK_SPEC.yaml`:

- `yaml_parses` — the file parses as a YAML mapping.
- `mode_is_dry_run` — the `mode` field equals `dry_run`. The validator only accepts `dry_run`.
- `required_fields_present` — all required task fields are present.

The required task fields are:

```txt
task_id, title, repo_root, mode, intent, scope, non_goals,
allowed_paths, forbidden_paths, allowed_commands, forbidden_commands,
validation, acceptance_criteria, expected_artifacts,
escalation_triggers, notes
```

`task_spec` checks **structure** (YAML parsing, required fields, and mode). It does not validate that the task is semantically correct or safe to execute.

### `escalation`

One check:

- `flag_banner_present` — the `FLAG### HUMAN OPERATOR DECISION REQUIRED` banner appears in the plan pack's required files.

`escalation` checks that the banner **exists**. It does not check that any individual escalation flag is well-formed.

### `issues`

A list of `{section, message}` objects describing every check that failed. Empty when `valid: true`.

`issues` explain what failed. They are diagnostic, not enforcement actions. They do not authorize the validator — or any reader — to repair anything automatically.

### `result`

The outcome token: `"pass"` or `"fail"`.

- `result: pass` means validation passed, **not** execution approval.
- `result: fail` means validation failed, **not** that the plan's intent is bad.

`result` always agrees with `valid`.

### `reason`

A one-line explanation. When `valid: true`, it states the plan pack is structurally complete enough to be read by Guardian. When `valid: false`, it is the first issue's message.

### `authority`

A fixed block of nine authority locks. See section 8.

---

## 7. Pass and fail meanings

### Pass

```yaml
valid: true
result: pass
```

A pass means: the plan pack has all required files, declares all required boundary signals, has a `TASK_SPEC.yaml` that parses with all required fields in `dry_run` mode, and contains the `FLAG###` escalation banner.

A pass means the plan pack is **structurally readable** by Guardian. It does **not** mean:

- the plan is approved
- Guardian may operate
- Pi Loop may be invoked
- Codexify may be touched
- any durable action is authorized

### Fail

```yaml
valid: false
result: fail
reason: <short explanation>
```

A fail means: at least one structural or boundary check did not pass. Read `issues` for the full list.

A fail does **not** mean:

- the plan's underlying intent is bad
- Guardian may repair the plan pack automatically
- the work is permanently blocked

A fail is a "repair the plan pack, then revalidate" signal. The repair is a manual or separately-approved docs task, never an automatic validator action.

---

## 8. Authority locks

Every JSON report — pass or fail — emits this fixed `authority` block:

```json
{
  "guardian_operational": false,
  "plan_execution_allowed": false,
  "pi_loop_invocation_allowed": false,
  "codexify_ingestion_allowed": false,
  "durable_mutation_allowed": false,
  "provider_execution_allowed": false,
  "patch_application_allowed": false,
  "dispatch_allowed": false,
  "merge_allowed": false
}
```

These locks describe what the **validator itself** will never do. They are not computed from the plan pack; they are constant guarantees. They are hardcoded `false` and pinned by the snapshot fixtures.

| Lock | Meaning |
| --- | --- |
| `guardian_operational` | The validator does not start or run Guardian. |
| `plan_execution_allowed` | The validator does not execute the plan. |
| `pi_loop_invocation_allowed` | The validator does not invoke Pi Loop. |
| `codexify_ingestion_allowed` | The validator does not ingest anything into Codexify. |
| `durable_mutation_allowed` | The validator does not mutate durable state. |
| `provider_execution_allowed` | The validator does not run a provider. |
| `patch_application_allowed` | The validator does not apply patches. |
| `dispatch_allowed` | The validator does not dispatch work. |
| `merge_allowed` | The validator does not merge anything. |

If any lock is ever not `false`, stop and treat the output as suspect. The validator is a scanner; it checks the bowl. It does not animate Guardian, execute plans, invoke Pi Loop, touch Codexify, or mutate durable state.

---

## 9. Common mistakes

These are the misreadings this runbook exists to prevent.

- Do not treat `valid: true` as plan approval. It only means structural completeness.
- Do not treat `result: pass` as permission to execute. It is a validation outcome, not an execution authorization.
- Do not treat a structurally valid plan pack as human authorization. Chris's sign-off lives in `AUTHORIZATION.md`, not in the validator output.
- Do not use the validator to repair plan packs automatically. The validator is read-only.
- Do not invoke Pi Loop from validator output. `pi_loop_invocation_allowed` is `false`.
- Do not mutate Codexify from validator output. `codexify_ingestion_allowed` is `false`.
- Do not promote Guardian authority from validator output. `guardian_operational` is `false`.
- Do not treat `boundary_checks` as perfect semantic analysis. They are conservative signal checks, not full intent proof.
- Do not treat `required_files` presence as content correctness. Presence is not quality.
- Do not confuse `valid: false` with "the plan's intent is bad." A fail is a structural gap, not an intent judgment.

---

## 10. What to do next

Safe next actions, by validator outcome.

### If validation passes (`valid: true`, `result: pass`)

Preserve the plan pack as structurally readable and wait for an explicitly authorized next step. A pass does not start Guardian. The next step (Guardian session, dry-run, execute) requires separate Chris authorization per the operating contract.

### If validation fails (`valid: false`, `result: fail`)

Inspect `issues`. Repair the plan pack manually or through a separate docs-only task (add a missing file, add a missing boundary declaration, fix `TASK_SPEC.yaml`, restore the `FLAG###` banner). Then validate again.

### If any authority lock is not `false`

Stop and treat the output as suspect. All nine locks must always be `false`. Do not proceed until the cause is understood.

### If `boundary_checks` fail

Do not proceed until the missing boundary declarations are repaired. Each missing signal is a required declaration, not a suggestion.

### If `forbidden_path_checks` fail

The plan pack must declare `/Volumes/Dev_SSD/Codexify-main` and `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core` as out-of-bounds. Restore those declarations before revalidating.

### If `TASK_SPEC.yaml` fails (parse / mode / fields)

Repair the task spec before any future dry-run consideration. The validator only accepts `mode: dry_run`; any other mode fails. Missing required fields must be added.

### If `escalation.flag_banner_present` is `false`

Restore the `FLAG### HUMAN OPERATOR DECISION REQUIRED` banner into the plan pack. The banner is required; its absence is a hard fail.

---

## 11. What not to do

A short, explicit list. If you are about to do any of these, stop.

- Do not execute the plan pack based on validator output.
- Do not invoke Pi Loop based on validator output.
- Do not make Guardian operational based on validator output.
- Do not ingest anything into Codexify based on validator output.
- Do not mutate WorkOrder lifecycle, Execution Ledger, or any durable state based on validator output.
- Do not run providers, apply patches, dispatch, or merge based on validator output.
- Do not auto-fill reviewer decisions or auto-promote trust levels based on validator output.
- Do not use the validator to modify plan pack files. It is read-only.
- Do not introduce new authority semantics, lifecycle states, or report classifications. Those require a separate, explicitly approved task.
- Do not modify `/Volumes/Dev_SSD/Codexify-main` or `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core` to "make the validator do more." Those surfaces are out of bounds.

---

## 12. Related documents

- `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md` — Guardian's role, authority levels, and the plan pack structure this validator checks.
- `docs/guardian/templates/` — blank plan pack templates for each required file.
- `docs/guardian/examples/sample-dry-run-plan-pack/` — the valid sample plan pack used as the validator's golden case.
- `tests/fixtures/guardian_plan_pack_validator_json_valid.json` — frozen JSON snapshot for a valid plan pack.
- `tests/fixtures/guardian_plan_pack_validator_json_invalid.json` — frozen JSON snapshot for an invalid plan pack (missing `FLAG###` banner).
- `src/codex_runner/guardian/plan_pack_validator.py` — the validator source of truth.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md` — the companion runbook for the Pi Loop receipt report scanner.

---

## Bottom line

The validator checks whether Guardian has a complete bowl.

It does not let Guardian drink from it without permission.

Validated bowl. Still no lightning.
