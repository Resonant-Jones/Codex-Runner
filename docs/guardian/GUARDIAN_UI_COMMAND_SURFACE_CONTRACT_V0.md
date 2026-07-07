# Guardian UI Command Surface Contract v0

## 1. Status

- **Status:** proposed integration contract
- **Scope:** docs-only contract for exposing the implemented Guardian CLI evidence chain to a future Codexify UI/backend surface
- **Runtime impact:** none in this repo
- **Current truth:** `codexrun guardian validate-plan-pack`, validation receipts, and `codexrun guardian orchestrate-dry-run` already exist in `Codex-Runner` as local CLI preflight tools
- **Non-goal:** this document does not make Codexify UI integration shipped

This contract defines the door between Codexify Guardian UI and Codex Runner.

The door is preflight-only.

It is not execution.

---

## 2. Purpose

The current evidence chain is local CLI-first:

```txt
Plan Pack
  -> validate-plan-pack
  -> validation receipt
  -> orchestrate-dry-run preflight
  -> orchestration log / orchestration receipt
```

That chain is now implemented on `main` in `Codex-Runner`, but it is not yet surfaced inside the Codexify Guardian UI.

This contract defines the smallest safe bridge:

```txt
Codexify Guardian UI
  -> Codexify backend command surface
  -> Codex Runner Guardian preflight commands
  -> local evidence artifacts
```

The bridge exists to expose validation and preflight evidence to the UI without smuggling execution authority into Guardian Chat.

---

## 3. Current Reality

Implemented today in `Codex-Runner`:

- `codexrun guardian validate-plan-pack`
- `codexrun guardian validate-plan-pack --write-receipt`
- `codexrun guardian orchestrate-dry-run`
- `codexrun guardian orchestrate-dry-run --write-orchestration-log --write-orchestration-receipt`

Not integrated today:

- no Codexify Guardian UI button
- no Codexify backend route or command handler for this evidence chain
- no Codex Runner daemon/service dedicated to Guardian UI calls
- no API contract for presenting receipts/logs inside Codexify

This document does not expand release truth beyond that boundary.

---

## 4. Decision Summary

The bridge should use a backend-owned command surface, not a frontend shell-out.

Recommended order of preference:

1. Codexify command-bus adapter
2. Codex Runner local daemon/service
3. Thin backend route that delegates into one of the two shapes above

Not recommended:

- direct browser or frontend subprocess access
- arbitrary shell command entry from the UI
- any path that lets the UI bypass Guardian authority locks

Why:

- the frontend is outside the trust boundary for local command execution
- backend command surfaces can enforce capability checks, path allowlists, timeouts, and audit logs
- Codexify already has a backend command/tooling layer, so the smallest compatibility move is to reuse that pattern

---

## 5. Nodes, Boundaries, Threat Model

### Nodes

- Codexify frontend (`Guardian UI`)
- Codexify backend (`API + command surface`)
- Codex Runner local process or daemon
- local filesystem under `/Volumes/Dev_SSD/Codex-Runner`
- optional future receipt viewer inside Codexify

### Trust boundaries

- browser boundary: untrusted for command invocation
- Codexify backend boundary: trusted to validate inputs and enforce capability rules
- Codex Runner boundary: trusted to run bounded Guardian preflight commands only
- filesystem boundary: evidence paths are local, explicit, and auditable

### Threat model

- honest-but-buggy frontend: wrong path, stale receipt selection, duplicate clicks
- honest-but-buggy backend: malformed command mapping, missing timeout, missing path validation
- malicious local caller with UI access: attempts path escape, receipt spoofing, or execution escalation
- compromised node: can lie about rendered UI state, so evidence truth must come from CLI outputs and hashes, not optimistic UI state

---

## 6. Authority and Non-Negotiables

The Codexify bridge must preserve the existing Guardian authority locks exactly.

The bridge must never imply or enable:

- Pi Loop invocation
- source mutation
- Codexify ingestion
- durable mutation
- provider execution
- patch application
- dispatch
- merge
- reviewer auto-fill
- trust promotion

The UI must display the current mode as:

```txt
PREFLIGHT ONLY
NO PI LOOP INVOCATION
NO SOURCE MUTATION
NO CODEXIFY INGESTION
```

Any backend contract that cannot preserve those boundaries should be rejected.

---

## 7. Interface Contract

The minimum UI-triggerable operations are:

1. Validate Plan Pack
2. Validate Plan Pack and write validation receipt
3. Run dry-run orchestration preflight
4. Run dry-run orchestration preflight and write orchestration log/receipt
5. Fetch or list the latest generated evidence artifacts for the selected Plan Pack

The minimum request fields are:

```yaml
plan_pack_path: absolute path inside /Volumes/Dev_SSD/Codex-Runner
validation_receipt_path: absolute path inside /Volumes/Dev_SSD/Codex-Runner
write_receipt: true | false
write_orchestration_log: true | false
write_orchestration_receipt: true | false
response_mode: text | json
```

The minimum response fields are:

