# Pi Loop Manager Diagnostic Spine Review Packet

## Status

- Status: review-readiness packet
- Scope: docs-only review packet
- Runtime impact: none
- Home repository: `Resonant-Jones/Campaign-Runner`
- Intended reader: reviewer receiving the current Pi Loop Manager diagnostic spine

## How To Use This Packet

This packet packages the **current** Campaign Runner-side diagnostic spine for review.

It does not add new runtime behavior.

It makes the current state legible: what exists, what is intentionally absent, what tests prove, and what boundaries remain locked.

The diagnostic spine is still a **scanner**, not a **gate**.

---

## 1. Summary

The Pi Loop Manager now has a Campaign Runner-side diagnostic spine made of these pieces:

```txt
dry-run loop manager
v0 receipt emission
version-aware receipt contracts
v0/v1 schemas
v0/v1 receipt fixtures
receipt compatibility report command
JSON report output
JSON snapshot fixtures
```

The spine does three things and only three things:

1. It runs a bounded, non-mutating dry-run loop and emits a v0 receipt.
2. It recognizes and validates v0 and v1 receipt shapes.
3. It reports a receipt's evidence posture without ingesting, mutating, approving, dispatching, or merging anything.

Everything else is deferred.

The governing authority line is unchanged:

- Campaign Runner emits receipts.
- Campaign Runner validates receipt versions.
- Campaign Runner reports evidence posture.
- Campaign Runner does not ingest receipts into Codexify.
- Campaign Runner does not mutate WorkOrders.
- Campaign Runner does not approve attempts.
- Campaign Runner does not promote trust.
- Campaign Runner does not dispatch or merge.

---

## 2. Current Repo Boundary

This packet and the work it describes live entirely in:

```txt
/Volumes/Dev_SSD/Codex-Runner
```

The following adjacent surfaces are explicitly **not** in scope for this packet and were not modified:

```txt
/Volumes/Dev_SSD/Codexify-main
  = future Codexify-side adoption or ingestion work only when explicitly approved

/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core
  = archived, not a target
```

The Pi Loop Manager diagnostic spine is Campaign Runner-local. It does not reach into Codexify durable contracts, WorkOrder state, Execution Ledger state, or any provider execution substrate.

---

## 3. Current Pi Loop Capabilities

The loop manager lives under:

```txt
src/codex_runner/loop_manager/
```

What it can do today:

- Load a bounded task spec (`loop_task.schema.json`, `LoopTask` in `contracts.py`).
- Walk a fixed gate graph of 10 gates (`gate_graph.py`): `context_curator`, `architecture_gate`, `adr_gate`, `planner`, `plan_validator`, `executor`, `inspector`, `runtime_validator`, `documentation_steward`, `receipt_writer`.
- Run declared validation commands and capture their output (`validator.py`).
- Inspect proposed changed paths against forbidden-path and documentation-authority rules (`inspector.py`, `docs_policy.py`).
- Classify ADR impact and documentation impact without auto-promoting anything (`adr_policy.py`, `docs_policy.py`).
- Apply a bounded retry policy (`retry_policy.py`).
- Emit per-gate `GateReceipt` records and a top-level v0 `LoopReceipt` (`receipts.py`, `runner.py`).
- Write run artifacts under `.pi/runs/<run_id>/` (receipt.json, gate-receipts.json, plan.md, validation.log, handoff.md, attempt artifacts).
- Recognize and validate both v0 and v1 receipt payloads (`contracts.py: validate_receipt_payload`).
- Classify a receipt's evidence posture and emit a compatibility report (`receipt_report.py`).

What it cannot do today, by design:

- It does not apply patches.
- It does not invoke a real provider that mutates the repo.
- It does not ingest receipts into Codexify.
- It does not mutate WorkOrder or Execution Ledger state.
- It does not approve, dispatch, or merge.

Provider posture:

- `--provider stub` (default): deterministic, non-mutating. Produces a proposed-path result.
- `--provider manual`: handoff-oriented. Writes a manual execution-packet request and blocks for an external operator/provider.
- `--execute` is wired through the same bounded provider interface, but the included providers remain non-mutating or handoff-oriented.

