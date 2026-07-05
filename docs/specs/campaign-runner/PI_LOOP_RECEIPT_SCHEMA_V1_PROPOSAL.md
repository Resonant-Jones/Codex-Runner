# Pi Loop Receipt Schema v1 Proposal

## Status

- Status: proposed
- Scope: docs-only schema proposal
- Runtime impact: none
- Home repository: `Resonant-Jones/Campaign-Runner`

## Executive Summary

This document proposes a Pi Loop receipt schema v1 for future Codexify attempt-evidence compatibility.

It does not implement a runtime schema change.

It does not replace the current v0 receipt shape.

It defines a stronger proof envelope so a later implementation task can emit receipts with clearer identity, validation, acceptance, change, review, lineage, artifact, and policy semantics.

The governing line remains:

- v0: dry-run evidence
- v1 proposal: Codexify-compatible proof envelope
- later: reviewed implementation and only then durable ingestion

This proposal exists because the current compatibility audit found that Pi Loop v0 receipts are useful as attached evidence, but not yet sufficient as Codexify-native durable proof artifacts.

## Recognition Status

Campaign Runner may eventually recognize both v0 and proposed v1 receipt shapes in typed contract code and fixture validation.

That does not make v1 the default emitted runtime receipt.

The runtime default remains:

- emitted receipt shape: v0
- v1 status: recognized/proposed envelope only
- implementation of v1 emission: deferred

## Inputs

This proposal is shaped directly by:

- [PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md](/Volumes/Dev_SSD/Codex-Runner/docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md)
- `src/codex_runner/loop_manager/contracts.py`
- `src/codex_runner/schemas/loop_receipt.schema.json`
- `src/codex_runner/schemas/gate_receipt.schema.json`

## Non-Goals

This task does not implement:

- runtime schema changes
- CLI changes
- provider execution changes
- patch-applying mode
- Codexify durable ingestion
- WorkOrder lifecycle mutation
- reviewer decision automation
- trust-level auto-promotion
- dispatch
- merge automation

## Design Constraints

The schema must preserve these boundaries:

- Campaign Runner emits receipts.
- Campaign Runner does not become the durable authority for WorkOrders or proof acceptance.
- Codexify remains the durable authority for WorkOrders and Execution Ledger interpretation.
- Whoosh'd or any later provider stays substrate-only and does not own task semantics, review authority, or completion truth.

## Field Groups

The proposed v1 envelope is organized under these field groups:

- `identity`
- `mode_trust_actionability`
- `validation`
- `acceptance`
- `changes`
- `review`
- `lineage`
- `artifacts`
- `policy`

## Important Authority Rule

The following fields are envelope slots only:

- `review.reviewer_decision`
- `review.reviewer`
- `review.reviewed_at`
- elevated `mode_trust_actionability.trust_level` values beyond low-authority loop evidence

The loop engine must not assert these values by default.

They may only be filled by:

- an operator
- a later governed Codexify review process
- an explicitly approved ingestion or review workflow

Low-authority defaults are acceptable for dry-run evidence, for example:

```yaml
review:
  reviewer_decision: null
  reviewer: null
  reviewed_at: null
  rationale: null
mode_trust_actionability:
  trust_level: validation_captured
```

Even then, `validation_captured` means only that validation artifacts were recorded. It does not mean proof accepted, merge ready, or durable ingestion approved.

## Proposed Schema Sketch

The following sketch is illustrative and intentionally not a runtime contract yet:

```yaml
schema_version: pi_loop_receipt.v1alpha
receipt_kind: pi_loop_receipt
identity:
  receipt_id: null
  task_id: null
  work_order_id: null
  attempt_id: null
  run_id: null
  source_repo: null
  source_ref: null
mode_trust_actionability:
  receipt_mode: dry_run
  trust_level: artifact_only
  actionability: observe_only
validation:
  commands:
    - command: null
      exit_code: null
      stdout_ref: null
      stderr_ref: null
      artifact_ref: null
      declared_by: task_spec
acceptance:
  criteria:
    - id: null
      text: null
      status: unknown
      evidence_refs: []
changes:
  changed_paths:
    - path: null
      change_kind: proposed
      evidence_ref: null
review:
  operator_review_required: false
  review_reasons: []
  reviewer_decision: null
  reviewer: null
  reviewed_at: null
  rationale: null
lineage:
  source_thread_id: null
  source_message_id: null
  command_run_id: null
  guardian_run_id: null
artifacts:
  receipt_ref: null
  gate_receipts_ref: null
  handoff_ref: null
  validation_refs: []
  plan_ref: null
policy:
  documentation_impact: none
  adr_impact: none
  operator_review_stop: false
  stop_reason: null
```

