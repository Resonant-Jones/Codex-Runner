# Codex Runner

Deterministic, receipt-driven orchestration for repository auditing, bounded task execution, Pi Loop diagnostics, and Guardian-governed preflight workflows.

Codex Runner packages a narrow, shareable execution path extracted from a larger internal orchestration system. It keeps planning, execution, evidence, and authority boundaries explicit so that providers such as Codex and Claude remain interchangeable execution engines rather than architectural owners.

> **Status:** Private alpha  
> **Distribution:** Trusted friend-share evaluation package  
> **Python:** 3.11+  
> **Default posture:** Inspect first. Execute deliberately. Preserve receipts.

---

## What Codex Runner Is

Codex Runner currently exposes three related but distinct surfaces:

| Surface | Purpose | Current authority |
|---|---|---|
| **Deterministic Runner** | Audit a repository, compile campaigns, select bounded tasks, execute through schema-validated provider interfaces, and write task/run receipts | Dry-run and governed execute mode |
| **Pi Loop Manager v0** | Produce supervised plan-execute-validate run artifacts and scan existing receipts for compatibility and ingestion readiness | Dry-run is the truthful supported mode; included providers remain non-mutating or handoff-oriented |
| **Guardian** | Validate Plan Packs, write evidence receipts, and prepare bounded dry-run orchestration records | Scanner and preflight only; no execution authority |

These surfaces share one doctrine:

- structured inputs before execution
- schema-validated outputs
- explicit provider boundaries
- inspectable artifacts and receipts
- no implied authority from successful validation
- durable or higher-risk actions remain human-governed

---

## Current Truth

### Implemented

- Deterministic repository audit and campaign compilation
- Campaign selection, task materialization, scoped execution, and run receipts
- Codex and Claude provider adapters behind the runner boundary
- Pi Loop Manager v0 dry-run workflow
- Pi Loop receipt compatibility reporting for v0 and v1 receipt envelopes
- Guardian Plan Pack validation
- Guardian validation session logs and SHA-256-backed validation receipts
- Guardian dry-run orchestration preflight
- Guardian orchestration logs and receipts
- Promptnomicon Steward scaffolding for repository-local context management
- Optional Textual TUI behind the `tui` extra

### Supported but bounded

- Deterministic execute mode requires a clean repository state
- Execute mode preserves auto-commit and auditability invariants
- Pi Loop `--execute` is wired through the bounded provider interface, but the included providers are currently non-mutating (`stub`) or handoff-oriented (`manual`)
- Guardian commands may inspect, validate, fingerprint, and prepare evidence
- A passing validator result means the input is structurally readable, not approved

### Proposed, not shipped

- A Codexify Guardian UI and backend bridge for invoking the existing preflight-only Guardian command surface
- Codexify durable ingestion of Pi Loop or Guardian evidence
- Whoosh'd-backed inference
- Provider-neutral offline execution outside the current default CLI path

### Explicitly prohibited from Guardian

Guardian does not:

- invoke Pi Loop
- execute Plan Packs
- mutate source
- touch Codexify durable state
- perform provider execution
- apply patches
- dispatch work
- merge changes
- auto-fill reviewer decisions
- promote trust or authority

The preflight boundary is fixed:

```text
PREFLIGHT ONLY
NO PI LOOP INVOCATION
NO SOURCE MUTATION
NO CODEXIFY INGESTION
```

---

## Architecture

