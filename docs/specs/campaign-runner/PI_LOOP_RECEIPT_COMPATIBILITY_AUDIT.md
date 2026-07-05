# Pi Loop Receipt Compatibility Audit

## Status

- Status: draft
- Scope: docs-only compatibility audit
- Runtime impact: none
- Issue: Codexify issue #475

## Purpose

Audit the current Campaign Runner Pi Loop v0 receipt shape against Codexify's durable attempt-evidence boundary.

This document answers one narrow question:

Can the current non-mutating Pi Loop v0 receipt be consumed as Codexify attempt evidence without accidentally granting Campaign Runner durable control-plane authority?

## Verified Sources Used

Campaign Runner truth surfaces:

- `src/codex_runner/loop_manager/contracts.py`
- `src/codex_runner/schemas/loop_receipt.schema.json`
- `src/codex_runner/schemas/gate_receipt.schema.json`
- `.pi/runs/pi-loop-5065fb426f70/receipt.json`
- `.pi/runs/pi-loop-5065fb426f70/attempt-1/gate-receipts.json`

Codexify durable truth surfaces:

- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core/guardian/agents/execution_ledger_contracts.py`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core/guardian/agents/work_orders.py`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core/docs/architecture/adr/028-execution-ledger-campaign-runner-contract.md`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core/docs/architecture/adr/036-campaign-runner-provider-adapter-contract.md`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core/docs/architecture/adr/037-campaign-runner-pi-provider-broker.md`

## Contract Assumptions

The following adoption-boundary statements were user-reported in PR `#474` and match the verified Codexify durable contracts above, but the new PR files themselves were not opened from this workspace during this audit:

- Pi Loop receipts are evidence, not durable truth.
- Campaign Runner owns bounded loop mechanics.
- Codexify owns WorkOrder and Execution Ledger authority.
- Whoosh'd remains substrate-only.

This audit therefore treats Codexify's existing accepted and proposed contracts as the canonical verification surface, and treats the user-reported PR text as consistent but not independently re-verified here.

## Classification Vocabulary

- `admissible_evidence`: may be ingested as attempt-evidence payload without granting control-plane authority by itself.
- `advisory_metadata`: useful context, but not sufficient for durable proof decisions.
- `operator_confirmation_required`: should not drive durable proof acceptance or state mutation without explicit human review.
- `missing_from_v0`: expected by Codexify's proof or work-order contracts but absent from Pi Loop v0.
- `requires_schema_revision`: present today, but shape or semantics are not yet compatible enough for direct durable ingestion.
- `out_of_scope`: not part of the Codexify attempt-evidence contract and should not be promoted into one implicitly.

## High-Level Verdict

Pi Loop v0 receipts are compatible with Codexify only as bounded evidence attachments.

They are not yet sufficient as a direct `CompletionProofGateArtifact` substitute because v0 is missing durable identifiers, acceptance-criteria proof structure, reviewer proof decisions, and stable attempt/run linkage expected by Codexify's proof contracts.

Current posture:

- safe as evidence attachment: yes
- safe as durable proof artifact: no
- safe to mutate WorkOrder lifecycle directly: no
- v1 schema revision likely needed: yes

## Mapping Baseline

Codexify's closest durable comparison point is `CompletionProofGateArtifact`, which expects:

- `work_order_id`
- `attempt_id`
- `guardian_run_id`
- `command_run_id`
- `completion_receipt_ref`
- `validation_commands_run`
- `validation_result`
- `changed_files_summary`
- `acceptance_criteria`
- `delivery_status`
- `follow_up_work_order_ids`
- `reviewer`
- `decision`
- `decision_rationale`
- `timestamp`

Pi Loop v0 instead emits:

- top-level `LoopReceipt`
- nested per-gate `GateReceipt`
- artifact path references under `.pi/runs/<run_id>/`
- summary strings and bounded status tokens

That means the right comparison is not "does Pi Loop already equal Execution Ledger?" but "which Pi Loop fields are admissible as evidence inputs into Execution Ledger review?"

## LoopReceipt Field Matrix