Receipt emission posture:

- The runtime default emitted receipt shape is **v0**.
- v1 is a **recognized/proposed** proof envelope that the contracts can parse and the report can classify. It is not the default emitted runtime receipt.

---

## 4. Commands

The diagnostic spine exposes the loop and the report through two entrypoints:

- `codexrun loop ...` (console script `codexrun`, dispatched in `src/codex_runner/runner.py:main` when the first token is `loop`).
- `python -m codex_runner.loop_manager ...` (module entrypoint in `src/codex_runner/loop_manager/__main__.py`).

### 4.1 Run a bounded dry-run loop

```bash
codexrun loop \
  --task examples/example-loop-task.yaml \
  --repo-root /path/to/repo \
  --dry-run
```

Behavior:

- Loads the task spec, walks the gate graph, runs validation commands, and emits a v0 receipt plus gate receipts and a handoff document under `.pi/runs/<run_id>/`.
- Exit code is `0` when the loop status is `passed`, otherwise `1`.

Required flags: `--task <path>`, `--repo-root <path>`, and exactly one of `--dry-run` / `--execute`.

Optional flags: `--provider {stub,manual}` (default `stub`), `--run-output-dir <path>`.

### 4.2 Receipt compatibility report (human-readable)

```bash
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json
```

Behavior:

- Reads the receipt file, detects its `receipt_version`, validates it, classifies its evidence posture, and prints a human-readable report.
- The receipt file is never modified.
- Exit code is `0` when the receipt is schema-valid, otherwise `1`.

### 4.3 Receipt compatibility report (JSON)

```bash
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json --json
```

Behavior:

- Same classification as the human-readable report, but emits a single JSON object to stdout.
- The receipt file is never modified.
- Exit code is `0` when the receipt is schema-valid, otherwise `1`.

### 4.4 Report via the module entrypoint (JSON, v1 fixture)

```bash
python -m codex_runner.loop_manager report --receipt tests/fixtures/loop_receipt_v1.json --json
```

Behavior:

- Identical classification and JSON output path as 4.3, reached through the module entrypoint instead of the console script.
- The same command without `--json` prints the human-readable report.

Note: no commands were invented for this packet. Every command above maps to an existing code path in `runner.py:main`, `loop_manager/runner.py:main`, and `loop_manager/receipt_report.py:main`.

---

## 5. Receipt Versions

Two receipt versions are recognized by the contracts today.

### 5.1 v0 — the emitted runtime shape

- Constant: `RECEIPT_VERSION_V0 = "v0"` in `contracts.py`.
- Class: `LoopReceipt` (with nested `GateReceipt` entries).
- Schema: `src/codex_runner/schemas/loop_receipt.schema.json` and `src/codex_runner/schemas/gate_receipt.schema.json`.
- This is the shape that `run_loop` actually emits at runtime under `.pi/runs/<run_id>/receipt.json`.
- Top-level fields: `receipt_version`, `task_id`, `run_id`, `status`, `stop_reason`, `attempts[]`, `final_summary`, `validation_summary`, `changed_paths`, `evidence_refs`, `operator_review_required`, `follow_up_recommendations`.
- `work_order_id` exists only as a nullable nested field on `GateReceipt` and is `null` in the v0 fixture. It is not durable work-order identity.

### 5.2 v1 — the recognized/proposed proof envelope

- Constants: `RECEIPT_VERSION_V1 = "v1"`, `RECEIPT_KIND_V1 = "pi_loop_receipt"` in `contracts.py`.
- Class: `V1LoopReceipt` with typed sub-envelopes: `identity`, `mode_trust_actionability`, `validation`, `acceptance`, `changes`, `review`, `lineage`, `artifacts`, `policy`.
- Schema: `src/codex_runner/schemas/loop_receipt_v1.schema.json`.
- Status: recognized and parseable, but **not** the default emitted runtime shape. A v1 fixture exists for testing classification.
- The v1 envelope is documented in `PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md`. The proposal is explicit that the loop may only claim conservative trust levels and must never auto-claim `operator_reviewed` or `durable_evidence_ingested`.

