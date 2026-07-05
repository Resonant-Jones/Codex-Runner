# Guardian Plan

## Plan Name

- `plan_name`: Guardian Sample Plan Pack v0 - Receipt Report Discoverability Review

## Repo Target

- `repo_target`: `/Volumes/Dev_SSD/Codex-Runner`

## Operator Intent

Chris wants a harmless simulated dry-run plan pack that shows how Guardian would prepare to review whether the Pi Loop receipt report operator runbook is discoverable from the repository README and Guardian documentation without running any real loop or changing runtime behavior.

## Success Definition

Success for this example is a fully prepared, internally consistent plan pack that shows the required session inputs, preserves all authority limits, and clearly marks itself as simulated and not executed.

## Scope

- In-scope paths: `README.md`, `docs/guardian/`, `docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`
- In-scope surfaces: docs-only planning, discoverability review framing, simulated session preparation
- In-scope commands: planning references to `codexrun loop --dry-run`, `codexrun loop report --json`, and read-only inspection commands

## Non-Goals

- Explicitly out of scope: real loop execution, report generation, receipt interpretation, repo mutation outside docs/example preparation
- Deferred follow-up work: any future CLI validation helper, runtime Guardian implementation, or Codexify-side adoption work

## Assumptions

- Assumption 1: the operator runbook remains at `docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`
- Assumption 2: discoverability can be assessed by inspecting README and Guardian docs without changing execution semantics

Mark assumptions clearly. A plan pack may rely on assumptions, but assumptions are not proof.

## Known Risks

- Risk: the sample could be mistaken for active authorization
- Likely failure mode: a future reader treats this example as permission to operate
- Mitigation or stop trigger: every file labels the session as simulated, not executed, and not an active authorization

- Risk: the scenario could drift into runtime design
- Likely failure mode: example wording implies Guardian is already operational
- Mitigation or stop trigger: keep the pack docs-only and stop before adding any runtime or CLI behavior

## Current Authority Level

- Authorized mode: `simulated dry-run planning only`
- Authorized authority level: `Guardian Operating, CLI/docs-only example layer`
- Execute approval present: `no`

Authority is fixed for the session unless Chris explicitly updates authorization. Authority is not self-promotable.

## Linked Task Specs

- `docs/guardian/examples/sample-dry-run-plan-pack/TASK_SPEC.yaml`
- Additional task specs for this session: none

## Session-Specific Escalation Triggers

- Trigger: a reviewer asks to treat the example as live approval for `--execute`
- Why Guardian must stop or escalate: execute mode requires explicit Chris approval and this example grants none

- Trigger: the scenario expands into Codexify ingestion or WorkOrder mutation
- Why Guardian must stop or escalate: those actions are out of scope and outside this authority layer

## Chris Pre-Authorizations

- Pre-authorized continue conditions: prepare docs-only planning artifacts for this simulated scenario
- Pre-authorized retry conditions: not applicable because no loop run is planned
- Pre-authorized review deferrals: not applicable because no receipt review is being performed

If empty, Guardian must use the default stop and escalation rules from the operating contract.

## Axis Notes

- Architecture boundary notes: keep the sample strictly inside Codex Runner operating doctrine
- Ambiguities to watch: avoid language that conflates discoverability review with execution approval
- Failure mode to stress-test first: a schema-valid report being misread as proof of correctness or permission

## Plan Summary

Chris, Axis, and Guardian prepare one properly bounded bowl for a simulated dry-run review; Guardian does not operate beyond planning in this example.
