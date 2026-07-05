# Codex Runner Scanner-Spine Review Checkpoint

## Status

- **Status:** review checkpoint (refreshed after Guardian session-log stub)
- **Scope:** docs-only packaging of the current Codex Runner scanner-spine work
- **Runtime impact:** none
- **Home repository:** `Resonant-Jones/Campaign-Runner` (`/Volumes/Dev_SSD/Codex-Runner`)
- **Intended reader:** reviewer receiving the two scanner spines as a packaged state

This checkpoint packages the map. It does not move the territory. It does not add claws.

---

## 1. Summary

Codex Runner now has **two scanner spines**, both read-only/diagnostic, neither granting authority:

```txt
Pi Loop diagnostic spine
  dry-run loop manager -> v0 receipt emission -> receipt report CLI
  -> JSON output -> snapshot fixtures -> review packet -> operator runbook

Guardian validation spine
  operating contract -> plan pack templates -> sample plan pack
  -> plan pack validator CLI -> JSON output -> snapshot fixtures
  -> operator runbook -> docs index -> session-log stub
```

Both spines are **scanners**. Neither spine is a **gate**. Neither spine grants durable authority. The creature has eyes, but still no claws.

The two authority lock blocks (Pi Loop receipt report; Guardian validator JSON) are hardcoded `false` and frozen by snapshot fixtures. The Guardian session-log stub reuses the validator authority locks and keeps them all `false`; its output is opt-in (`--write-session-log`) and generated under a git-ignored path.

---

## 2. Active Repo Boundary

```txt
Active (this checkpoint):
  /Volumes/Dev_SSD/Codex-Runner

Future explicit Codexify work only (not touched):
  /Volumes/Dev_SSD/Codexify-main

Archived (not touched):
  /Volumes/Dev_SSD/ResonantConstructs/Codexify-Core
```

No file outside `/Volumes/Dev_SSD/Codex-Runner` was modified by any slice summarized here.

---

## 3. Current Working Tree Status

`git status --short` shows **5 tracked files modified** and a large set of **untracked files/directories** (the two spines were added as new, untracked paths). Generated output directories (`.pi/`, `.guardian/sessions/`) are git-ignored and do not appear in `git status --short`.

### Tracked modifications (5 files)

```txt
 M .gitignore                   ignores .pi/ and .guardian/sessions/ (generated output)
 M README.md                    Pi Loop docs sections (operator surface)
 M pyproject.toml               PyYAML dependency + textual pin (infrastructure)
 M src/codex_runner/runner.py   loop + guardian subcommand dispatch
 M tests/test_runner_entry.py   guardian dispatch test
```

These tracked changes are **not unrelated** — they are the infrastructure/dispatch/docs/hygiene layer that connects the console script to the two spines. They are classified in detail in §8.

### Untracked top-level entries

```txt
?? .promptnomicon/                        repo-local scaffolding (pre-existing; authored, not generated)
?? docs/                                  both spines' docs (Pi Loop + Guardian)
?? examples/                              Pi Loop example task
?? src/codex_runner/guardian/             Guardian validator + session-log implementation
?? src/codex_runner/loop_manager/         Pi Loop manager implementation
?? src/codex_runner/prompts/loop_*.md     Pi Loop prompt packets (4)
?? src/codex_runner/schemas/*.json        Pi Loop schemas (4)
?? tests/fixtures/                        snapshot + receipt fixtures (6)
?? tests/test_guardian_plan_pack_validator.py
?? tests/test_loop_*.py                   Pi Loop tests (7)
```

`.pi/` and `.guardian/sessions/` are intentionally absent from this list: they are generated output, now git-ignored (see `docs/review/CODEX_RUNNER_GENERATED_ARTIFACT_HYGIENE.md`). Nothing is hidden. Pre-existing and incidental changes are itemized in §8 and §9.

---

## 4. Pi Loop Diagnostic Spine Artifacts

### Implementation (`src/codex_runner/loop_manager/`, 14 modules)

