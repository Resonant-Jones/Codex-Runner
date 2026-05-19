# Codex Runner Friend Share

Private-alpha package for sharing the deterministic Codex Runner path with trusted friends.

This repository is intentionally narrow:

- it is not public open source
- it is not ready for public PyPI publishing
- it packages the deterministic runner first
- Pi is treated as the future provider-neutral/offline harness layer for Guardian, not the default friend-share CLI surface
- Codex, Claude, and other providers are execution providers behind the harness boundary, not conceptual owners of Codex Runner

## What this repo is for

Use this checkout when you want a standalone, shareable Codex Runner package without exposing the full Codexify repository or adjacent project appliances.

The default path is the deterministic runner. The TUI is optional and only appears if you install the `tui` extra.

## Install from a local checkout

From the repository root:

```bash
python3 -m pip install -e .
```

If you want the optional interactive TUI:

```bash
python3 -m pip install -e .[tui]
```

## Install from a local wheel

Build the distribution:

```bash
python3 -m build
```

Install the wheel:

```bash
python3 -m pip install --force-reinstall dist/*.whl
```

The installed wheel ships the bundled prompts, schemas, and templates under the `codex_runner` package path.

## Recommended first command

Start in dry-run mode and inspect the planned work before allowing execution:

```bash
codexrun --dry-run \
  --repo-root /path/to/target-repo \
  --audit-prompt-file src/codex_runner/prompts/mega_audit.md \
  --audit-schema-file src/codex_runner/schemas/mega_audit_output.schema.json \
  --compiler-prompt-file src/codex_runner/prompts/audit_report_to_campaign_runner.md \
  --campaign-set-schema-file src/codex_runner/schemas/campaign_set.schema.json \
  --task-result-schema-file src/codex_runner/schemas/task_result.schema.json
```

If you are working from an installed wheel instead of a checkout, point the prompt and schema flags at the installed package files under `site-packages/codex_runner/`.

## Module entrypoint

`python -m codex_runner` remains supported after installation and maps to the same deterministic runner entrypoint as `codexrun`.

## Execute mode and clean trees

Do not run execute mode on a dirty repo unless you are intentionally testing failure behavior.

Deterministic execute mode expects the auto-commit invariant to hold. The runner rejects `--no-auto-commit` in deterministic mode so the clean-tree contract stays explicit.

## Pi boundary

Pi is a future provider-neutral/offline harness layer for Guardian. It is documented here as an experimental boundary note, not as the default friend-share CLI path.

This repo does not make Pi the conceptual owner of Codex Runner.

## Status

This package is a private-alpha friend-share build. Access may be revoked, and the license and safety notes in this repo remain part of the intended usage contract.