| Pi Loop field | Current meaning in v0 | Codexify alignment | Classification | Notes |
| --- | --- | --- | --- | --- |
| `task_id` | local Pi Loop task identity | partially overlaps with WorkOrder title/objective context, not durable work-order identity | `advisory_metadata` | useful for human correlation only; not a substitute for `work_order_id` |
| `run_id` | local loop run identifier | can map loosely to `command_run_id` or related attempt evidence handle | `requires_schema_revision` | needs explicit semantics and stable cross-system naming before direct ingestion |
| `status` | overall loop result token | loosely related to proof outcome | `operator_confirmation_required` | a passed dry-run receipt is not proof acceptance in Codexify |
| `stop_reason` | why the loop stopped | useful for triage and escalation | `advisory_metadata` | not a durable proof decision token |
| `attempts` | list of gate receipts across the loop | evidence detail for review | `admissible_evidence` | admissible as attached raw evidence, not as a direct substitute for normalized proof artifacts |
| `final_summary` | human-readable closeout summary | review context | `advisory_metadata` | summary text is not durable proof |
| `validation_summary` | human-readable validation outcome summary | related to `validation_result` | `requires_schema_revision` | needs structured tokenized result plus command list linkage |
| `changed_paths` | proposed or observed path scope summary | related to `changed_files_summary` | `requires_schema_revision` | current values may be globs or provider-declared paths rather than actual changed files |
| `evidence_refs` | file paths to receipt/handoff artifacts | related to `completion_receipt_ref` and artifact lineage | `admissible_evidence` | valid as references, but not durable storage pointers by themselves |
| `operator_review_required` | whether loop stopped for review | strong governance signal | `operator_confirmation_required` | should block automation rather than authorize mutation |
| `follow_up_recommendations` | suggested next steps | review aid | `advisory_metadata` | useful for handoff only |

## GateReceipt Field Matrix

| Pi Loop field | Current meaning in v0 | Codexify alignment | Classification | Notes |
| --- | --- | --- | --- | --- |
| `work_order_id` | optional linkage slot, currently `null` in smoke proof | direct overlap with `work_order_id` | `missing_from_v0` | field exists, but v0 does not populate it; durable ingestion should not infer it |
| `task_id` | local task identifier | human correlation only | `advisory_metadata` | not durable work-order identity |
| `run_id` | local loop run id | possible run correlation | `requires_schema_revision` | needs explicit mapping to `command_run_id`, `guardian_run_id`, or separate receipt id |
| `attempt` | local ordinal inside loop | partial overlap with attempt sequencing | `requires_schema_revision` | ordinal is not a durable `attempt_id` |
| `gate_id` | gate role token | useful to reconstruct review path | `admissible_evidence` | valid evidence metadata for review, but not a canonical Codexify proof field today |
| `status` | gate outcome token | partial overlap with gate/proof decisions | `requires_schema_revision` | current tokens are Pi Loop-local, not Codexify proof-decision canon |
| `summary` | human-readable gate result | review context | `advisory_metadata` | not durable proof |
| `evidence_refs` | artifact paths for this gate | direct evidence links | `admissible_evidence` | useful as attached proof material |
| `changed_paths` | scope/path report for this gate | related to changed-file summaries | `requires_schema_revision` | currently may be globs or proposed paths, not canonical changed-file evidence |
| `adr_impact` | architecture-governance classification | governance signal outside proof acceptance | `operator_confirmation_required` | should trigger review, not durable completion mutation |
| `documentation_impact` | doc-authority classification | governance signal outside proof acceptance | `operator_confirmation_required` | useful review stop, not proof acceptance |
| `next_gate` | planned next gate token | internal loop routing detail | `out_of_scope` | should not become durable attempt-evidence truth |
| `stop_reason` | gate-level stop reason | triage signal | `advisory_metadata` | useful for audit trail only |

## Codexify Fields Missing From Pi Loop v0

These fields appear necessary or strongly expected by Codexify's proof contracts and are absent from v0 receipts as durable, typed values:

| Codexify field | Why it matters | Classification | Audit note |
| --- | --- | --- | --- |
| `attempt_id` | durable attempt identity must be distinct from ordinal `attempt` | `missing_from_v0` | current loop only emits an integer counter |
| `completion_receipt_ref` | Codexify proof contract expects a referenceable receipt object | `missing_from_v0` | current `evidence_refs` include the receipt file path, but the top-level contract does not expose a dedicated receipt-ref field |
| `validation_commands_run` | proof review needs exact executed commands, not only a summary string | `missing_from_v0` | commands live in `validation.log`, not in typed receipt fields |
| `validation_result` token | Codexify expects a canonical proof token | `missing_from_v0` | current top-level summary is prose, not tokenized contract state |
| `acceptance_criteria` with per-criterion results | proof decisions must map to explicit criteria | `missing_from_v0` | Pi Loop task spec has criteria, but receipt does not emit criterion-by-criterion proof results |
| `reviewer` | proof acceptance must name accountable reviewer | `missing_from_v0` | v0 intentionally has no durable reviewer identity |
| `decision` | proof acceptance requires explicit review decision | `missing_from_v0` | v0 loop status is not a human proof decision |
| `decision_rationale` | durable review rationale is required | `missing_from_v0` | not represented |
| `timestamp` | proof artifact needs durable decision timestamp | `missing_from_v0` | artifact files have filesystem timestamps, but contract field is absent |
| `follow_up_work_order_ids` | downstream durable work should link explicitly | `missing_from_v0` | current recommendations are freeform text only |
| `guardian_run_id` | aligns with Guardian-mediated execution evidence | `missing_from_v0` | v0 intentionally stays Campaign Runner-local |
| `command_run_id` | distinguishes orchestrator-side attempt/run identity | `missing_from_v0` | `run_id` is close in spirit but not contractually aligned |
| `delivery_status` | completion-proof contract expects delivery posture | `missing_from_v0` | not represented |