```txt
__init__.py        __main__.py         adr_policy.py
contracts.py       docs_policy.py      executor.py
gate_graph.py      inspector.py        planner.py
receipt_report.py  receipts.py         retry_policy.py
runner.py          validator.py
```

### Schemas (`src/codex_runner/schemas/`)

```txt
loop_receipt.schema.json       loop_receipt_v1.schema.json
gate_receipt.schema.json       loop_task.schema.json
```

### Prompt packets (`src/codex_runner/prompts/`)

```txt
loop_execution_packet.md   loop_plan_gate.md
loop_repair_packet.md      loop_validation_critic.md
```

### Example

```txt
examples/example-loop-task.yaml
```

### Tests

```txt
tests/test_loop_contracts.py       tests/test_loop_runner.py
tests/test_loop_receipt_report.py  tests/test_loop_adr_policy.py
tests/test_loop_docs_policy.py     tests/test_loop_gate_graph.py
tests/test_loop_retry_policy.py
```

### Fixtures (`tests/fixtures/`)

```txt
loop_receipt_v0.json             loop_receipt_v1.json
receipt_report_json_v0.json      receipt_report_json_v1.json
```

### Docs (`docs/specs/campaign-runner/`)

```txt
PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md
PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md
PI_LOOP_DIAGNOSTIC_SPINE_REVIEW_PACKET.md
PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md
```

### Tracked docs surface

```txt
README.md   (Pi Loop Manager v0 + Receipt Compatibility Report sections)
```

---

## 5. Guardian Validation Spine Artifacts

### Implementation (`src/codex_runner/guardian/`, 4 modules)

```txt
__init__.py              plan_pack_validator.py      runner.py
session_log.py
```

### Session-log generated output

`--write-session-log` (opt-in) writes one generated JSON session log under:

```txt
.guardian/sessions/<timestamp>-validate-plan-pack-<slug>.json
```

Default validation writes nothing. Session logs are generated evidence artifacts, not source authority; `.guardian/sessions/` is git-ignored. The `authority` block in every session log reuses `AUTHORITY_LOCKS` and keeps all nine locks `false`.

### Docs (`docs/guardian/`)

```txt
README.md                                         (docs index)
GUARDIAN_OPERATING_CONTRACT_V0.md                 (role, authority, plan pack structure)
GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md  (how to read the validator; includes --write-session-log)
templates/                                        (8 required plan pack file templates + README)
examples/sample-dry-run-plan-pack/                (valid golden plan pack, 8 files)
```

### Tests

```txt
tests/test_guardian_plan_pack_validator.py   (32 tests: validator + JSON snapshots + 9 session-log tests)
```

### Fixtures (`tests/fixtures/`)

```txt
guardian_plan_pack_validator_json_valid.json
guardian_plan_pack_validator_json_invalid.json
```

### Tracked dispatch surface

```txt
src/codex_runner/runner.py        (guardian subcommand dispatch)
tests/test_runner_entry.py        (test_main_dispatches_guardian_subcommand)
```

---

## 6. Tests and Validation Evidence

All validation run from `/Volumes/Dev_SSD/Codex-Runner`. All green.

| Command | Result |
| --- | --- |
| `pytest -q tests/test_loop_receipt_report.py` | **13 passed** |
| `pytest -q tests/test_guardian_plan_pack_validator.py` | **32 passed** |
| `pytest -q tests/test_loop_contracts.py tests/test_loop_runner.py tests/test_loop_receipt_report.py tests/test_guardian_plan_pack_validator.py` | **55 passed** |
| `python3 -m compileall src/codex_runner/loop_manager src/codex_runner/guardian src/codex_runner/runner.py tests/test_loop_receipt_report.py tests/test_guardian_plan_pack_validator.py` | **clean (exit 0)** |
| `pytest -q` (full suite) | **92 passed, 1 skipped** |

