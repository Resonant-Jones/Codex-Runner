# Guardian Operational Contract Addendum v0

## 1. Status

- **Status:** contract addendum for the implemented dry-run orchestration preflight boundary
- **Scope:** docs-only definition of the first permitted operational category and its limits
- **Runtime impact:** documentation only; the bounded orchestration preflight CLI now exists, but this document does not expand it beyond preflight
- **Home repository:** `Resonant-Jones/Campaign-Runner` (`/Volumes/Dev_SSD/Codex-Runner`)
- **Dependency:** `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`
- **Intended reader:** Chris (human operator), Axis (architecture voice), and reviewers deciding whether to approve the first operational implementation slice

> Guardian currently validates, logs, receipts, fingerprints Plan Packs, and performs bounded dry-run orchestration preflight.
>
> Guardian still does not execute runs.
>
> This addendum defines and constrains that first bounded operational category.

This addendum is the treaty. It constrains the machine that now exists. It defines the first permitted operational category. It does not grant execution.

---

## 2. Purpose

This addendum documents the transition boundary from:

```txt
scanner of artifacts
```

to:

```txt
operator of a bounded dry-run
```

It exists because the scanner boundary is now complete (validation, JSON, session logs, hash-strengthened receipts, runbooks, hygiene). The next category — Guardian *operating* a bounded run, even a dry-run — is a category change, not another scanner artifact. A category change deserves a contract before any implementation.

The addendum answers eight questions a reviewer needs answered about the first operational slice (see §5–§13). It does not implement anything by itself.

The implemented step defined here is:

```txt
Guardian-operated dry-run orchestration stub
```

That step is implemented in CLI form and remains preflight-only.

---

## 3. Current Guardian Capability

Today Guardian can:

```txt
validate a Plan Pack               (codexrun guardian validate-plan-pack)
emit JSON                          (--json)
write a session log                (--write-session-log, .guardian/sessions/)
write a validation receipt         (--write-receipt, .guardian/receipts/)
fingerprint required Plan Pack files with SHA-256
verify validation receipt continuity and current file hashes
write orchestration logs           (--write-orchestration-log, .guardian/orchestrations/)
write orchestration receipts       (--write-orchestration-receipt, .guardian/orchestration-receipts/)
```

Today Guardian cannot:

```txt
execute the plan
invoke Pi Loop
mutate source
apply patches
invoke providers
merge branches
write Codexify records
mutate durable state
approve the Plan Pack
promote trust
auto-fill reviewer decisions
```

All nine validator authority locks remain `false` in every artifact Guardian emits today. This addendum does not change that.

---

## 4. Category Boundary

This addendum uses the term **operated dry-run orchestration** for the first permitted operational category. It is deliberately narrow.

Operated dry-run orchestration means: Guardian reads a validated Plan Pack, verifies its validation evidence, constructs a bounded dry-run orchestration request, and produces an orchestration record. It stops before execution authority.

It is **not**:

- freeform agent autonomy
- unbounded repo operation
- automatic Pi Loop execution
- provider execution
- patch generation or application
- Codexify ingestion
- approval
- merge

The phrase "operational contract" does **not** mean Guardian has execution authority now. It means the first operational category now exists in bounded preflight form and remains limited by this contract.

---

## 5. First Future Operational Step (Q1: What is Guardian allowed to do first?)

The first allowed operational step is:

```txt
Guardian-operated dry-run orchestration stub
```

In that step, Guardian may:

```txt
read a validated Plan Pack
verify its validation evidence
construct a bounded dry-run orchestration request
produce an orchestration record
```

The first future implementation must remain **dry-run only**. It must not:

```txt
modify source
apply patches
invoke providers
merge branches
write Codexify records
mutate durable state
approve the Plan Pack
promote trust
auto-fill reviewer decisions
```

> Guardian may prepare the road, but it may not drive without a later explicit grant.

---

## 6. Non-Goals

This addendum does **not**:

- change any authority lock
- invoke Pi Loop
- touch Codexify
- authorize execution, dispatch, patch application, or merge
- approve any Plan Pack
- promote any trust level
- replace `GUARDIAN_OPERATING_CONTRACT_V0.md` (it layers on top of it)
- imply that any future UI bridge is already shipped

---

## 7. Proposed Future Command Shape (Q3: What command shape will exist?)

Implemented command shape:

```bash
codexrun guardian orchestrate-dry-run --plan-pack <plan-pack-dir>
```

Implemented flags:

```bash
--require-receipt <receipt-path>
--write-orchestration-log
--write-orchestration-receipt
--json
```

The command exists in `src/codex_runner/guardian/runner.py` and is covered by `tests/test_guardian_orchestration.py`. This document remains the boundary contract, not the implementation source of truth.

---

## 8. Required Preconditions (Q4: What must be validated before orchestration?)