### 5.3 Version dispatch

`validate_receipt_payload` in `contracts.py` selects the parser by `receipt_version`:

- `"v0"` -> `LoopReceipt.from_dict`
- `"v1"` -> `V1LoopReceipt.from_dict`
- anything else (including missing version) -> `LoopManagerError`

The report command separately surfaces `version: unknown` when `receipt_version` is absent, and reports the receipt as schema-invalid without raising.

---

## 6. Receipt Report Modes

The report command (`receipt_report.py:main`) has two output modes.

### 6.1 Human-readable (default)

```bash
codexrun loop report --receipt <path>
```

Prints a fixed-section text report: receipt identity, evidence posture, authority posture, missing proof fields, authority warnings, operator review triggers, Codexify ingestion readiness, and a reason line.

`render_report` always emits `receipt_is_evidence_not_truth: true` and the four authority booleans, so a human reader cannot mistake the receipt for durable truth.

### 6.2 JSON (`--json`)

```bash
codexrun loop report --receipt <path> --json
```

Prints a single JSON object (via `ReceiptReport.to_dict()`). This is the machine-readable surface a future governed review workflow could consume.

Exit codes are identical in both modes: `0` when `schema_valid` is `True`, otherwise `1`.

### 6.3 What the report never does

- It never writes to the receipt file (proven by `test_report_command_does_not_mutate_receipt_file` and `test_json_report_does_not_mutate_receipt_file`).
- It never mutates WorkOrder, Execution Ledger, or any durable state.
- It never ingests. `ingestion_performed` is hardcoded `False`.
- It never authorizes durable action. `durable_action_allowed`, `lifecycle_mutation_allowed`, and `ingestion_allowed` are hardcoded `False`.

---

## 7. JSON Snapshot Contract

The JSON report shape is fixed by `ReceiptReport.to_dict()` and locked by snapshot fixtures and tests.

### 7.1 Fields emitted by the JSON report

| Field | Meaning | Constraint |
| --- | --- | --- |
| `receipt_path` | absolute path of the scanned receipt | reflects input |
| `receipt_version` | `v0`, `v1`, or `unknown` | derived from payload |
| `schema_valid` | whether the payload parsed against its declared version | drives exit code |
| `mode` | receipt mode, e.g. `dry_run` | from payload (v1) or fixed (v0) |
| `evidence_posture` | `attached_evidence`, `proof_envelope_candidate`, or `unknown` | classification |
| `trust_level` | loop evidence trust token | never auto-elevated by the report |
| `actionability` | `observe_only`, `review_required`, or `ingestion_candidate` | classification |
| `authority_warnings` | reviewer-authority gaps for elevated trust levels | v1-only |
| `missing_proof_fields` | fields required for Codexify ingestion that are absent | drives `review_required` |
| `operator_review_triggers` | human-readable reasons review is needed | drives `operator_review_required_fields` |
| `lifecycle_mutation_allowed` | may WorkOrder lifecycle be mutated from this receipt | **always `false`** |
| `ingestion_allowed` | may this receipt be ingested as durable proof | **always `false`** |
| `operator_review_required` | does this receipt require operator review | `true` for v0; v1-dependent |
| `codexify_ingestion_readiness` | `blocked` or `candidate` | `candidate` only for a complete v1 envelope |
| `reason` | one-paragraph explanation | human review aid |
| `operator_review_required_fields` | mirror of `operator_review_triggers` | legacy alias slot |
| `durable_action_allowed` | may durable action proceed from this receipt | **always `false`** |
| `ingestion_performed` | did the report ingest anything | **always `false`** |

### 7.2 Snapshot fixtures

- `tests/fixtures/receipt_report_json_v0.json` — locked output for the v0 fixture.
- `tests/fixtures/receipt_report_json_v1.json` — locked output for the v1 fixture.