The single skip is `tests/test_tui_palette.py` — `could not import 'textual'`. It is **unrelated** to either scanner spine (it is a TUI-extra test; `textual` is an optional dependency behind the `[tui]` extra). It does not affect any scanner-spine conclusion.

---

## 7. Authority Boundaries Preserved

No scanner spine in this checkpoint authorizes any of the following. Each is either hardcoded `false` in an authority-lock block, not implemented, or explicitly out of scope:

```txt
Codexify ingestion
WorkOrder lifecycle mutation
Execution Ledger writes
DB migrations
API routes
Command Center UI
provider execution
patch application
dispatch
merge automation
automatic reviewer decisions
trust-level auto-promotion
plan execution
Pi Loop invocation from Guardian
Guardian operational autonomy
```

### Pi Loop receipt report authority block (hardcoded `false`)

```txt
durable_action_allowed: false
lifecycle_mutation_allowed: false
ingestion_allowed: false
ingestion_performed: false
```

### Guardian validator authority block (hardcoded `false`, frozen by snapshots)

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

If any lock is ever not `false`, the report is suspect and the operator must stop.

### Session-log authority ( Guardian session-log stub )

Session logs reuse the validator authority locks above. A session log records that a validation scan happened — nothing more:

```txt
Session logs do not make Guardian operational.
Session logs do not approve plans.
Session logs do not invoke Pi Loop.
Session logs do not authorize Codexify ingestion.
Session logs do not mutate durable state.
```

`--write-session-log` is opt-in. Without it, the validator remains strictly read-only and writes no files.

---

## 8. Pre-existing or Unrelated Working-Tree Changes

These are **not reverted** and **not modified** by this checkpoint. They are classified only.

### Tracked modifications supporting the spines (infrastructure + dispatch + docs)

| File | Change | Classification |
| --- | --- | --- |
| `pyproject.toml` | `dependencies = ["PyYAML>=6.0"]`; `tui = ["textual>=0.70.0,<1"]` | Infrastructure — `PyYAML` is required by `loop_manager/contracts.py`; textual pin is a packaging tightening. Supports the Pi Loop spine. |
| `src/codex_runner/runner.py` | `launch_tui` reorder + `loop` dispatch + `guardian` dispatch in `main()` | Dispatch wiring connecting the `codexrun` console script to both spines. |
| `tests/test_runner_entry.py` | `+test_main_dispatches_guardian_subcommand` | Test for the guardian dispatch. |
| `README.md` | `+## Pi Loop Manager v0`, `+### Receipt Compatibility Report`, `+## Context Management` | Operator docs surface for the Pi Loop spine. |

These four tracked changes belong with the scanner-spine work. They are called out separately only because they are the **only** changes touching already-tracked files; everything else in the spines is new (untracked).

### Incidental / scaffolding (pre-existing, not spine work)

| Path | Classification |
| --- | --- |
| `.promptnomicon/` (3 files) | Repo-local Promptnomicon Steward scaffolding. Pre-existing. Referenced by `README.md`. Not part of either spine. |

### Runtime outputs (generated, not source)

| Path | Classification |
| --- | --- |
| `.pi/runs/*` (~40 files across several run dirs) | Pi Loop dry-run outputs (`receipt.json`, `gate-receipts.json`, `validation.log`, `handoff.md`, `plan.md`, etc.). Generated by exercising the loop. Not source. Ignored via `.gitignore`; see `docs/review/CODEX_RUNNER_GENERATED_ARTIFACT_HYGIENE.md`. |
| `.guardian/sessions/*.json` | Guardian validation session logs, written only when `--write-session-log` is passed. Generated runtime/session output. Ignored via `.gitignore` (narrow rule on `.guardian/sessions/`, not all of `.guardian/`). Evidence, not source. |

### Unrelated test skip

| Path | Note |
| --- | --- |
| `tests/test_tui_palette.py` | Skipped: `textual` not installed. TUI-extra test; unrelated to either spine. |

---

## 9. Untracked Files by Slice

