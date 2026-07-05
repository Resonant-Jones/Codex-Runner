# Guardian Sample Plan Pack v0

This directory is a filled example Guardian plan pack for a simulated dry-run planning session in `/Volumes/Dev_SSD/Codex-Runner`.

It demonstrates what a properly prepared Guardian plan pack looks like before Guardian operates Codex Runner.

## Status

- Scenario type: simulated dry-run plan pack
- Execution status: not executed
- Purpose: show what a properly prepared Guardian plan pack looks like before operation

## What This Example Demonstrates

- How intent is captured in `PLAN.md`
- How goals are separated from non-goals in `GOALS.md`
- How hard limits are locked in `BOUNDARIES.md`
- How explicit human approval is recorded in `AUTHORIZATION.md`
- How human interrupts are shaped in `ESCALATION.md`
- How a simulated session would be logged in `SESSION_LOG.md`
- How one bounded task can be expressed in `TASK_SPEC.yaml`

## What This Example Does Not Do

- This is an example.
- This is not an active authorization.
- This does not make Guardian operational.
- This does not grant Codexify authority.
- This does not authorize Codexify ingestion.
- This does not authorize WorkOrder lifecycle mutation.
- This does not authorize provider execution, patch application, dispatch, merge, reviewer auto-fill, or trust promotion.

## Sample Scenario

This sample pack uses a harmless docs-only scenario:

Prepare a dry-run review of whether the Pi Loop receipt report operator runbook is discoverable from the README and Guardian docs.

The scenario is deliberately non-destructive and documentation-scoped. It exists to show preparation, not execution.

## Governing Line

- Guardian operates Codex Runner.
- Guardian does not become uncontrolled authority.
- Codex Runner remains CLI-first.
- Receipts are evidence, not durable truth.
- Reports are diagnostics, not permission.
- Chris remains human authority.
- Authority is not self-promotable.
- Candidate does not mean approved.
- Schema-valid does not mean correct.

## Boundary Reminder

This sample pack does not authorize touching:

- `/Volumes/Dev_SSD/Codexify-main`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`

Those paths remain out of bounds for this sample.