```text
                                  HUMAN AUTHORITY
                                         |
                                         v
+------------------+          +-------------------------+
| Repository or    |          | Guardian Plan Pack      |
| target workspace |          | + explicit authorization|
+--------+---------+          +------------+------------+
         |                                 |
         v                                 v
+------------------+          +-------------------------+
| Structured audit |          | Guardian validator      |
+--------+---------+          | scanner-only            |
         |                    +------------+------------+
         v                                 |
+------------------+                       v
| Campaign compiler|          +-------------------------+
+--------+---------+          | Validation report, log, |
         |                    | and SHA-256 receipt      |
         v                    +------------+------------+
+------------------+                       |
| Deterministic    |                       v
| campaign state   |          +-------------------------+
+--------+---------+          | Dry-run orchestration   |
         |                    | preflight                |
         v                    +------------+------------+
+------------------+                       |
| Task selection   |                       v
| and materialize  |          +-------------------------+
+--------+---------+          | Orchestration log and   |
         |                    | orchestration receipt   |
         v                    +-------------------------+
+------------------+
| Dry-run or       |
| governed execute |
+--------+---------+
         |
         v
+------------------+          +-------------------------+
| Implementation,  |          | Existing Pi Loop       |
| task, state, and |          | receipt                 |
| run receipts     |          +------------+------------+
+------------------+                       |
                                           v
                              +-------------------------+
                              | Compatibility scanner   |
                              | read-only               |
                              +------------+------------+
                                           |
                                           v
                              +-------------------------+
                              | Version, schema, proof, |
                              | and ingestion-readiness |
                              | report                  |
                              +-------------------------+
```

### Boundary summary

```text
Providers execute behind the harness.
Receipts provide evidence, not authority.
Guardian prepares and reports, but does not execute.
Codexify durable mutation remains outside this repository's default path.
Human approval remains the final authority boundary.
```

---

## Quick Start

### 1. Install from a local checkout

From the repository root:

```bash
python3 -m pip install -e .
```

Install with optional TUI support:

```bash
python3 -m pip install -e '.[tui]'
```

Install development dependencies:

```bash
python3 -m pip install -e '.[dev]'
```

---

### 2. Run the deterministic audit-to-campaign pipeline

Begin with dry-run inspection:

```bash
codexrun --dry-run \
  --repo-root /path/to/target-repo \
  --audit-prompt-file src/codex_runner/prompts/mega_audit.md \
  --audit-schema-file src/codex_runner/schemas/mega_audit_output.schema.json \
  --compiler-prompt-file src/codex_runner/prompts/audit_report_to_campaign_runner.md \
  --campaign-set-schema-file src/codex_runner/schemas/campaign_set.schema.json \
  --task-result-schema-file src/codex_runner/schemas/task_result.schema.json
```

The module entrypoint maps to the same deterministic runner:

```bash
python -m codex_runner
```

#### Execute mode expectations

Deterministic execute mode assumes a clean repository state.

Running against a dirty tree is discouraged unless intentionally testing failure or recovery behavior. The runner rejects `--no-auto-commit` in execute mode to preserve explicit execution invariants and auditability guarantees.

---

### 3. Run Pi Loop Manager v0

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

Pi Loop run artifacts are written under:

```text
.pi/runs/<run_id>/
```

Current v0 posture:

- `--dry-run` is the truthful supported mode
- `--execute` uses the same bounded provider interface
- included providers remain non-mutating (`stub`) or handoff-oriented (`manual`)
- durable Codexify ingestion remains deferred

---

### 4. Scan a Pi Loop receipt

Human-readable compatibility report:

```bash
codexrun loop report \
  --receipt tests/fixtures/loop_receipt_v0.json
```

Machine-readable JSON report:

```bash
codexrun loop report \
  --receipt tests/fixtures/loop_receipt_v0.json \
  --json
```

Module entrypoint:

```bash
python -m codex_runner.loop_manager report \
  --receipt tests/fixtures/loop_receipt_v1.json \
  --json
```

The report is a scanner, not a gate. It never ingests, mutates, approves, dispatches, or merges.

The report always emits the following as `false`:

- `lifecycle_mutation_allowed`
- `ingestion_allowed`
- `durable_action_allowed`
- `ingestion_performed`

`codexify_ingestion_readiness` is:

- `blocked` for v0 receipts
- `blocked` for incomplete v1 envelopes
- `candidate` only for a complete v1 proof envelope pending governed operator review