Before the orchestration stub may proceed, **all** of the following must hold. If any fails, the stub must stop.

```txt
Plan Pack validation passes.
A Guardian validation receipt exists.
Receipt type is guardian_plan_pack_validation.
Receipt version is v0.
Receipt validation.valid is true.
Receipt authority locks are all false.
Receipt evidence.approval_granted is false.
Receipt evidence.execution_performed is false.
Receipt evidence.codexify_ingestion_performed is false.
Receipt evidence.durable_mutation_performed is false.
Receipt manifest hash_algorithm is sha256.
Required Plan Pack file hashes still match the current file contents.
Plan Pack AUTHORIZATION.md explicitly allows dry-run orchestration preparation.
Plan Pack BOUNDARIES.md does not conflict with the requested dry-run orchestration.
```

The hash re-verification step is critical: a receipt proves a past validation. Re-hashing proves the Plan Pack has not changed since. Both must pass.

> A hash match proves file continuity, not correctness.

---

## 9. Required Evidence Checks (Q4 cont.)

The stub must treat the validation receipt as **evidence to be checked**, not as authority. Concretely it must verify:

```txt
receipt schema is the known v0 validation receipt shape
receipt validation.valid is true
every authority lock in the receipt is false
every evidence "performed/granted" boolean is false
manifest hash_algorithm is sha256
each required Plan Pack file's current sha256 equals the receipt's recorded sha256
each required Plan Pack file's current size_bytes equals the receipt's recorded size_bytes
```

A receipt that claims approval or execution already occurred is a hard stop. A receipt whose hashes no longer match the files is a hard stop.

> A validation receipt is not execution authority.

---

## 10. Required Generated Records (Q5: What receipts or logs must be produced?)

The dry-run orchestration stub produces local generated records under git-ignored paths:

```txt
.guardian/orchestrations/             (orchestration attempt logs)
.guardian/orchestration-receipts/     (orchestration receipts)
```

These paths are implementation-owned generated output. This document does not change their behavior.

The orchestration record contains at least:

```yaml
orchestration_type: guardian_operated_dry_run
orchestration_version: v0
created_at:
plan_pack_path:
validation_receipt_path:
receipt_hash_verification:
preconditions:
intended_action:
authority:
evidence:
result:
notes:
```

Authority locks in the record must remain `false`. The record must explicitly state that **no execution occurred**.

> A dry-run orchestration record is not a dispatch.

---

## 11. Authority Locks (Q6: What authority locks remain false?)

The first operational stub must pin these `false` in every record it emits:

```yaml
authority:
  guardian_operational: false
  plan_execution_allowed: false
  pi_loop_invocation_allowed: false
  codexify_ingestion_allowed: false
  durable_mutation_allowed: false
  provider_execution_allowed: false
  patch_application_allowed: false
  dispatch_allowed: false
  merge_allowed: false
```

Important:

> The phrase "operational contract" does not mean Guardian is operational now. The first stub may prepare an orchestration record only. It may not promote `guardian_operational` to `true`.

`guardian_operational: true` would mean Guardian actually executed a run. The first stub is explicitly forbidden from claiming that. It prepares; it does not operate.

---

## 12. Stop Conditions (Q7: What exact conditions stop the run?)

The future stub must stop immediately if **any** of the following is true:

```txt
validation fails
validation receipt missing
receipt type/version mismatch
receipt says validation.valid false
receipt authority lock is true
receipt evidence claims approval or execution already occurred
receipt manifest hash mismatch
required Plan Pack file missing
Plan Pack boundaries conflict with requested action
Plan Pack authorization is missing or ambiguous
target repo path is outside /Volumes/Dev_SSD/Codex-Runner
any requested action touches Codexify-main
any requested action touches archived Codexify-Core
any requested action requires provider execution
any requested action requires patch application
any requested action requires merge/dispatch
any requested action requires durable state mutation
any requested action requires new trust or reviewer authority
```

For every stop condition, the future stub should produce a local failure record when it is safe to do so (i.e. writing the failure record does not itself cross a boundary). A stop is correct behavior, not a defect.

---

## 13. Human Operator Decisions (Q8: What requires Chris?)

The following decisions require Chris as Human Operator. They are never self-granted by Guardian, by a stub, or by a receipt.

```txt
approving implementation of the orchestration command
allowing Guardian to invoke Pi Loop
allowing Guardian to modify source
allowing Guardian to apply patches
allowing Guardian to call external providers
allowing Guardian to write Codexify records
allowing Guardian to mutate durable state
allowing Guardian to merge or dispatch
changing authority locks from false to true
accepting a Plan Pack as approved
promoting a validation receipt into durable truth
changing the active repo boundary
touching Codexify-main
touching archived Codexify-Core
```

When a genuine decision is required, the future implementation must surface it using the exact escalation banner in §13.1.

