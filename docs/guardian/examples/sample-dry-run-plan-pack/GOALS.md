# Guardian Goals

## Primary Goals

- Goal: show one fully prepared Guardian plan pack for a simulated dry-run docs discoverability review
- Why it matters now: Guardian needs a concrete example of what readiness looks like before any operational implementation exists
- Evidence that would show progress: all example files are filled, aligned, and consistent with the operating contract

## Secondary Goals

- Goal: show how a harmless docs-only scenario can stay bounded without implying runtime authority
- Nice-to-have value: future reviewers can copy structure without copying unsafe assumptions

## Future Goals

- Future goal: add a validation helper that checks whether plan packs are structurally complete
- Why it is deferred: example-first doctrine should land before any new CLI or runtime surface

## Out-of-Scope Goals

- Explicitly not part of this session: running Codex Runner, producing receipts, reading real reports, or changing any runtime path
- Goals requiring a future approval boundary: Codexify ingestion, WorkOrder lifecycle mutation, dispatch, patch application, merge automation, reviewer auto-fill, trust promotion

## Definition Of Done

- Required outcome: a filled sample plan pack exists under `docs/guardian/examples/sample-dry-run-plan-pack/`
- Required validation or evidence: docs/example files are readable, bounded, and marked as simulated and not executed
- Required stop condition if not met: stop if the example starts implying active authority or runtime behavior

Schema-valid output does not by itself satisfy done. Candidate posture does not mean approved.

## Goal Priority

- `P1`: preserve authority boundaries while showing a usable sample plan pack
- `P2`: make the sample scenario concrete enough to be reused as an example
- `P3`: hint at future validation work without implementing it

## Goal Conflicts

- Conflict: realism versus safety
- Which goal wins: safety and boundary clarity
- Why: the sample is meant to prepare operation, not smuggle in operation

## Goal Notes

This example should be understandable to a human operator and safe for an agent to read, but it must not expand authority or imply that simulated planning is equivalent to execution.
