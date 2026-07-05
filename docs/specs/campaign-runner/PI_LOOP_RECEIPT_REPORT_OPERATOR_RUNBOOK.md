# Pi Loop Receipt Report Operator Runbook

## Status

- Status: operator runbook
- Scope: docs-only interpretation guide
- Runtime impact: none
- Home repository: `Resonant-Jones/Campaign-Runner`
- Intended reader: operator who runs or reads a Pi Loop receipt compatibility report

This runbook teaches you how to read the scanner.

It does **not** turn the scanner into a gate.

---

## 1. Purpose

The Pi Loop receipt compatibility report is a read-only diagnostic. You point it at a receipt file and it tells you:

- what receipt version it found
- whether the receipt's shape is valid for that version
- how the receipt may be treated as evidence
- whether it is blocked or a candidate for future Codexify-side consideration
- what proof fields or reviewer authority it is missing

The report never ingests, approves, dispatches, merges, or mutates anything. It only describes.

This runbook exists so operators do not misread a diagnostic as an authorization.

---

## 2. When to use the report

Use the report when you want to understand a receipt's posture without acting on it, for example:

- after running a bounded dry-run loop and inspecting the emitted receipt
- when handed a receipt from another operator or run
- before triaging whether a receipt is even structurally ready for deeper review
- when explaining to a reviewer why a receipt is not yet durable proof

Do not use the report to:

- decide that work is correct
- approve an attempt
- complete a WorkOrder
- trigger ingestion, dispatch, patch application, or merge

If you find yourself wanting the report to *do* something, stop. It is not built for that. The next slice for any durable action is a separate, explicitly approved task.

---

## 3. Commands

The report is available through two entrypoints, with two output modes.

### 3.1 Human-readable report (default)

```bash
codexrun loop report --receipt <path/to/receipt.json>
```

Prints a fixed-section text report to stdout.

### 3.2 JSON report

```bash
codexrun loop report --receipt <path/to/receipt.json> --json
```

Prints a single JSON object to stdout. Same classification as the human-readable form.

### 3.3 Module entrypoint

```bash
python -m codex_runner.loop_manager report --receipt <path/to/receipt.json> --json
```

Identical classification and output. Use the module entrypoint when the `codexrun` console script is not on PATH. Drop `--json` for the human-readable form.

### 3.4 Against the shipped fixtures

```bash
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json --json
python -m codex_runner.loop_manager report --receipt tests/fixtures/loop_receipt_v1.json --json
```

### 3.5 Exit codes

Both modes share the same exit-code rule:

- exit `0` when the receipt is schema-valid for its declared version
- exit `1` when the receipt is malformed, missing its version, or fails version-specific validation

A `0` exit means the shape parsed. It does **not** mean the work is correct or approved.

---

## 4. How to read human-readable output

The text report is organized into fixed sections. Read it top to bottom.

```text
Pi Loop Receipt Compatibility Report
Receipt:
  path:        where the receipt file lives on disk
  version:     v0, v1, or unknown
  schema_valid: did the shape parse against its declared version
Evidence posture:
  mode:               receipt mode (e.g. dry_run)
  evidence_posture:   how the receipt may be treated as evidence
  trust_level:        loop evidence trust token
  actionability:      what a consumer may do with it
Authority posture:
  receipt_is_evidence_not_truth: true   <-- always true; the anchor line
  lifecycle_mutation_allowed:    always false
  ingestion_allowed:             always false
  operator_review_required:      does this receipt require human review
Missing proof fields:
  - fields required for stronger evidence posture that are absent
Authority warnings:
  - reviewer-authority gaps for elevated trust levels
Operator review triggers:
  - human-readable reasons review is needed
Codexify ingestion readiness:
  blocked | candidate
Reason:
  one-paragraph explanation
```

The most important line is `receipt_is_evidence_not_truth: true`. It is always printed. If you remember nothing else from this section, remember that line.

---

## 5. How to read JSON output

The JSON report (`--json`) emits one object. The field set is fixed and is documented in section 6.

When reading JSON programmatically:

- Treat `receipt_version` first. If it is `unknown`, the rest is triage-only.
- Treat `schema_valid` next. If `false`, do not interpret posture fields as authoritative.
- Treat `codexify_ingestion_readiness` as **diagnostic**, never as an instruction.
- Always check the four authority booleans. They must be `false`. If any are ever not `false`, stop and treat the report as suspect.