### Pi Loop diagnostic spine

```txt
src/codex_runner/loop_manager/                  (14 modules)
src/codex_runner/schemas/{loop_receipt,loop_receipt_v1,gate_receipt,loop_task}.schema.json
src/codex_runner/prompts/loop_{execution_packet,plan_gate,repair_packet,validation_critic}.md
examples/example-loop-task.yaml
tests/test_loop_{contracts,runner,receipt_report,adr_policy,docs_policy,gate_graph,retry_policy}.py
tests/fixtures/{loop_receipt_v0,loop_receipt_v1,receipt_report_json_v0,receipt_report_json_v1}.json
docs/specs/campaign-runner/PI_LOOP_*.md         (4 docs)
```

### Guardian doctrine / templates / examples

```txt
docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md
docs/guardian/README.md
docs/guardian/templates/                        (9 files)
docs/guardian/examples/sample-dry-run-plan-pack/ (8 files)
```

### Guardian validator implementation

```txt
src/codex_runner/guardian/                      (4 modules: __init__, plan_pack_validator, runner, session_log)
tests/test_guardian_plan_pack_validator.py
tests/fixtures/guardian_plan_pack_validator_json_{valid,invalid}.json
```

### Guardian session-log generated output (ignored)

```txt
.guardian/sessions/   (Guardian validation session logs; written by --write-session-log; generated, git-ignored)
```

### Guardian validator runbook + index (docs)

```txt
docs/guardian/GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md
docs/guardian/README.md   (also listed above as the surface index)
```

### Review checkpoint (this slice)

```txt
docs/review/CODEX_RUNNER_SCANNER_SPINE_REVIEW_CHECKPOINT.md
```

### Runtime outputs

```txt
.pi/                  (Pi Loop dry-run artifacts; generated, not source; git-ignored)
.guardian/sessions/   (Guardian session logs; generated, not source; git-ignored)
```

### Unknown / unclassified

None. Every untracked entry maps to one of the groups above.

---

## 10. Recommended Commit Grouping

A clean logical grouping for review/PR purposes. **No commits are made by this checkpoint.**

> Granularity note: several source files were built incrementally across slices (e.g. `loop_manager/receipt_report.py` carries both the report and its JSON mode; `guardian/plan_pack_validator.py` and `guardian/runner.py` each carry both the base validator and the `--json` additions; `guardian/runner.py` further carries the `--write-session-log` wiring). A strict file-level split of those would require `git add -p`. The grouping below is the recommended logical ordering; where a single file spans two commits, stage it with the commit where it was *introduced* and treat the later slice as additive docs/tests.

| # | Commit | Contents |
| --- | --- | --- |
| 1 | **Pi Loop dry-run manager and receipt spine** | `src/codex_runner/loop_manager/` (14 modules), the 4 schemas, the 4 loop prompt packets, `examples/example-loop-task.yaml`, `pyproject.toml` (PyYAML dep), `src/codex_runner/runner.py` (`loop` dispatch), the 6 non-report loop tests, `tests/fixtures/loop_receipt_{v0,v1}.json` |
| 2 | **Pi Loop receipt report JSON and snapshots** | `tests/test_loop_receipt_report.py`, `tests/fixtures/receipt_report_json_{v0,v1}.json` (report JSON mode lives in `loop_manager/receipt_report.py`, introduced in commit 1) |
| 3 | **Pi Loop diagnostic docs and runbook** | `docs/specs/campaign-runner/PI_LOOP_*.md` (4), `README.md` Pi Loop sections |
| 4 | **Guardian operating contract, templates, and sample plan pack** | `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`, `docs/guardian/templates/` (9), `docs/guardian/examples/sample-dry-run-plan-pack/` (8) |
| 5 | **Guardian plan pack validator CLI** | `src/codex_runner/guardian/` (`__init__`, `plan_pack_validator`, `runner`), `src/codex_runner/runner.py` (`guardian` dispatch), `tests/test_runner_entry.py` (guardian dispatch test) |
| 6 | **Guardian validator JSON output and snapshots** | `tests/test_guardian_plan_pack_validator.py`, `tests/fixtures/guardian_plan_pack_validator_json_{valid,invalid}.json` (JSON mode is additive within the commit-5 source files) |
| 7 | **Guardian validator runbook and docs index** | `docs/guardian/GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md`, `docs/guardian/README.md` |
| 8 | **Guardian session-log stub and generated-output hygiene** | `src/codex_runner/guardian/session_log.py`, the `--write-session-log` wiring + `DEFAULT_SESSIONS_DIR` in `guardian/runner.py`, the 9 session-log tests in `tests/test_guardian_plan_pack_validator.py`, the runbook §3.5 addition, `.gitignore` (`.pi/` + `.guardian/sessions/` rules), `docs/review/CODEX_RUNNER_GENERATED_ARTIFACT_HYGIENE.md` |
| 9 | **Scanner-spine review checkpoint** | `docs/review/CODEX_RUNNER_SCANNER_SPINE_REVIEW_CHECKPOINT.md` |