Both are verified byte-for-shape by `test_v0_json_report_matches_snapshot_fixture` and `test_v1_json_report_matches_snapshot_fixture` (only `receipt_path` is normalized to a basename for portability).

### 7.3 Classification outcomes

- **v0 receipt**: `schema_valid=true`, `evidence_posture=attached_evidence`, `trust_level=validation_captured`, `actionability=review_required`, `codexify_ingestion_readiness=blocked`. Missing proof fields always include `attempt_id`, `explicit receipt_ref`, `structured validation outputs`, `per-criterion acceptance results`, `reviewer_decision`, `actual changed-file semantics`.
- **v1 receipt (complete)**: `codexify_ingestion_readiness=candidate`, with an operator-review trigger noting it remains evidence pending governed operator review.
- **v1 receipt (incomplete)**: `codexify_ingestion_readiness=blocked`, with the specific missing fields and any reviewer-authority warnings listed.
- **Missing `receipt_version`**: `version=unknown`, `schema_valid=false`, `codexify_ingestion_readiness=blocked`.
- **Malformed JSON**: `schema_valid=false`, exit code `1`, no exception propagated out of `classify_receipt`.

---

## 8. Tests and Evidence

All tests pass. Full suite: `59 passed, 1 skipped` (the skip is unrelated to the loop manager). The loop-relevant tests are listed below.

### 8.1 Loop manager receipt report — `tests/test_loop_receipt_report.py` (13 tests)

- `test_valid_v0_fixture_reports_blocked_ingestion_readiness`
- `test_valid_v1_fixture_reports_review_required_or_blocked`
- `test_malformed_receipt_reports_schema_invalid`
- `test_missing_receipt_version_reports_unknown_invalid`
- `test_elevated_trust_level_without_reviewer_evidence_is_flagged`
- `test_report_command_does_not_mutate_receipt_file`
- `test_report_command_supports_v1_fixture`
- `test_human_readable_report_still_works`
- `test_json_report_for_v0_fixture`
- `test_json_report_for_v1_fixture`
- `test_json_report_does_not_mutate_receipt_file`
- `test_v0_json_report_matches_snapshot_fixture`
- `test_v1_json_report_matches_snapshot_fixture`

These prove: v0 and v1 classification, unknown/malformed handling, reviewer-authority warning for elevated trust without reviewer evidence, no-mutation behavior, both output modes, exit codes, and the JSON snapshot contract.

### 8.2 Loop contracts — `tests/test_loop_contracts.py` (6 tests)

- task spec load + validation
- task spec rejects missing fields
- gate receipt generation
- loop receipt generation (v0)
- `test_v0_fixture_receipt_validates`
- `test_v1_fixture_receipt_validates_as_proposed_envelope`

These prove the version-aware contract layer and that both fixtures parse into the correct dataclasses.

### 8.3 Loop runner — `tests/test_loop_runner.py` (4 tests)

- `test_stub_provider_execution`
- `test_validation_command_capture_and_dry_run`
- `test_runner_stops_on_forbidden_path`
- `test_runner_dispatches_loop_subcommand`

These prove dry-run emission, validation capture, forbidden-path stopping, gate/receipt artifact creation, and that `codexrun loop ...` dispatches correctly.

### 8.4 Policy and graph tests

- `tests/test_loop_adr_policy.py` — ADR impact classification (none / proposal_required / proposal_created).
- `tests/test_loop_docs_policy.py` — documentation authority classes (free_write / proposal_only / read_only), forbidden path detection, UI operator-review detection.
- `tests/test_loop_gate_graph.py` — fixed 10-gate ordering.
- `tests/test_loop_retry_policy.py` — retry budget exhaustion and repeated-failure stop.

### 8.5 Verification commands run for this packet

```bash
pytest -q tests/test_loop_receipt_report.py
pytest -q tests/test_loop_contracts.py tests/test_loop_runner.py tests/test_loop_receipt_report.py
python3 -m compileall src/codex_runner/loop_manager tests/test_loop_receipt_report.py
pytest -q
```

All green. The three documented command surfaces were also exercised against the fixtures (human-readable v0, JSON v0, JSON v1 via the module entrypoint) and produce the expected non-mutating output.