The JSON object is the same classification as the human-readable form, just shaped for a machine reader. It is not permission to mutate Codexify.

---

## 6. Field meanings

Plain-language meanings for the fields emitted by the report.

### `receipt_path`

The absolute path of the receipt file you scanned. Reflects your input. The report never writes to this file.

### `receipt_version`

The version declared on the receipt. One of:

- `v0` — the default emitted runtime shape (bounded dry-run evidence).
- `v1` — a recognized/proposed proof envelope. Recognized for parsing and reporting; not the default emitted runtime shape.
- `unknown` — the receipt has no usable `receipt_version`.

### `schema_valid`

Whether the receipt's shape parsed against the rules for its declared version.

- `schema_valid` means the receipt **shape** is valid for its version.
- `schema_valid` does **not** mean the work is correct.
- `schema_valid` does **not** mean the attempt is approved.

### `evidence_posture`

How the receipt may be treated as evidence. Values:

- `attached_evidence` — admissible as an attached evidence artifact, not as durable proof.
- `proof_envelope_candidate` — structurally a candidate proof envelope, pending review and missing-field resolution.
- `unknown` — the receipt could not be classified.

- `evidence_posture` describes how the receipt may be treated as evidence.
- `evidence_posture` does **not** approve the attempt.

### `trust_level`

A loop evidence trust token. Conservative values: `artifact_only`, `validation_captured`, `validation_passed`. Elevated values: `operator_reviewed`, `durable_evidence_ingested`.

The report never auto-promotes trust level. Elevated values are only ever read from the receipt, never asserted by the report.

### `actionability`

What a consumer may do with the receipt. Values:

- `observe_only` — informative evidence only.
- `review_required` — must be reviewed before any stronger use.
- `ingestion_candidate` — structurally suitable for a later governed ingestion workflow. This is **not** the same as ingested.

### `codexify_ingestion_readiness`

Diagnostic readiness only. Values: `blocked` or `candidate`. See section 7.

- `codexify_ingestion_readiness` describes diagnostic readiness only.
- `candidate` does **not** mean ingested.
- `blocked` does **not** mean failed work.

### `missing_proof_fields`

The proof fields the receipt lacks that would be needed for a stronger evidence posture. For v0 this is a fixed list. For v1 it is computed from the envelope contents.

- `missing_proof_fields` means the receipt lacks proof fields needed for stronger evidence posture.

### `operator_review_required_fields`

The human-readable reasons a governed review process would need to act, mirrored as a field list.

- `operator_review_required_fields` means a human or governed review process would need to fill those fields later.

(Note: in the JSON output this field mirrors `operator_review_triggers`. Treat both as "reasons review is required," not as authoritative requirements the report enforces.)

### `authority_warnings`

Warnings about reviewer-authority gaps, e.g. an elevated `trust_level` without matching `reviewer`, `reviewed_at`, and `reviewer_decision`.

- `authority_warnings` are warnings, not automatic enforcement actions. Read and resolve them before any higher-level use.

### `durable_action_allowed`

Whether durable action may proceed from this receipt.

- `durable_action_allowed` must remain `false`. It is hardcoded `false`.

### `lifecycle_mutation_allowed`

Whether a WorkOrder or other durable lifecycle may be mutated from this receipt.

- `lifecycle_mutation_allowed` must remain `false`. It is hardcoded `false`.

### `ingestion_performed`

Whether the report ingested anything into Codexify.

- `ingestion_performed` must remain `false`. It is hardcoded `false`. The report never ingests.

---

## 7. Readiness meanings

`codexify_ingestion_readiness` has two values. Use conservative language when interpreting them.

### `blocked`

The receipt/report is not ready to be treated as a Codexify ingestion candidate.

This may be because it is v0, incomplete, advisory, or missing stronger proof fields.

`blocked` does not mean the work failed. It means the receipt is not, on its own, ready for durable ingestion. The underlying loop may have run perfectly. The receipt is simply not a governed proof artifact.

All v0 receipts are `blocked`. A v1 receipt is `blocked` when any required proof field or reviewer-authority slot is missing or incomplete.

### `candidate`

The receipt/report may be structurally ready for future Codexify-side consideration.

