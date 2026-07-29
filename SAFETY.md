# Safety Notes

- use dry-run first
- inspect generated campaigns and tasks before execution
- do not run against repositories with uncommitted work unless you are intentionally testing failure behavior
- do not include secrets in prompts
- do not share logs that contain private repo paths, keys, or customer/user data
- provider execution may mutate files when execute mode is enabled

Operationally, the runner is designed so the deterministic path stays explicit. If you switch into execute mode, treat it like a file-mutating action and verify the target repo state before and after the run.

## Codex executable trust boundary

The deterministic Runner normally resolves `codex` from `PATH`. An operator
may instead pass `--codex-executable` with an absolute path to an executable
regular file. Runner validates that override before capability inspection and
provider execution, then uses the same resolved binary for `--version`,
`exec --help`, and every campaign `codex exec` call. A task packet, provider
response, receipt, Guardian command, or Pi Loop operation cannot select or
promote a binary. Invalid overrides fail closed and do not fall back to PATH.
