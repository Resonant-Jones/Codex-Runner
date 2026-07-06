# Guardian Docs Index

## 1. Purpose

This index gives reviewers and operators one place to understand the Guardian surface in `/Volumes/Dev_SSD/Codex-Runner`.

It is a navigation aid. It does not add authority, runtime behavior, or new contracts. It points at the documents, templates, sample pack, validator, and fixtures that already exist.

Guardian is a proposed operating agent layered on top of the Codex Runner diagnostic spine. This index helps you find the pieces that define it — and the pieces that keep it bounded.

---

## 2. Current Status

```txt
Guardian runtime:   not implemented (Guardian does not execute plans)
Dry-run orchestration preflight: implemented, preparation-only, governed by the operational addendum
Plan pack validator: implemented, read-only, scanner-only
Validator JSON:     implemented, frozen by snapshots
Validation receipts: implemented, with SHA-256 manifest hashes
Operating contract: proposed design (v0)
Operational addendum: proposed design (v0) — defines the first future operational category, not implemented
```

Guardian is **not operational** in the sense of executing plans. The executable Guardian surfaces today are all scanners or preparation-only: the plan pack validator, its generated evidence (session logs, validation receipts), and the dry-run orchestration preflight (which prepares a record but does not execute). They check the bowl and prepare the road; they do not let Guardian drive.

---

## 3. Guardian Surface Map

```txt
docs/guardian/
  README.md                                         <- you are here
  GUARDIAN_OPERATING_CONTRACT_V0.md                 <- role, authority levels, plan pack structure
  GUARDIAN_OPERATIONAL_CONTRACT_ADDENDUM_V0.md      <- first future operational category (design only, not implemented)
  GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md  <- how to read the validator
  templates/                                        <- blank plan pack templates (8 required files)
  examples/sample-dry-run-plan-pack/                <- a valid golden plan pack
```

Supporting code and fixtures:

```txt
src/codex_runner/guardian/plan_pack_validator.py                       <- validator source of truth
src/codex_runner/guardian/runner.py                                    <- guardian CLI dispatch (validate-plan-pack + orchestrate-dry-run)
src/codex_runner/guardian/session_log.py                               <- session-log writer
src/codex_runner/guardian/receipt.py                                   <- validation-receipt writer (SHA-256 manifest)
src/codex_runner/guardian/orchestration.py                             <- dry-run orchestration preflight (preparation-only)
tests/test_guardian_plan_pack_validator.py                             <- validator tests (50)
tests/test_guardian_orchestration.py                                   <- orchestration preflight tests (22)
tests/fixtures/guardian_plan_pack_validator_json_valid.json            <- frozen valid JSON snapshot
tests/fixtures/guardian_plan_pack_validator_json_invalid.json          <- frozen invalid JSON snapshot
```

---

## 4. Operating Doctrine

The governing line, restated from the operating contract:

- Codex Runner emits receipts as evidence.
- Guardian reads receipts and JSON reports as diagnostics.
- Guardian operates the CLI, not the control plane.
- Chris remains authority.

Guardian is bounded by three fixed authority levels (defined fully in `GUARDIAN_OPERATING_CONTRACT_V0.md`):

1. **Guardian Operating Authority** — run dry-run loops, read reports, surface escalation flags.
2. **Chris Operating Authority** — approve execute mode, resolve escalations, supply reviewer decisions.
3. **Chris Codexify Authority** — ingestion, WorkOrder/Execution Ledger mutation, any durable action.

Level 3 is Chris's alone. It is never delegable to Guardian.

---

## 5. Plan Pack Templates

`docs/guardian/templates/` holds the canonical v0 templates for a Guardian plan pack. A complete plan pack requires eight files:

```txt
README.md         PLAN.md          GOALS.md         BOUNDARIES.md
AUTHORIZATION.md  ESCALATION.md    SESSION_LOG.md   TASK_SPEC.yaml
```

The templates are starting points, not authority. Copy them, fill them in, and have Chris sign `AUTHORIZATION.md` before any Guardian session. The plan pack is an operating license, not self-granted permission.

---

## 6. Sample Plan Pack

