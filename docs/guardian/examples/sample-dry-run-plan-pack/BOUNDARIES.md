# Guardian Boundaries

## Allowed Work

- Prepare a simulated dry-run plan pack inside `/Volumes/Dev_SSD/Codex-Runner`
- Describe a docs-only discoverability review for the operator runbook and Guardian docs
- Reference read-only inspection commands that a future real session could use
- Record simulated session expectations and stop conditions

## Disallowed Work

- Any runtime Guardian behavior
- Any actual Codex Runner loop execution for this sample
- Any Codexify ingestion behavior
- Any WorkOrder or Execution Ledger mutation
- Any provider execution, patch application, dispatch, merge, reviewer auto-fill, or trust promotion

## Allowed Repo Paths

- `/Volumes/Dev_SSD/Codex-Runner/README.md`
- `/Volumes/Dev_SSD/Codex-Runner/docs/guardian/`
- `/Volumes/Dev_SSD/Codex-Runner/docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`
- `/Volumes/Dev_SSD/Codex-Runner/docs/guardian/examples/sample-dry-run-plan-pack/`

## Forbidden Repo Paths

- `/Volumes/Dev_SSD/Codexify-main`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
- Any database, API, UI, or durable-state surface outside the approved docs-only sample scope

## Allowed Commands

- `test -f README.md`
- `test -f docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`
- `rg -n "receipt|report|guardian" README.md docs/guardian docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`
- `codexrun loop --task <task.yaml> --repo-root /Volumes/Dev_SSD/Codex-Runner --dry-run`
- `codexrun loop report --receipt <path> --json`

The Codex Runner commands above are included as planned commands for a future real session. They are not authorized for execution by this example.

## Forbidden Commands

- Any command targeting `/Volumes/Dev_SSD/Codexify-main`
- Any command targeting `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
- Any `codexrun loop --execute` command
- Any database migration command
- Any API route or UI action command
- Any command that modifies receipt files in place
- Any command that changes authority or lifecycle state by implication

## Authority Limits

- Guardian operates Codex Runner.
- Guardian does not become uncontrolled authority.
- Chris remains human authority.
- Authority is not self-promotable.
- Candidate does not mean approved.
- Schema-valid does not mean correct.
- The plan pack does not authorize Codexify ingestion.
- The plan pack does not authorize WorkOrder lifecycle mutation.

## Stop Conditions

- The sample is misread as active authorization
- A request expands this scenario beyond simulated dry-run planning
- Any path outside the approved docs-only sample scope is introduced
- A future reviewer requests provider execution, patch application, dispatch, or merge behavior inside this example
- A boundary note becomes ambiguous enough that Guardian could not safely continue without Chris

## Boundary Notes

This sample is intentionally bowl-shaped: it shows preparation structure only. It does not animate Guardian, start Codex Runner, or authorize any action beyond example planning.
