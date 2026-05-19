# Safety Notes

- use dry-run first
- inspect generated campaigns and tasks before execution
- do not run against repositories with uncommitted work unless you are intentionally testing failure behavior
- do not include secrets in prompts
- do not share logs that contain private repo paths, keys, or customer/user data
- provider execution may mutate files when execute mode is enabled

Operationally, the runner is designed so the deterministic path stays explicit. If you switch into execute mode, treat it like a file-mutating action and verify the target repo state before and after the run.