## Field Group Detail

### `identity`

Purpose:

- define durable receipt identity
- bind the receipt to a task, work order, attempt, run, repo, and source ref

Proposed fields:

- `receipt_id`
- `task_id`
- `work_order_id`
- `attempt_id`
- `run_id`
- `source_repo`
- `source_ref`

Notes:

- `task_id` may remain Campaign Runner-local.
- `work_order_id` must remain nullable until a governed cross-system linkage exists.
- `attempt_id` must be distinct from ordinal loop attempt counters.

### `mode_trust_actionability`

Purpose:

- separate execution mode from trust posture
- prevent receipt consumers from mistaking "captured artifacts" for "approved proof"

Proposed fields:

- `receipt_mode`: `dry_run | patch_producing | local_execution`
- `trust_level`: `artifact_only | validation_captured | validation_passed | operator_reviewed | durable_evidence_ingested`
- `actionability`: `observe_only | review_required | ingestion_candidate`

Authority notes:

- the loop may set conservative values such as `artifact_only` or `validation_captured`
- the loop should not set `operator_reviewed` or `durable_evidence_ingested`

### `validation`

Purpose:

- carry structured validation proof instead of only summary prose

Proposed fields:

- `commands[]`
  - `command`
  - `exit_code`
  - `stdout_ref`
  - `stderr_ref`
  - `artifact_ref`
  - `declared_by: task_spec | repo_profile | loop_suggested`

Notes:

- `declared_by` preserves who authorized the command lane.
- this group should represent executed commands, not merely proposed ones.

### `acceptance`

Purpose:

- map proof to explicit acceptance criteria

Proposed fields:

- `criteria[]`
  - `id`
  - `text`
  - `status: passed | failed | blocked | unknown`
  - `evidence_refs`

Notes:

- `unknown` is important because not every criterion will be proven in every dry-run receipt.
- the engine may emit criterion evidence observations without claiming reviewed proof acceptance.

### `changes`

Purpose:

- distinguish proposed scope from actual observed changes

Proposed fields:

- `changed_paths[]`
  - `path`
  - `change_kind: proposed | generated_patch | applied_diff | observed_git_diff`
  - `evidence_ref`

Notes:

- `proposed` is valid for dry-run output.
- `observed_git_diff` is stronger and should be reserved for later implemented evidence.
- glob patterns should not be treated as equivalent to actual changed files.

### `review`

Purpose:

- define review slots without granting the loop proof authority

Proposed fields:

- `operator_review_required`
- `review_reasons`
- `reviewer_decision`
- `reviewer`
- `reviewed_at`
- `rationale`

Authority notes:

- `reviewer_decision`, `reviewer`, `reviewed_at`, and `rationale` default to `null`
- these fields are not loop claims by default

### `lineage`

Purpose:

- preserve provenance across Campaign Runner, Guardian, command-bus, and chat-linked work

Proposed fields:

- `source_thread_id`
- `source_message_id`
- `command_run_id`
- `guardian_run_id`

Notes:

- these fields stay nullable until the receipt originates from a path that can actually provide them

### `artifacts`

Purpose:

- expose explicit artifact references rather than forcing consumers to infer them from freeform lists

Proposed fields:

- `receipt_ref`
- `gate_receipts_ref`
- `handoff_ref`
- `validation_refs`
- `plan_ref`

Notes:

- a dedicated `receipt_ref` closes the audit gap around explicit receipt reference
- the v0 `evidence_refs` list may continue to exist historically, but v1 should prefer named slots

### `policy`

Purpose:

- preserve governance-relevant stop signals and policy classifications without conflating them with proof acceptance

Proposed fields:

- `documentation_impact`
- `adr_impact`
- `operator_review_stop`
- `stop_reason`

Notes:

- these are governance and routing signals
- they should not imply proof acceptance or WorkOrder mutation