```yaml
command_kind: validate_plan_pack | orchestrate_dry_run
result: pass | fail
reason: string
stdout_text: optional rendered text form
json_payload: optional machine-readable payload
evidence_paths:
  validation_receipt_path:
  orchestration_log_path:
  orchestration_receipt_path:
authority:
  guardian_operational: false
  plan_execution_allowed: false
  pi_loop_invocation_allowed: false
  codexify_ingestion_allowed: false
  durable_mutation_allowed: false
  provider_execution_allowed: false
  patch_application_allowed: false
  dispatch_allowed: false
  merge_allowed: false
```

The backend must not accept arbitrary command strings from the frontend.

It should accept a typed operation name plus validated arguments only.

---

## 8. Path and Capability Rules

The bridge must enforce all of the following before invoking Codex Runner:

- `plan_pack_path` must resolve inside `/Volumes/Dev_SSD/Codex-Runner`
- `validation_receipt_path` must resolve inside `/Volumes/Dev_SSD/Codex-Runner`
- neither path may resolve inside `/Volumes/Dev_SSD/Codexify-main`
- neither path may resolve inside `/Volumes/Dev_SSD/ResonantConstructs/Codexify-Core`
- the selected operation must be one of the explicitly allowlisted Guardian preflight actions
- each invocation must run with bounded timeout, bounded output capture, and explicit exit-code handling

The backend must treat all file paths as hostile until normalized and checked.

---

## 9. Data Model Reality

Source of truth by artifact:

- Plan Pack files: the selected local directory under `Codex-Runner`
- validation outcome: the current CLI run result
- validation continuity: the selected validation receipt plus current file hashes
- orchestration preflight outcome: the current `orchestrate-dry-run` result
- durable audit trail: generated local evidence under `.guardian/`

Consistency target:

- local strong consistency within one invocation
- no distributed consistency promise across Codexify and Codex Runner beyond the returned artifact paths and hashes

Conflict policy:

- latest successful artifact path may be suggested by the backend
- explicit user selection wins when multiple receipts exist
- no hidden merge of receipts or plan packs

Identity binding:

- UI session identity may authorize access to the bridge
- command authority still derives from backend capability checks and Codex Runner boundary enforcement
- receipts remain evidence artifacts, not identity grants

---

## 10. Recommended Adapter Shape

### Preferred V1: command-bus adapter

Codexify backend exposes typed internal commands such as:

```txt
guardian.validate_plan_pack
guardian.write_validation_receipt
guardian.orchestrate_dry_run_preflight
guardian.write_orchestration_evidence
guardian.list_evidence_for_plan_pack
```

Properties:

- reuses existing backend command handling patterns
- easiest place to enforce capability checks and audit entries
- keeps UI thin and declarative

### Acceptable V1.5: local Codex Runner daemon/service

Use this when repeated subprocess startup cost, streaming progress, or lifecycle isolation becomes materially important.

Properties:

- clearer process boundary
- easier future streaming/log subscription
- more moving pieces than the command-bus adapter

### Least preferred: ad hoc backend route wrapping shell commands

Only acceptable if it still uses typed operations internally and never exposes freeform shell input.

If this route is chosen, it should be treated as a temporary compatibility layer, not the long-term architecture.

---

## 11. Failure Modes

Top failure modes and required mitigations:

1. Stale receipt selected for a changed Plan Pack.
Mitigation: require receipt continuity checks and surface hash mismatch clearly.

2. Path escape or wrong repo target.
Mitigation: normalize paths, enforce repo-root allowlist, reject forbidden roots.

3. UI implies execution happened because preflight passed.
Mitigation: hard-code preflight-only labels and display all authority locks as `false`.

4. Duplicate user actions create evidence confusion.
Mitigation: return created artifact paths explicitly and sort latest artifacts by creation time.

5. Backend command hangs or emits too much output.
Mitigation: bounded timeout, bounded output capture, structured error envelope, no streaming shell passthrough in V1.

---

## 12. UI Shape for the Smallest Safe Slice

The smallest acceptable UI surface is:

- Plan Pack path input
- Validate button
- Write validation receipt button
- Orchestrate dry-run preflight button
- Evidence chain panel
- latest receipt/log/receipt-path display
- authority lock display

V1 should be trigger-plus-read only.

It should not:

- edit Plan Pack contents
- execute Pi Loop
- mutate source
- create Codexify records from Guardian evidence

---

## 13. Out of Scope

This contract does not define:

- execution-mode UI
- Pi Loop invocation from Codexify
- receipt ingestion into Codexify durable state
- remote multi-node Guardian orchestration
- background scheduling
- trust promotion workflows
- automated reviewer-decision flows

Those are separate category changes.

---

## 14. Next Implementation Slice

Smallest implementable slice after this contract:

1. Codexify docs contract mirrored on the Codexify side.
2. One backend-owned typed command for `validate-plan-pack --json`.
3. One backend-owned typed command for `orchestrate-dry-run --json`.
4. Read-only Guardian panel that renders returned JSON and artifact paths.

Stop there.

Do not add execution.

Do not add mutation.

Do not add ingestion.
