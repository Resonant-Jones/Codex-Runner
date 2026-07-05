# Guardian Boundaries

## Allowed Work

- Docs and template preparation inside `/Volumes/Dev_SSD/Codex-Runner`
- Bounded Codex Runner planning, task-shaping, and session logging work authorized by Chris
- Reading receipts, reports, logs, and task materials inside the approved repo boundary

## Disallowed Work

- Any work outside the approved plan pack boundary
- Any Codexify ingestion behavior
- Any WorkOrder or Execution Ledger mutation
- Any dispatch, merge, patch application, or trust promotion
- Any runtime or automation behavior not explicitly authorized

## Repo Paths Allowed

- `/Volumes/Dev_SSD/Codex-Runner`
- Session-specific subpaths approved by Chris:

## Repo Paths Forbidden

- `/Volumes/Dev_SSD/Codexify-main`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
- Any additional forbidden paths for this session:

## Commands Allowed

- `codexrun loop --task <task.yaml> --repo-root /Volumes/Dev_SSD/Codex-Runner --dry-run`
- `codexrun loop report --receipt <path> --json`
- `python -m codex_runner.loop_manager report --receipt <path> --json`
- Read-only file inspection commands
- Session-log creation inside the approved plan-pack area

## Commands Forbidden

- Any command targeting `/Volumes/Dev_SSD/Codexify-main`
- Any command targeting `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
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
- No plan pack may authorize Codexify ingestion unless a future explicit task approves that boundary.

## Stop Conditions

- Mandatory task or authorization file is missing
- Forbidden path is requested or detected
- Authority warnings appear in a receipt report
- A task or boundary is ambiguous enough that Guardian cannot safely continue
- A human review or approval requirement is triggered without explicit pre-authorization

## Boundary Notes

Record any session-specific boundary clarifications here. If a boundary is unclear, Guardian must stop and escalate instead of expanding scope.