It has **not** been ingested.
It has **not** been approved.
It has **not** been merged.
It has **not** been used to mutate durable state.

`candidate` is a "preserve this for later governed review" signal, nothing more. Any actual ingestion belongs in a separate, explicitly approved Codexify-side task.

---

## 8. Authority locks

These are not policies. They are constraints enforced in code and verified by tests.

- `receipt_is_evidence_not_truth` is always `true` in human-readable output.
- `durable_action_allowed` is always `false`.
- `lifecycle_mutation_allowed` is always `false`.
- `ingestion_allowed` is always `false`.
- `ingestion_performed` is always `false`.
- The report never writes to the receipt file (locked by no-mutation tests).
- The report never elevates trust level on its own.
- The report never fills reviewer fields.
- The report never mutates WorkOrder, Execution Ledger, or any durable state.

If you ever see one of the four authority booleans report anything other than `false`, treat the output as suspect and do not act on it.

---

## 9. Common mistakes

These are the misreadings this runbook exists to prevent.

- Do not treat `schema_valid: true` as approval. It only means the shape parsed.
- Do not treat `candidate` as ingested. It is a "preserve for later" signal.
- Do not treat `proof_envelope_candidate` as accepted proof. It is a structural candidate, not a proof decision.
- Do not treat JSON output as permission to mutate Codexify. The JSON is a machine-readable description, not an instruction.
- Do not auto-fill reviewer fields (`reviewer`, `reviewed_at`, `reviewer_decision`). Those slots are filled by a human or a governed review process, never by the report.
- Do not promote trust levels automatically. The report reads trust level; it never raises it.
- Do not complete WorkOrders from this report. The report has no WorkOrder authority.
- Do not dispatch, patch, or merge based on this report. The report has no execution authority.
- Do not confuse `blocked` with "the work is wrong." `blocked` is about receipt readiness, not work correctness.
- Do not treat a `0` exit code as a green light for durable action. It only means the receipt was schema-valid.

---

## 10. What to do next

Safe next actions, by report outcome.

### If the report is v0 and `blocked`

Keep the receipt as attached evidence, or rerun the loop when a stronger receipt format exists. v0 is intentionally `blocked` for ingestion readiness; this is expected, not a defect.

### If the report is v1 and `blocked`

Inspect `missing_proof_fields` and `operator_review_required_fields`. Decide whether the gaps can be closed by a governed review process. If reviewer authority is the gap, that gap is filled by a human or an explicitly approved review workflow, not by the report.

### If the report is v1 and `candidate`

Preserve it as a candidate artifact for later governed Codexify-side adoption. Do **not** ingest automatically. "Candidate" means "worth keeping for a future, separately-approved review," not "ready to ingest now."

### If `authority_warnings` are present

Read and resolve them before using the report in any higher-level workflow. A typical warning is an elevated `trust_level` without matching reviewer evidence. Resolve means: have a human or governed process supply the missing reviewer fields, or downgrade the claim. Never silence a warning by editing the report output.

### If the receipt is malformed or `unknown`

Do not interpret posture fields as authoritative. Fix the receipt source (the loop that produced it) and rescan. A malformed receipt is a triage signal, not evidence of anything about the work.

---

## 11. What not to do

A short, explicit list. If you are about to do any of these, stop.

- Do not ingest the receipt into Codexify based on this report.
- Do not mutate WorkOrder lifecycle based on this report.
- Do not run DB migrations, API routes, or UI actions based on this report.
- Do not execute providers, apply patches, dispatch, or merge based on this report.
- Do not auto-fill reviewer decisions.
- Do not auto-promote trust levels.
- Do not introduce new receipt authority semantics, lifecycle states, or report classifications. Those require a separate, explicitly approved task.
- Do not modify `/Volumes/Dev_SSD/Codexify-main` or `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core` to "make the report do more." Those surfaces are out of bounds for this runbook and for the report itself.

---

## Related Documents

- `docs/specs/campaign-runner/PI_LOOP_DIAGNOSTIC_SPINE_REVIEW_PACKET.md` — the review packet for the whole diagnostic spine.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md` — the audit that motivated the v1 envelope.
- `docs/specs/campaign-runner/PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md` — the v1 envelope proposal.
- `README.md` — operator-facing surface, including the receipt compatibility report commands.
