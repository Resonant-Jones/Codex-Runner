# Guardian Escalation Guide

Use this file when Guardian reaches a real authority, ambiguity, or boundary decision that cannot be safely resolved inside the approved plan pack.

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

## When To Escalate

- A stop condition in the operating contract is hit and Chris must decide whether to continue
- A receipt report shows authority warnings or a suspect authority boolean
- `operator_review_required` is true without explicit pre-authorization
- A task spec, path boundary, or authorization note is ambiguous enough that Guardian cannot confidently proceed
- `--execute` is requested without explicit Chris approval
- A `candidate` posture needs Chris awareness or a governance decision

## When Not To Escalate

- Expected v0 blocked posture after a clean dry-run
- Routine schema-valid confirmation
- Normal repo inspection or template wording choices
- Test failures that are clearly out of scope for a docs/templates-only task

## Escalation Examples

### Example: Missing Execute Approval

Decision needed:
Whether Guardian may run a task in `--execute` mode for this session.

Why this needs Chris:
Only Chris may approve execute mode.

### Example: Boundary Ambiguity

Decision needed:
Whether a requested task path belongs inside the approved Codex Runner boundary.

Why this needs Chris:
The plan pack does not authorize Guardian to reinterpret repo boundaries on its own.

### Example: Candidate Receipt

Decision needed:
Whether to preserve a candidate receipt for future governed review without treating it as approved.

Why this needs Chris:
Candidate is an awareness signal, not permission.

## Logging Requirement

Every escalation must be recorded in the session log with the banner text, timestamp, trigger, evidence, and Chris's eventual resolution.
