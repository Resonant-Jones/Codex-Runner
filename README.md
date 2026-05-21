
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

---

Project Links
Find more about Codexify and Resonant Constructs here:

Website: https://ResonantConstructs.ai
Codexify space: https://Codexify.Space
Community: https://reddit.com/r/ResonantConstructs
Discord: https://discord.gg/C6AvyWpd