## Fields That Are Safe To Treat As Attached Evidence Today

Without widening authority, Codexify can safely treat the following Pi Loop outputs as attached evidence only:

- full `receipt.json`
- full `gate-receipts.json`
- `validation.log`
- `plan.md`
- `executor-output.md`
- `changed-paths.json`
- `handoff.md`

This means:

- store the artifact reference
- preserve provenance
- allow operator review to inspect it
- do not let it mutate WorkOrder status or proof acceptance automatically

## Fields That Need Schema Revision Before Durable Ingestion

### 1. Run and attempt identity

Current problem:

- `run_id` exists
- `attempt` exists
- there is no durable `attempt_id`
- there is no explicit contract for mapping Pi Loop `run_id` into Guardian or command-bus attempt lineage

Needed revision:

- add `receipt_id`
- add `attempt_id`
- define whether `run_id` means loop-run, command-run, or provider-run
- add lineage fields rather than relying on positional inference

### 2. Validation proof

Current problem:

- validation outcome is summarized in prose
- executed commands are not emitted as typed top-level fields
- durable proof review needs exact commands and result tokens

Needed revision:

- add `validation_commands_run`
- add `validation_result`
- optionally add structured command result entries

### 3. Changed file semantics

Current problem:

- `changed_paths` can contain globs such as `docs/handoffs/**`
- stub/manual providers may report proposed paths rather than actual modified files

Needed revision:

- distinguish `declared_scope_paths` from `actual_changed_files`
- require normalized repo-relative file paths for actual changes
- keep proposed patterns separate from proven changed-file evidence

### 4. Acceptance-criteria proof

Current problem:

- task specs include acceptance criteria
- receipts do not emit per-criterion proof results

Needed revision:

- add criterion identifiers
- add observed evidence per criterion
- add result token per criterion

### 5. Reviewer decision boundary

Current problem:

- v0 receipt status is loop-engine output
- Codexify proof acceptance requires accountable review

Needed revision:

- keep engine status separate from proof review decision
- add optional review-envelope fields only when an operator actually confirms them

## Recommended Compatibility Posture

### Admissible now

Pi Loop v0 receipts may be attached to Codexify as:

- external evidence artifacts
- human-review inputs
- local dry-run proof attachments
- planning and validation context for future attempt records

### Not admissible now

Pi Loop v0 receipts should not directly:

- set `coding_work_orders.status`
- satisfy `CompletionProofGateArtifact`
- satisfy proof acceptance without human confirmation
- populate `latest_receipt_id` as if the receipt were a governed Codexify-native proof artifact
- authorize merge readiness
- authorize autonomous follow-up work-order creation

## Recommended v1 Receipt Additions

If Codexify wants more than attachment-only evidence, the minimum useful v1 revision is:

1. Add stable identifiers:
   - `receipt_id`
   - `attempt_id`
   - `work_order_id`
   - `campaign_id`

2. Add proof structure:
   - `validation_commands_run`
   - `validation_result`
   - `acceptance_criteria_results`
   - `actual_changed_files`

3. Add lineage:
   - `source_thread_id`
   - `source_message_id`
   - `command_run_id`
   - `guardian_run_id` when applicable

4. Add contract metadata:
   - `schema_version`
   - `receipt_kind`
   - `generated_at`

5. Preserve governance:
   - engine output remains evidence
   - reviewer decision remains separate
   - no implicit WorkOrder mutation

## Bottom Line

Pi Loop Manager v0 already emits enough structure to be useful.

It does not yet emit enough governed proof structure to be treated as Codexify-native durable attempt truth.

The compatibility answer is therefore:

- receipts are compatible as evidence attachments
- receipts are not yet compatible as proof-decision artifacts
- a v1 schema revision is warranted before durable ingestion is attempted

## Follow-Up Questions For The Next Slice

1. Should Pi Loop `run_id` map to `command_run_id`, or should those remain separate identifiers?
2. Does Codexify want a dedicated external-evidence envelope instead of overloading `CompletionProofGateArtifact`?
3. Should `GateReceipt` remain a raw nested structure, or be normalized into Codexify-native gate artifacts at ingestion time?
4. Should v1 require actual changed-file manifests before any receipt can be considered more than advisory?
5. Which fields, if any, may be auto-filled from WorkOrder context at ingestion time without creating authority drift?