## Suggested Token Meanings

### `trust_level`

- `artifact_only`: artifact exists, but validation proof may be absent or incomplete
- `validation_captured`: validation artifacts were captured
- `validation_passed`: validation command results passed as emitted by the loop
- `operator_reviewed`: a reviewer has explicitly reviewed the receipt envelope
- `durable_evidence_ingested`: a governed downstream system has ingested the receipt as durable evidence

Authority rule:

- the loop should only claim the first three, and should be conservative even there
- the loop should never auto-claim `operator_reviewed` or `durable_evidence_ingested`

### `actionability`

- `observe_only`: informative evidence only
- `review_required`: must be reviewed before any stronger use
- `ingestion_candidate`: structurally suitable for a later governed ingestion workflow

Authority rule:

- `ingestion_candidate` does not mean ingestion happened

## Mapping From Audit Gaps

| Audit gap | v1 field(s) | Required before provider execution? | Required before Codexify ingestion? | Authority / trust note |
| --- | --- | --- | --- | --- |
| durable identity | `identity.receipt_id`, `identity.work_order_id`, `identity.attempt_id`, `identity.run_id` | no | yes | no cross-system durable claims without explicit linkage |
| explicit receipt reference | `artifacts.receipt_ref` | no | yes | referenceable evidence is required before governed ingestion |
| WorkOrder linkage | `identity.work_order_id` | no | yes | must remain nullable until governed linkage exists |
| structured validation proof | `validation.commands[]` | recommended | yes | loop may emit command facts; proof interpretation stays downstream |
| per-criterion acceptance results | `acceptance.criteria[]` | recommended | yes | criterion status is not the same as reviewer proof acceptance |
| reviewer decision fields | `review.reviewer_decision`, `review.reviewer`, `review.reviewed_at`, `review.rationale` | no | yes | review slots are not loop claims by default |
| actual changed-file semantics | `changes.changed_paths[].change_kind`, `changes.changed_paths[].path`, `changes.changed_paths[].evidence_ref` | recommended | yes | `proposed` paths are weaker than `observed_git_diff` |
| run lineage | `lineage.command_run_id`, `lineage.guardian_run_id` | no | recommended | nullable until the runtime path can prove them |
| source provenance | `lineage.source_thread_id`, `lineage.source_message_id` | no | recommended | useful provenance, not proof by itself |
| governance stop signals | `policy.documentation_impact`, `policy.adr_impact`, `policy.operator_review_stop`, `policy.stop_reason` | yes | yes | these must never auto-promote trust or completion |

## Migration Posture

v0 receipts remain valid historical dry-run evidence.

They do not need to be rewritten.

Suggested migration stance:

- v0 receipts remain archival evidence artifacts
- v1 receipts are emitted only after a later implementation task changes runtime behavior
- runtime support for v1 must be explicit and versioned
- Codexify ingestion must accept only explicitly supported receipt versions
- mixed historical repositories may contain both v0 and v1 receipts without backfilling

This avoids fake continuity and keeps older artifacts honest.

## Relationship To v0

This proposal does not invalidate v0.

It clarifies what v0 already is:

- useful
- bounded
- inspectable
- non-mutating in the proven path
- not yet a governed proof envelope

The main continuity goal is:

- keep v0 evidence readable
- let v1 grow alongside it
- require explicit runtime implementation before any consumer treats v1 as emitted truth

## Implementation Recommendations

Future work, not included here:

1. Add a v1 schema file.
2. Add versioned receipt contracts.
3. Add fixture receipts for v0 and v1.
4. Add compatibility tests.
5. Add optional v1 emission behind an explicit flag or version selector.
6. Add Codexify fixture-based ingestion proof later.

## Recommended Next Implementation Task

The next implementation task, if approved later, should be:

`Add versioned Pi Loop receipt contracts and v1 fixture coverage without changing default v0 emission semantics.`

That keeps runtime change smaller than a full ingestion or provider-expansion jump and lets the new envelope be tested before any durable authority touches it.

## Bottom Line

This is schema cartography, not engine upgrade.

The proposal draws the envelope needed for future Codexify attempt-evidence compatibility while preserving the current truth line:

- the loop emits bounded evidence
- review authority stays outside the loop
- durable ingestion remains deferred until a later implemented and governed change
