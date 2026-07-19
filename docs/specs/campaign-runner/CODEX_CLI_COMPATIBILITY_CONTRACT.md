# Codex CLI Structured-Output Compatibility Contract

## Status

- Status: implemented fail-closed compatibility guard
- Scope: Deterministic Campaign Runner Codex provider boundary
- Live proof date: 2026-07-19
- ADR impact: aligned with existing architecture; no new ADR required

## Purpose

Codex Runner requires schema-constrained provider output for audit, campaign
compilation, and task-result stages. This contract prevents a locally installed
Codex CLI from reaching provider execution when it cannot satisfy that
structured-output requirement.

This contract does not change MCP, Pi Loop, Guardian, receipt authority, or
campaign semantics.

## Required capability

The Codex provider path requires `codex exec --help` to advertise the exact
`--output-schema` option. Runner detects capability from local command help,
not from a guessed version range.

The accepted command shape remains:

```text
codex [model/config options] exec \
  --output-schema <schema.json> \
  -o <output.json> \
  <prompt>
```

Runner does not substitute prompt-only JSON instructions or treat
`--output-last-message` as equivalent schema-constrained generation.

## Detection method

Before resolving the base Git reference, creating run artifacts, invoking a
provider, or entering `run_pass()`, Runner executes these non-provider
inspection commands:

```text
codex --version
codex exec --help
```

Compatibility requires:

1. `codex exec --help` exits zero.
2. Its stdout or stderr includes the exact token `--output-schema`.

Version output is diagnostic evidence only. It does not independently grant
compatibility.

## Fail-closed behavior

Missing executables, failed or malformed help output, and missing
`--output-schema` support stop the Runner before:

- provider execution;
- audit or campaign artifact creation;
- campaign state loading or mutation;
- state-transition recording.

The error reports the detected version, missing capability, exact inspection
command, inspection exit code when available, remediation guidance, and
`provider_execution_occurred: false`.

No missing capability is downgraded to a warning.

## Verified local evidence

Environment:

- Machine: `AxisNode.local`
- Date: 2026-07-19
- Executable: `/opt/homebrew/bin/codex`
- Version: `codex-cli 0.36.0`

Observed `codex exec --help` output advertises:

```text
--json
--output-last-message <LAST_MESSAGE_FILE>
```

It does not advertise `--output-schema`. Direct execution previously failed:

```text
error: unexpected argument '--output-schema' found
```

Classification: output capture is available, but no equivalent
schema-constrained generation mechanism is exposed by the installed CLI.

Therefore `codex-cli 0.36.0` is verified incompatible with the current Runner
Codex provider contract. No minimum compatible version is claimed because no
compatible version was installed and proved in this task.

## Schema enforcement

The provider flag constrains generation to the stage schema. Runner then reads
the generated JSON and applies stage-specific invariants before campaign state
may advance, including audit identity, campaign structure, required task-result
fields, and allowed status values.

Provider exit code zero alone does not prove valid JSON, schema compliance,
semantic quality, test success, approval, or authorization. Invalid or
unverifiable output must raise a Runner error and must not advance state.

## Live proof outcome

The previous MCP transport proof reached the Runner-owned provider boundary but
failed when Codex CLI 0.36.0 rejected `--output-schema`.

After this guard, a clean disposable repository was exercised through the full
Deterministic Runner CLI command. The Runner exited `1` during capability
inspection with the required error fields and `provider_execution_occurred:
false`. Initial and final Git status were clean. No audit, campaign, task, run,
or state-transition artifact was created.

Final result:

```text
compatibility guard: PASS
semantic campaign completion: BLOCKED
```

## Remediation and deferred work

Official OpenAI installation guidance identifies `codex --upgrade` as an update
path. Operators may upgrade, but must re-run `codex exec --help` and prove the
required capability locally; a changed version number is insufficient.

Deferred work:

- identify and live-prove a Codex CLI exposing `--output-schema`;
- record that executable path and version without generalizing to an unproved
  version range;
- repeat end-to-end disposable campaign generation and schema validation;
- consider an alternative provider mechanism only if it preserves mandatory
  schema enforcement and state safety.

Public support claims remain unchanged until semantic campaign completion is
proved.
