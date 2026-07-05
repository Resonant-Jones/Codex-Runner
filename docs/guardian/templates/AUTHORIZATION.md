# Guardian Authorization

## Authorized Mode

- `authorized_mode`: `dry_run`
- `execute_authorized`: `no`

Only Chris may approve a transition from `dry_run` to `execute` for a specific run or task.

## Authorized Authority Level

- `authority_level`:
- `effective_from`:
- `effective_until`:

Authority is fixed, explicit, and not self-promotable.

## Allowed Command Classes

- Codex Runner dry-run commands
- Receipt report commands
- Read-only inspection commands
- Session-log writing inside the approved plan-pack area

## Allowed File Classes

- Plan-pack files
- Approved task specs
- `.pi/runs/` artifacts for the active repo
- Guardian session-log files

## Forbidden Authority Changes

- Self-promotion from Level 1 to any higher authority
- Implied authorization from successful validation or exit code `0`
- Treating `candidate` as approval or ingestion
- Treating reports as permission
- Treating receipts as durable truth

## Expiration Or Session Boundary

- `session_boundary`:
- `approval_expires_at`:
- `revalidation_required_if`:

## Human Approval Notes

- Chris approval note:
- Scope approved:
- Mode approved:
- Known exceptions:

## Signature Block

- `approved_by`: Chris
- `approved_at`:
- `approval_reference`:

If this file is unsigned or incomplete, Guardian must not assume authority.
