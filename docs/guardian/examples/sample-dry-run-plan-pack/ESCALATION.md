# Guardian Escalation Guide

Use this file when the simulated scenario reveals a real authority, ambiguity, or boundary decision that cannot be safely resolved inside the approved plan pack.

## Required Banner

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

## Scenario-Specific Guidance

For this sample, escalation would only be appropriate if the harmless docs-only discoverability review is asked to cross an authority or repo boundary.

## When To Escalate

- Someone asks Guardian to treat this sample as active authorization
- Someone asks Guardian to run `--execute` based on this example
- Someone asks Guardian to expand the review into `/Volumes/Dev_SSD/Codexify-main` or `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
- A reviewer tries to turn a simulated receipt expectation into proof of correctness or permission

## When Not To Escalate

- Ordinary wording refinements inside the example files
- Safe repo inspection needed to understand the sample scenario
- Expected absence of real receipts or reports, because this session is not executed
- Test failures outside the scope of this docs/example slice

## Escalation Examples

### Example: Request To Execute The Sample

Decision needed:
Whether Guardian may convert this simulated plan pack into an actual dry-run session.

Options:
A) Keep the example non-operational
B) Approve a separate real dry-run plan pack task
C) Approve execute mode immediately

Recommended choice:
A separate real dry-run plan pack task

Why this needs Chris:
This sample is not active authorization, and execute mode cannot be inferred from example preparation.

Evidence:
- `docs/guardian/examples/sample-dry-run-plan-pack/AUTHORIZATION.md`
- `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`

### Example: Cross-Repo Boundary Request

Decision needed:
Whether the discoverability review may expand into Codexify-side adoption surfaces.

Options:
A) Keep the sample inside Codex Runner only
B) Open a future explicit Codexify-side task
C) Merge the scopes now

Recommended choice:
B) Open a future explicit Codexify-side task

Why this needs Chris:
This sample pack does not authorize cross-repo work or Codexify governance action.

Evidence:
- `docs/guardian/examples/sample-dry-run-plan-pack/BOUNDARIES.md`
- `docs/guardian/examples/sample-dry-run-plan-pack/TASK_SPEC.yaml`

### Example: Candidate Misread As Approval

Decision needed:
Whether a hypothetical candidate receipt posture may be treated as approval.

Options:
A) Treat candidate as awareness only
B) Treat candidate as approved
C) Pause and wait

Recommended choice:
A) Treat candidate as awareness only

Why this needs Chris:
Candidate does not mean approved, and authority is not self-promotable.

Evidence:
- `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`
- `docs/guardian/examples/sample-dry-run-plan-pack/README.md`

## Logging Requirement

Any real escalation arising from future use of this example must be recorded in the session log with the banner text, timestamp, trigger, evidence, and Chris's resolution.
