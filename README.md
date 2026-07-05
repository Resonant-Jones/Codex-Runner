
````md
# Codex Runner

Deterministic audit-to-campaign execution runner for structured repository analysis and task orchestration.

Codex Runner packages a narrow, shareable execution path extracted from a larger internal orchestration system. The focus is deterministic execution, schema-validated planning, and provider-agnostic runtime boundaries.

## Design Intent

This repository is intentionally constrained.

- Private-alpha friend-share package
- Not public open source
- Not intended for public PyPI distribution
- Deterministic runner is the primary execution surface
- Optional TUI layer exists behind the `tui` extra
- Providers such as Codex or Claude operate behind the harness boundary and are treated as interchangeable execution engines rather than architectural owners

The long-term architecture separates orchestration, identity, and execution into distinct layers. Experimental future work around provider-neutral and offline execution remains outside the default CLI path.

---

## What This Repository Is For

Use this repository when you want a standalone Codex Runner package without exposing adjacent systems, internal infrastructure, or the broader Codexify project surface.

The intended workflow is:

1. Analyze a repository or target workspace
2. Produce structured audit output
3. Compile deterministic execution plans
4. Execute tasks through schema-validated orchestration

Dry-run inspection is the default recommended starting point.

## Pi Loop Manager v0

This repository now includes a bounded Pi Loop Manager v0 for supervised plan-execute-validate receipts.

Dry-run usage:

```bash
codexrun loop \
  --task examples/example-loop-task.yaml \
  --repo-root /path/to/repo \
  --dry-run
```

Module entrypoint:

```bash
python -m codex_runner.loop_manager \
  --task examples/example-loop-task.yaml \
  --repo-root /path/to/repo \
  --dry-run
```

Run artifacts are written under:

```text
.pi/runs/<run_id>/
```

Current v0 posture:

- `--dry-run` is the truthful supported mode.
- `--execute` is wired through the same bounded provider interface, but the included providers remain non-mutating (`stub`) or handoff-oriented (`manual`).
- Codexify durable ingestion and Whoosh'd-backed inference stay deferred.

### Receipt Compatibility Report

The Pi Loop Manager also ships a read-only receipt compatibility report. It scans an existing receipt file and reports its version, schema validity, evidence posture, and Codexify ingestion readiness without mutating the file or any durable state.

Human-readable report against the v0 fixture:

```bash
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json
```

Machine-readable JSON report against the v0 fixture:

```bash
codexrun loop report --receipt tests/fixtures/loop_receipt_v0.json --json
```

The same report path is available through the module entrypoint:

```bash
python -m codex_runner.loop_manager report --receipt tests/fixtures/loop_receipt_v1.json --json
```

Report posture:

- The report is a scanner, not a gate. It never ingests, mutates, approves, dispatches, or merges.
- `lifecycle_mutation_allowed`, `ingestion_allowed`, `durable_action_allowed`, and `ingestion_performed` are always emitted as `false`.
- `codexify_ingestion_readiness` is `blocked` for v0 receipts and any v1 envelope that is missing proof fields or reviewer authority; it is `candidate` only for a complete v1 envelope pending governed operator review.

---

## Installation

### Install From Local Checkout

From the repository root:

```bash
python3 -m pip install -e .
````

Install with optional interactive TUI support:

```bash
python3 -m pip install -e .[tui]
```

---

### Install From a Local Wheel

Build the distribution:

```bash
python3 -m build
```

Install the wheel:

```bash
python3 -m pip install --force-reinstall dist/*.whl
```

The packaged wheel includes bundled prompts, templates, and JSON schemas under the `codex_runner` package path.

---

## Recommended First Run

Start in dry-run mode and inspect the generated execution plan before allowing task execution:

```bash
codexrun --dry-run \
  --repo-root /path/to/target-repo \
  --audit-prompt-file src/codex_runner/prompts/mega_audit.md \
  --audit-schema-file src/codex_runner/schemas/mega_audit_output.schema.json \
  --compiler-prompt-file src/codex_runner/prompts/audit_report_to_campaign_runner.md \
  --campaign-set-schema-file src/codex_runner/schemas/campaign_set.schema.json \
  --task-result-schema-file src/codex_runner/schemas/task_result.schema.json
```

If working from an installed wheel rather than a repository checkout, point prompt and schema arguments at the installed package files under:

```text
site-packages/codex_runner/
```

---

## Module Entrypoint

The module entrypoint remains supported after installation:

```bash
python -m codex_runner
```

This maps to the same deterministic runner entrypoint as `codexrun`.

---

## Execute Mode Expectations

Deterministic execute mode assumes a clean repository state.

Running against a dirty tree is discouraged unless intentionally testing failure or recovery behavior.

The deterministic runner rejects `--no-auto-commit` in execute mode to preserve explicit execution invariants and auditability guarantees.

---

## Status

Codex Runner is currently a private-alpha friend-share package.

Interfaces, execution semantics, packaging strategy, and licensing terms may change without notice as the system evolves.

## Context Management

This repo now includes Promptnomicon Steward scaffolding under `.promptnomicon/`:

- `.promptnomicon/promptnomicon-steward.md`
- `.promptnomicon/promptnomicon-steward-session.md`
- `.promptnomicon/project-reality-footer.md`

Start a repo-local stewardship pass with `.promptnomicon/promptnomicon-steward-session.md` when you want current-state analysis, bounded next steps, and a receipt-shaped session output.

---

Project Links
Find more about Codexify and Resonant Constructs here:

Website: https://ResonantConstructs.ai
Codexify space: https://Codexify.Space
Community: https://reddit.com/r/ResonantConstructs
Discord: https://discord.gg/C6AvyWpd