---

### 5. Validate a Guardian Plan Pack

Validate the included golden sample:

```bash
codexrun guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/
```

Return machine-readable JSON:

```bash
codexrun guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/ \
  --json
```

Write a validation receipt:

```bash
codexrun guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/ \
  --write-receipt
```

Module entrypoint:

```bash
python3 -m codex_runner.runner guardian validate-plan-pack \
  --path docs/guardian/examples/sample-dry-run-plan-pack/ \
  --json
```

Exit codes:

- `0`: the Plan Pack passes structural validation
- `1`: the Plan Pack fails structural validation

A `0` exit is not approval and does not grant execution permission.

---

### 6. Run Guardian dry-run orchestration preflight

```bash
codexrun guardian orchestrate-dry-run \
  --plan-pack docs/guardian/examples/sample-dry-run-plan-pack/
```

Write local orchestration evidence:

```bash
codexrun guardian orchestrate-dry-run \
  --plan-pack docs/guardian/examples/sample-dry-run-plan-pack/ \
  --write-orchestration-log \
  --write-orchestration-receipt
```

This command prepares evidence only. It does not invoke Pi Loop, execute a provider, mutate source, or touch Codexify.

---

## Generated Artifacts

| Surface | Default artifact locations |
|---|---|
| Deterministic Runner | `docs/_audits/`, `docs/Campaign/`, `docs/tasks/`, `docs/_campaign_runs/` |
| Pi Loop Manager | `.pi/runs/<run_id>/` |
| Guardian validator | `.guardian/sessions/`, `.guardian/receipts/` |
| Guardian orchestration preflight | `.guardian/orchestrations/`, `.guardian/orchestration-receipts/` |

Generated artifacts are evidence and diagnostics. They do not independently grant approval, execution authority, ingestion permission, or trust promotion.

---

## Provider Boundary

Codex Runner currently supports Codex and Claude provider adapters for the deterministic runner.

Providers receive:

- rendered stage or task prompts
- explicit repository and campaign context
- schema requirements
- allowed file scope
- listed validation commands
- bounded execution constraints

Providers do not own:

- campaign state
- authority policy
- receipt semantics
- repository identity
- durable Codexify state
- approval decisions

The harness owns the orchestration contract. Providers remain replaceable.

---

## Guardian Authority Model

Guardian is layered on top of the Codex Runner diagnostic spine.

The current authority model separates three levels:

1. **Guardian operating authority**  
   Read Plan Packs, run scanners, prepare dry-run orchestration records, and surface escalation flags.

2. **Human operating authority**  
   Approve execution, resolve escalations, and supply reviewer decisions.

3. **Human Codexify authority**  
   Approve ingestion, WorkOrder or Execution Ledger mutation, and all durable actions.

The third level is never delegated to Guardian.

For the full contract, begin with [`docs/guardian/README.md`](docs/guardian/README.md).

---

## Documentation Map

### Core repository documents

- [`SAFETY.md`](SAFETY.md): safety posture and execution boundaries
- [`CHANGELOG.md`](CHANGELOG.md): package history
- [`EVALUATION-LICENSE.md`](EVALUATION-LICENSE.md): private-alpha evaluation terms

### Pi Loop and diagnostic spine

- [`docs/specs/campaign-runner/PI_LOOP_DIAGNOSTIC_SPINE_REVIEW_PACKET.md`](docs/specs/campaign-runner/PI_LOOP_DIAGNOSTIC_SPINE_REVIEW_PACKET.md)
- [`docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md`](docs/specs/campaign-runner/PI_LOOP_RECEIPT_REPORT_OPERATOR_RUNBOOK.md)
- [`docs/specs/campaign-runner/PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md`](docs/specs/campaign-runner/PI_LOOP_RECEIPT_SCHEMA_V1_PROPOSAL.md)
- [`docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md`](docs/specs/campaign-runner/PI_LOOP_RECEIPT_COMPATIBILITY_AUDIT.md)

