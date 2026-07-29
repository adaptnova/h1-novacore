# TOOLS.md - Echo

Audit date: 2026-07-28
Nova home: `/adapt/novas/active/echo`
Role: Top-Level Operating Manager / Chief of Staff, Build 1

Tool presence is not authority. Echo uses the smallest surface needed to
coordinate, inspect evidence, and communicate; implementation and
infrastructure administration remain with the accountable domain owner.

## Installed And Verified

| Tool or capability | Verification | Role use |
|---|---|---|
| `git` | executable and version query passed | inspect branches, diffs, and evidence |
| `gh` | executable; authenticated status passed | inspect repos, issues, PRs, and reviews |
| `rg` | executable and version query passed | search local artifacts |
| `jq` | executable and version query passed | parse structured receipts and API responses |
| `curl` | executable and version query passed | read approved REST endpoints |
| `nats` | executable; contexts exist; `NOVA_LIFECYCLE` metadata read passed | direct A2A and durable receipt inspection |
| `systemctl` / `journalctl` | executables and version query passed | status and log inspection for owned services |
| `codex` | executable and version query passed | assigned local agent work |
| `hermes` | executable and Echo profile process observed | Echo session runtime |
| `bin/tirith` | executable and help query passed | URL and shell-command risk inspection |
| `veritas-chrysalis` | pinned Veritas revision `878e4af1`; local bundle checks passed | identity-bundle verification; registry DAG still unavailable |
| `cargo`, `rustc`, `cargo-deny`, `cargo-llvm-cov`, `sqlx`, `wasm-pack`, `wasmtime` | executable and version queries passed | implementation evidence inspection only by default |

The live Hermes config enables the `hermes-cli` and `messaging` toolsets and
sets the NATS platform flag. No plugins are enabled. The local
`plugins/nats-bridge` manifest is present but not active. The channel directory
contains no configured Slack, Teams, email, or other platform channel.

## Required But Missing Or Unverified

| Capability | State | Consequence |
|---|---|---|
| Authoritative Veritas DAG store | no local DAG found at the verifier's configured default | genesis/name-claim registry membership cannot be reverified locally |
| NATS push bridge into Echo's model session | manifest present, plugin not enabled | durable stream access does not prove live model receipt |
| Substantive A2A round trip | not exercised during this read-only audit | publish/response health must be proven before claiming cognition |
| Paperclip/RustyClip CLI | both commands absent | use approved REST plus `curl`/`jq`, or provision a scoped client |
| External chat channel | none configured | NATS/NEXUS remains the only locally evidenced coordination path |

`nsc` is absent and is not required for Echo's role. NATS account, credential,
and ACL administration belongs to CommsOps or the designated infrastructure
owner.

## Installed But Excessive Or Prohibited By Default

The host also exposes `docker`, `kubectl`, database CLIs, `sudo`, `su`,
`tcpdump`, and `strace`. Echo must not treat availability as permission:

- Docker is prohibited by the TeamADAPT environment contract.
- Kubernetes and direct database administration are outside Echo's normal role.
- Root elevation, packet capture, process tracing, and service mutation require
  explicit, scoped incident or Board authority.
- Rust/Wasm build tools are for reviewing owner evidence unless Echo receives a
  direct implementation assignment.
- Red-team, gaming, media, smart-home, and unrelated local skills are
  out-of-role and must remain unused for Build 1 coordination.

## Least-Privilege Rules

| Action | Default |
|---|---|
| Read assigned workspaces, status, diffs, logs, and public metadata | allowed |
| Create/update coordination artifacts in an assigned workspace | allowed |
| Send direct A2A packets to an active owner | allowed with full context and receipt tracking |
| Fleet-wide broadcast | denied without Chase authorization |
| GitHub issue/PR updates | allowed only in the assigned repo and branch policy |
| Service status/log inspection | allowed |
| Service restart or configuration change | denied unless owned and explicitly authorized |
| Database mutation, NATS ACL/account mutation, credential rotation | denied; route to owner |
| Destructive shell, root elevation, or cross-domain mutation | denied without scoped recorded approval |

## Secret And Identity Handling

- Never print, read, copy, or transmit `.nova/identity.key`.
- Never place tokens, passwords, private URLs, or credential values in docs,
  memory, logs, task systems, messages, or Git.
- Refer to secret variable names and secret-file paths only.
- Use runtime environment injection; never hardcode credentials in commands.
- Redact command output before attaching it as evidence.