---

## 9. Explicit Non-Goals

This packet, and the spine it packages, intentionally do **not** add or implement:

- Codexify ingestion behavior
- WorkOrder lifecycle mutation
- DB migrations
- API routes
- Command Center UI
- provider execution (real mutating providers)
- patch application
- dispatch
- merge automation
- automatic reviewer decisions
- trust-level auto-promotion
- new receipt authority semantics
- new lifecycle states
- new report classifications

The report command's authority booleans (`lifecycle_mutation_allowed`, `ingestion_allowed`, `durable_action_allowed`, `ingestion_performed`) are not just undocumented as out-of-scope — they are hardcoded `False` in `ReceiptReport.to_dict()`.

---

## 10. Boundary Locks

These locks are enforced by code and/or test, not just by convention.

1. **Receipts are evidence, not truth.** The human-readable report always prints `receipt_is_evidence_not_truth: true`.
2. **No durable action.** `durable_action_allowed` is hardcoded `False`.
3. **No ingestion.** `ingestion_performed` and `ingestion_allowed` are hardcoded `False`.
4. **No lifecycle mutation.** `lifecycle_mutation_allowed` is hardcoded `False`.
5. **No receipt file mutation.** Locked by two no-mutation tests.
6. **No v0 promotion to durable proof.** v0 is always `codexify_ingestion_readiness=blocked` with a fixed missing-proof-fields list.
7. **No reviewer authority from the loop.** v1 reviewer slots (`reviewer_decision`, `reviewer`, `reviewed_at`) default to `null`. An elevated `trust_level` without reviewer evidence is flagged as a warning and blocks ingestion readiness.
8. **No runtime v1 emission by default.** `run_loop` emits v0. v1 is recognized for parsing/reporting only.
9. **No mutating providers in the shipped set.** `stub` is non-mutating; `manual` writes a handoff packet and blocks.
10. **Repo boundary.** Only `/Volumes/Dev_SSD/Codex-Runner` is touched. `Codexify-main` and `ResonantConstructs/Codexify-Core` are not modified.

---

## 11. Known Deferred Work

These are intentionally deferred and are **not** opened by this packet. They are listed only so a reviewer can see the full posture.

- Default v1 runtime emission behind an explicit version selector (currently v1 is recognized, not emitted).
- Codexify-side ingestion of v1 envelopes, governed by Codexify authority — belongs in `Codexify-main`, not here.
- Mapping Pi Loop `run_id` to `command_run_id` / `guardian_run_id` lineage — deferred per the compatibility audit open questions.
- Real mutating provider adapter behind the bounded provider interface — deferred; current providers stay non-mutating or handoff-oriented.
- Patch-applying / dispatch / merge automation — explicitly out of scope.
- Reviewer auto-fill and trust auto-promotion — explicitly out of scope.

The open questions from `PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md` ("Follow-Up Questions For The Next Slice") remain open and are not resolved here.

---

## 12. Recommended Next Slice

Keep the spine a scanner. The smallest honest next slice is **discoverability and reviewer confidence**, not new authority:

- Surface the `report` subcommand in operator-facing docs (README already updated minimally in this packet to cover `--receipt` and `--json`).
- Add a short operator runbook entry that shows how to read a compatibility report and what `codexify_ingestion_readiness` means in plain language.
- Optional: add a single `report --version` / help-string touch if a reviewer finds discoverability weak. No runtime change.

Any slice that would widen authority — default v1 emission, ingestion, WorkOrder mutation, mutating providers, reviewer auto-fill, trust auto-promotion, dispatch, or merge — must be a separate, explicitly approved task with its own packet, and must not be smuggled into a review-readiness pass.

The line stays:

- the loop emits bounded evidence
- review authority stays outside the loop
- durable ingestion remains deferred until a later implemented and governed change

---

## Related Documents

- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md` — the audit that motivated v1.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md` — the v1 envelope proposal.
- `README.md` — operator-facing surface, now including the receipt compatibility report.