### Guardian

- [`docs/guardian/README.md`](docs/guardian/README.md): Guardian surface map and reading order
- [`docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md`](docs/guardian/GUARDIAN_OPERATING_CONTRACT_V0.md)
- [`docs/guardian/GUARDIAN_OPERATIONAL_CONTRACT_ADDENDUM_V0.md`](docs/guardian/GUARDIAN_OPERATIONAL_CONTRACT_ADDENDUM_V0.md)
- [`docs/guardian/GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md`](docs/guardian/GUARDIAN_PLAN_PACK_VALIDATOR_OPERATOR_RUNBOOK.md)
- [`docs/guardian/GUARDIAN_UI_COMMAND_SURFACE_CONTRACT_V0.md`](docs/guardian/GUARDIAN_UI_COMMAND_SURFACE_CONTRACT_V0.md)
- [`docs/guardian/templates/`](docs/guardian/templates/)
- [`docs/guardian/examples/sample-dry-run-plan-pack/`](docs/guardian/examples/sample-dry-run-plan-pack/)

### Context management

Promptnomicon Steward scaffolding lives under `.promptnomicon/`:

- [`.promptnomicon/promptnomicon-steward.md`](.promptnomicon/promptnomicon-steward.md)
- [`.promptnomicon/promptnomicon-steward-session.md`](.promptnomicon/promptnomicon-steward-session.md)
- [`.promptnomicon/project-reality-footer.md`](.promptnomicon/project-reality-footer.md)

Start a repository-local stewardship pass with `.promptnomicon/promptnomicon-steward-session.md` when you need current-state analysis, bounded next steps, and a receipt-shaped session output.

---

## Build a Local Wheel

Build the distribution:

```bash
python3 -m build
```

Install the wheel:

```bash
python3 -m pip install --force-reinstall dist/*.whl
```

The packaged wheel includes bundled prompts, templates, and JSON schemas under the `codex_runner` package path.

When working from an installed wheel rather than a repository checkout, point prompt and schema arguments at the installed package files under:

```text
site-packages/codex_runner/
```

---

## Development

Run the test suite:

```bash
pytest -q
```

The project package metadata is defined in `pyproject.toml`.

Current package name:

```text
codex-runner-friend-share
```

Current package version:

```text
0.1.0a0
```

This repository is not intended for public PyPI distribution.

---

## License and Distribution

Codex Runner is a private-alpha evaluation package, not public open source.

The included [`EVALUATION-LICENSE.md`](EVALUATION-LICENSE.md) permits private evaluation, inspection, installation, execution, and local backups.

It prohibits:

- redistribution
- sublicensing
- resale
- hosting the software as a service
- public publication
- removal or alteration of attribution and license notices

No rights beyond private evaluation are granted unless a separate written agreement says otherwise.

Because this repository may be visible while remaining source-available only under restrictive evaluation terms, visibility must not be interpreted as an open-source grant.

---

## Design Intent

This repository is intentionally constrained.

- It exposes a narrow execution path without publishing adjacent internal systems
- It separates orchestration, identity, execution, and durable authority
- It prefers deterministic planning and receipt-backed evidence
- It treats dry-run inspection as the recommended starting point
- It keeps experimental provider-neutral, offline, and Codexify-ingestion work outside the default CLI path
- It preserves human authority at every category boundary

Codex Runner is currently a private-alpha friend-share package. Interfaces, execution semantics, packaging strategy, and licensing terms may change as the system evolves.

---

## Project Links

- Website: [ResonantConstructs.ai](https://ResonantConstructs.ai)
- Codexify: [Codexify.Space](https://Codexify.Space)
- Community: [r/ResonantConstructs](https://reddit.com/r/ResonantConstructs)
- Discord: [Resonant Constructs](https://discord.gg/C6AvyWpd)