`docs/guardian/examples/sample-dry-run-plan-pack/` is a valid golden plan pack. It is the validator's passing case and the reference shape for what "structurally complete enough to read" means.

It is a **sample**, not an authorization to operate Guardian or execute anything.

---

## 7. Validator CLI

The plan pack validator is the only executable Guardian surface today. It is read-only and scanner-only.

Human-readable report:

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/
```

Machine-readable JSON report:

```bash
codexrun guardian validate-plan-pack --path docs/guardian/examples/sample-dry-run-plan-pack/ --json
```

Module entrypoints (confirmed supported, useful when `codexrun` is not on PATH):

```bash
python3 -m codex_runner.runner guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/ --json
```

Exit codes:

- `0` — plan pack passes validation (structurally complete enough to read)
- `1` — plan pack fails validation

A `0` exit is **not** approval. It is **not** execution permission. It only means the bowl is complete.

---

## 8. Validator JSON Contract

The `--json` output is a single object with a fixed shape, frozen by snapshots:

```yaml
plan_pack_path:        resolved plan pack directory
valid:                 true | false
result:                pass | fail
required_files:        <8 file names> -> true | false
forbidden_path_checks: out-of-bounds repo paths declared -> true | false
boundary_checks:       9 boundary signals -> true | false
task_spec:
  yaml_parses:               true | false
  mode_is_dry_run:           true | false
  required_fields_present:   true | false
escalation:
  flag_banner_present:       true | false
issues:                list of {section, message} failures
reason:                one-line explanation
authority:             9 hardcoded-false locks (see §9)
```

The shape is pinned by:

- `tests/fixtures/guardian_plan_pack_validator_json_valid.json`
- `tests/fixtures/guardian_plan_pack_validator_json_invalid.json`

For full field meanings, read `GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md`.

---

## 9. Authority Locks

Every validator JSON report — pass or fail — emits this fixed `authority` block. The locks are hardcoded `false`; they describe what the validator itself will never do.

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

If any lock is ever not `false`, treat the output as suspect.

---

## 10. What Guardian Is Not Allowed To Do

These are fixed boundaries, not aspirations.

- Guardian is **not operational yet**.
- Guardian does **not** execute plan packs.
- Guardian does **not** invoke Pi Loop.
- Guardian does **not** touch Codexify.
- Guardian does **not** mutate durable state (WorkOrders, Execution Ledger).
- Guardian does **not** dispatch, patch, merge, auto-fill reviewer fields, or promote trust.
- The validator checks whether the plan pack is structurally readable — nothing more.
- A **valid** plan pack is not approval.
- A **passing** validator result is not execution permission.
- Chris remains human authority.

---

## 11. Recommended Reading Order

Read the surface in this order to build the full picture:

1. `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md` — role, authority levels, plan pack structure.
2. `docs/guardian/GUARDIAN_OPERATIONAL_CONTRACT_ADDENDUM_V0.md` — the first future operational category (design only; defines the scanner→operator boundary, not yet implemented).
3. `docs/guardian/templates/README.md` — what a plan pack is and when to use the templates.
4. `docs/guardian/examples/sample-dry-run-plan-pack/README.md` — the golden sample.
5. `docs/guardian/GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md` — how to read the validator.
6. `tests/fixtures/guardian_plan_pack_validator_json_valid.json` — the frozen valid shape.
7. `tests/fixtures/guardian_plan_pack_validator_json_invalid.json` — the frozen invalid shape.

For the broader diagnostic spine Guardian layers on top of, continue with the Codex Runner documents below.

---

## 12. Related Codex Runner Documents

Guardian operates on top of the Codex Runner diagnostic spine. These documents define that spine:

- `docs/specs/campaign-runner/PI_LOOP_DIAGNOSTIC_SPINE_REVIEW_PACKET.md` — the diagnostic spine inventory.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md` — how to read the Pi Loop receipt scanner.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md` — the v1 proof envelope.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md` — the compatibility posture.

These are companion documents. The Guardian contract does not supersede them.

---

## Bottom line

This index adds the map.

It does not move the territory.

Guardian has a complete bowl and a reader for it. Guardian still cannot drink without Chris's permission.
