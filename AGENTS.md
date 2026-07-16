# Codex Runner Agent Operating Contract

## Start here

Codex Runner has three sibling surfaces with different authority:

- Deterministic Campaign Runner: governed repository audit and execution.
- Pi Loop Manager v0: supervised dry-run and handoff workflow. Included providers are non-mutating or handoff-oriented.
- Guardian: validation and dry-run preflight only. Guardian does not execute plans, invoke Pi Loop, mutate source, dispatch work, or promote authority.

Read `README.md`, `SAFETY.md`, and the relevant document under `docs/guardian/` or `docs/specs/campaign-runner/` before changing behavior.

## Bootstrap and validation

From the repository root:

```bash
make bootstrap
```

For an already-installed environment:

```bash
make check
```

The canonical test command is:

```bash
python3 -m pytest -v
```

## Repository invariants

- Begin execution work from a clean Git worktree.
- Keep provider execution behind the harness boundary.
- Treat receipts as evidence, never authority or approval.
- Preserve the distinction between Campaign Runner execution, Pi Loop supervision, and Guardian preflight.
- Do not silently widen Guardian authority.
- Do not commit `.venv`, `.pi/`, `.guardian/` generated evidence, credentials, or local configuration.
- Keep changes atomic and validate before committing.

## Guardian repository boundary

`guardian orchestrate-dry-run` resolves its trusted repository root in this order:

1. explicit `--repo-root`
2. `CODEX_RUNNER_REPO_ROOT`
3. the Git top-level containing the current working directory

Explicit and environment values must identify the Git repository top-level exactly. Plan packs and validation receipts must resolve inside that boundary. Boundary uncertainty fails closed.

## Validation command authority

Pi Loop validation commands are executed with shell semantics. Treat `validation_commands` as privileged operator-authored input. Do not execute validation commands from an untrusted task packet without human review.

## Closeout

Report:

- summary of changes
- files changed
- exact validation commands and results
- remaining limitations
- commit hash
