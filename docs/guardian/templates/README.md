# Guardian Plan Pack Templates

This directory holds the canonical v0 templates for a Guardian plan pack in `/Volumes/Dev_SSD/Codex-Runner`.

A Guardian plan pack is the operator-readable and agent-usable bundle Guardian must read before operating Codex Runner. It gives Guardian a bounded session substrate for intent, goals, boundaries, authorization, task specs, escalation, and session logging.

The plan pack is an operating license for a Guardian session. It is not authority by itself.

## When To Use This Directory

Use these templates when Chris, Axis, and Guardian are preparing a bounded Codex Runner session and want a repo-native plan pack that matches `docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`.

Do not use these templates to imply that Guardian is already operational. The contract remains a proposed design until explicitly approved, and Guardian remains non-operational until a future task authorizes implementation.

## Core Truths

- Guardian reads the plan pack before operating Codex Runner.
- The plan pack does not grant authority by itself.
- Authorization must be explicit.
- Codex Runner remains CLI-first.
- Receipts remain evidence.
- Reports remain diagnostics.
- Chris remains human authority.
- Authority is not self-promotable.
- Candidate does not mean approved.
- Schema-valid does not mean correct.
- No plan pack may authorize Codexify ingestion unless a future explicit task approves that boundary.

## Files

- `PLAN.md` defines the session-level intent, scope, success definition, risks, and current authority level.
- `GOALS.md` organizes the session goals, priorities, conflicts, and definition of done.
- `BOUNDARIES.md` declares allowed and forbidden work, paths, commands, authority limits, and stop conditions.
- `AUTHORIZATION.md` records explicit operator authorization for mode, authority level, file classes, command classes, and approval notes.
- `ESCALATION.md` defines the human escalation banner and when to use it.
- `SESSION_LOG.md` is the template for Guardian's own audit trail during a session.
- `TASK_SPEC.yaml` is a bounded task-spec template suitable for future Pi Loop use.

## How The Files Fit Together

1. Start with `PLAN.md` to define the session.
2. Use `GOALS.md` to separate primary goals from future goals and non-goals.
3. Lock the operating envelope in `BOUNDARIES.md`.
4. Record explicit Chris approval in `AUTHORIZATION.md`.
5. Create one or more bounded task specs from `TASK_SPEC.yaml`.
6. Keep `ESCALATION.md` available for real authority or ambiguity decisions.
7. Write actual run history into a session log derived from `SESSION_LOG.md`.

## Boundary Reminder

For current Codex Runner work, Guardian may not touch:

- `/Volumes/Dev_SSD/Codexify-main`
- `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`

Those repos remain out of bounds unless a future explicit task changes that boundary.