`.pi/`, `.guardian/sessions/`, and `.promptnomicon/` are intentionally **excluded** from all spine commits: `.pi/` and `.guardian/sessions/` are generated runtime/session output (now git-ignored), `.promptnomicon/` is pre-existing authored scaffolding (currently untracked; recommended for a separate source commit, or Chris confirms it stays local).

---

## 11. Deferred Work

Each item below requires an **explicit future task packet**. None is opened by this checkpoint.

```txt
Plan-pack validation receipt              (a receipt emitted by the validator itself)
Goal-to-WorkOrder compiler                (turns plan goals into bounded task specs)
Guardian-operated dry-run orchestration   (Guardian actually runs codexrun loop; first operational step, needs Chris approval)
Codexify adoption packet                  (Codexify-side, in Codexify-main)
Codexify ingestion design                 (Level-3 Chris authority)
WorkOrder lifecycle mutation              (Level-3 Chris authority)
provider execution                        (real mutating providers)
dispatch / merge automation               (Level-3 Chris authority)
```

Operational widening (plan execution, Pi Loop invocation from Guardian, Codexify touch, durable mutation) is **never** smuggled into a docs/review slice.

---

## 12. Recommended Next Slice

The Guardian session-log stub is now complete (delivered in the slice this refresh summarizes). The smallest safe next slice, still inside the scanner boundary:

```txt
Add Guardian plan-pack validation receipt
```

Scope (future task, not this refresh): a non-mutating receipt emitted by the validator itself when a plan pack passes — a stronger, referenceable evidence artifact than a session log, but still evidence, not approval. It would not execute the plan, invoke Pi Loop, touch Codexify, or mutate durable state.

The first *operational* slice — Guardian-operated dry-run orchestration (Guardian actually running `codexrun loop` from a validated plan pack) — is larger and requires explicit Chris approval and a new contract slice. It is **not** the recommended next slice here; it is the first slice that crosses from "scanner" into "agent that drives the runner."

Any operational widening requires explicit Chris approval.

---

## 13. Human Operator Decision Status

```txt
No human operator decision required.
```

This checkpoint is pure classification and packaging. No boundary was ambiguous; no authority question arose; no test failure required a judgement call. The single test skip (`test_tui_palette.py`, missing optional `textual`) is unrelated to either spine and resolves itself when the `[tui]` extra is installed.

---

## Bottom Line

Two scanner spines, packaged and legible.

```txt
Pi Loop diagnostic spine:   receipts -> report -> JSON -> snapshots -> runbook
Guardian validation spine:  contract -> validator -> JSON -> snapshots -> runbook -> index -> session logs
```

Both are read-only. Both are frozen by snapshots. Neither grants authority. Session logs are opt-in generated evidence under a git-ignored path.

The creature has eyes. It still has no claws.

This checkpoint adds the map. It does not move the territory.