### 13.1 Escalation banner format

```txt
FLAG### HUMAN OPERATOR DECISION REQUIRED

Decision needed:
<one-sentence decision>

Options:
A) <option>
B) <option>
C) <option>

Recommended choice:
<recommendation>

Why this needs Chris:
<brief reason>

Evidence:
<paths, receipts, reports, or logs>
```

Guardian must never proceed past this banner until Chris resolves it.

---

## 14. Relationship to Pi Loop

> The first future operational stub must not invoke Pi Loop.
>
> A later slice may request explicit Chris approval to allow Guardian to invoke Pi Loop in dry-run mode only.
>
> Any Pi Loop invocation path must preserve existing Pi Loop authority boundaries and receipt semantics.

Pi Loop receipts remain evidence, not durable truth. If Guardian is ever allowed to invoke Pi Loop, the Pi Loop's existing authority locks (`durable_action_allowed`, `lifecycle_mutation_allowed`, `ingestion_allowed`, `ingestion_performed`) stay hardcoded `false`. Guardian invoking Pi Loop would not change Pi Loop's authority posture.

---

## 15. Relationship to Codexify

> Codexify is not touched by this addendum.
>
> Codexify ingestion is not authorized.
>
> Codexify remains a future downstream durable governance layer.
>
> Validation receipts and orchestration records may later become admissible evidence for Codexify, but only after a separate Codexify-side adoption contract.

> Codexify remains downstream durable governance, not part of this operational stub.

---

## 16. Relationship to Validation Receipts

The validation receipt (from PR #3 / #4) is the precondition evidence for the future stub. The addendum treats receipts exactly as the receipt runbook defines them:

```txt
a receipt records that a validation scan happened
a receipt is evidence, not approval
a receipt's authority locks are all false
a receipt's evidence block claims no approval/execution/ingestion/mutation
a receipt's manifest hashes prove file continuity, not correctness
```

> A valid Plan Pack is not an approved Plan Pack.

The future stub re-verifies receipt hashes against the current Plan Pack files. A receipt alone is not sufficient; a receipt plus a live hash match plus an explicit Plan Pack `AUTHORIZATION.md` is the minimum posture for the stub to even prepare an orchestration record.

---

## 17. Implementation Requirements for Later Slice

A future implementation slice of the orchestration stub must:

```txt
add no new authority beyond the local v0 orchestration record
keep all nine authority locks false
keep all four evidence "performed/granted" booleans false
write only to git-ignored generated paths (.guardian/orchestrations/, .guardian/orchestration-receipts/)
verify every precondition in §8 and §9 before preparing a record
stop on every condition in §12
produce a failure record on stop when safe
state "no execution occurred" in every successful record
not invoke Pi Loop
not touch Codexify
not modify source, apply patches, dispatch, or merge
surface Chris-only decisions via the §13.1 banner
be merged only after Chris approves the implementation slice
```

That future slice must update this addendum's Status from "design only" to "implemented" only after the stub actually exists and its authority locks remain `false` under test.

---

## 18. Forbidden Interpretations

This addendum explicitly rejects the following interpretations:

```txt
Guardian is now autonomous.
Guardian may execute plans.
Guardian may invoke Pi Loop.
Guardian may write to Codexify.
Guardian may approve Plan Packs.
Guardian may mutate durable state.
Guardian may apply patches.
Guardian may merge branches.
A receipt is approval.
A hash match is correctness.
A dry-run record is permission.
```

If any reader concludes one of these from this document, the document has been misread. This addendum grants nothing executable.

---

## 19. Review Checklist

A human reviewer can use this checklist before approving the next implementation slice.

- [ ] Does this preserve scanner evidence boundaries?
- [ ] Does this avoid Pi Loop invocation?
- [ ] Does this avoid Codexify ingestion?
- [ ] Are all authority locks `false`?
- [ ] Are stop conditions explicit?
- [ ] Are Chris-only decisions explicit?
- [ ] Is the proposed command dry-run only?
- [ ] Are generated outputs local and git-ignored?
- [ ] Is the next implementation slice still bounded?
- [ ] Does the proposed stub re-verify receipt hashes against current files?
- [ ] Does the proposed stub require explicit Plan Pack `AUTHORIZATION.md` consent?
- [ ] Does the proposed stub keep the active repo boundary at `/Volumes/Dev_SSD/Codex-Runner`?

If any box cannot be checked, the implementation slice is not ready for approval.

---

## 20. Bottom Line

This addendum is the bridge from "Guardian can read the road signs" to "Guardian may someday touch the ignition under supervision."

It defines the first operational category. It does not grant it.

```txt
Guardian may prepare the road.
Guardian may not drive without a later explicit grant.
```

The scanner phase is complete. The operational phase has a treaty. The treaty awaits Chris's signature before any machine is built to obey it.
