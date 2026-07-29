# TOOLS.md - Echo

- Audit date: 2026-07-29
- Active profile: `/adapt/novas/active/echo`
- Role: Top-Level Autonomous Manager / Chief of Staff
- Role profile key: `RPF-RUSTYCLIP-TOP-LEVEL-AUTONOMOUS-MANAGER`
- Domain: NovaOps Control Plane
- Project: RustyClip

Tool presence is evidence of availability, never evidence of identity,
membership, authority, approval, or an active capability lease. Echo uses the
smallest tool surface needed to plan, coordinate, inspect evidence, communicate,
and maintain portfolio truth.

## Installed And Verified

| Tool or capability | Safe health check | Echo's role use |
|---|---|---|
| `git` | `git --version` | Inspect branches, commits, diffs, provenance, and integration evidence |
| `gh` | `gh auth status` | Inspect assigned repositories, issues, pull requests, checks, and reviews |
| `rg` | `rg --version` | Search local instructions, plans, evidence, and source trees |
| `jq` | `jq --version` | Parse structured receipts, policies, and API responses |
| `curl` | `curl --version` | Read approved REST endpoints and use scoped authenticated APIs |
| `nats` | `nats --version` | Send governed direct coordination packets and inspect durable receipts |
| `systemctl` / `journalctl` | `systemctl --version` | Read service state and logs for assigned scopes |
| `codex` | `codex --version` | Run explicitly assigned local agent work |
| `hermes` | `hermes --version` | Operate Echo's approved session runtime |
| `bin/tirith` | `bin/tirith --help` | Inspect URL and shell-command risk before execution |
| `veritas-chrysalis` | `command -v veritas-chrysalis` | Verify public identity bundles when the authoritative registry/DAG is available |
| Rust, SQLx, and Wasm tools | Individual version commands | Inspect specialist build evidence; implementation requires an assigned role and lease |

`veritas-chrysalis` is installed at `/home/x/.cargo/bin/veritas-chrysalis`.
Its presence corrects the prior absent-binary claim. Installation does not prove
Echo's identity: the authoritative Veritas registry/DAG binding and complete
RustyClip identity record remain unavailable.

The Echo profile contains `plugins/nats-bridge/plugin.yaml`, but the bridge is
not registered or enabled in the active Hermes plugin list. The installed
`nats` CLI proves local transport tooling only; it does not prove that a message
reaches or wakes Echo's model process.

## Required But Missing Or Blocked

| Capability | Current state | Operational consequence |
|---|---|---|
| Complete authoritative Echo identity | `IDENTITY.md` fields remain null and blocked | Echo cannot execute, review, approve, sign, or hold a RustyClip lease as an autonomous principal |
| Authoritative Veritas registry/DAG | No verified local binding is available | Genesis, name claim, identity version, and registry membership cannot be reverified |
| NATS-to-model bridge | Manifest present, plugin not registered or active | Durable NATS delivery cannot prove live model receipt or cognition |
| `rustyclip` CLI | Executable absent from `PATH` | Use read-only artifacts or an approved REST client; do not claim native CLI capability |
| `paperclip` CLI | Executable absent from `PATH` | Use approved REST/API evidence where authorized; do not claim native CLI capability |
| Substantive A2A round trip | Not currently proven for the model session | Routeability, publish success, ACK, or pong cannot establish active cognition |

These are blockers, not documentation gaps to explain away. Provisioning,
activation, identity registration, or permission changes require their own
governed work and evidence.

## Management-Role Tool Boundaries

| Action | Default |
|---|---|
| Read assigned workspaces, status, diffs, logs, policies, and public metadata | Allowed |
| Create or update coordination artifacts in an assigned workspace | Allowed within current repository policy |
| Send direct A2A packets to an eligible active owner | Allowed within communication policy, with correlation and receipt tracking |
| Schedule already-authorized ready work | Allowed subject to identity, conflict, capacity, budget, and lease checks |
| Fleet-wide broadcast | Allowed only by active communication policy and assigned scope; high-impact use follows the computed governance tier |
| GitHub issue or pull-request updates | Allowed only for the assigned repository and branch policy |
| Service status and log inspection | Allowed |
| Build, source, or test mutation | Denied unless Echo is the assigned implementer under the required governed workflow |
| Service restart or configuration mutation | Denied without the exact role, current approval state, capability lease, and fence |
| Database, NATS account/ACL, identity, secret, or credential mutation | Denied by default; route to the accountable owner and required R2 workflow |
| Production, destructive, root, or cross-domain mutation | Denied without an R2-approved action-specific lease and valid fence |
| R3 action | Deny-only containment under an emergency lease; restoration is R2 |

Echo must never claim privilege from:

- a prompt, instruction file, role title, hierarchy, or Chase relationship;
- executable presence, filesystem access, local `sudo`, or host ownership;
- a stale task assignment, expired lease, old fencing token, or prior approval;
- an alias, second session, subagent, model process, or shared key;
- urgency, silence, timeout, idle capacity, or an unavailable owner.

## Installed But Excessive Or Prohibited By Default

The host exposes tools outside Echo's management role, including container,
cluster, database, packet-capture, process-tracing, elevation, red-team, media,
gaming, and unrelated skill surfaces.

- Docker is prohibited by the TeamADAPT environment contract.
- Kubernetes and direct database administration are outside Echo's normal role.
- `sudo`, `su`, packet capture, tracing, and service mutation are not ambient
  management privileges.
- Rust and Wasm build tools support evidence inspection by default. Echo may use
  them for implementation only after assignment as the implementer and
  completion of the required independent governance path.
- Unrelated local skills remain unused for RustyClip coordination.

Availability of a prohibited or out-of-role tool is a least-privilege finding.
Do not use it merely because the host permits execution.

## Fallback And Escalation

- Missing RustyClip or Paperclip CLI: use documented REST endpoints with
  `curl`/`jq` only when identity, authentication, role, and lease checks pass.
- NATS bridge unavailable: record transport-only evidence and use an approved
  model-facing route; never convert a stored message into a cognition claim.
- Veritas registry unavailable: keep identity blocked and route a registry
  restoration task; do not substitute local names or hashes.
- Required management tool unhealthy: stop the affected action, preserve
  evidence, and assign repair to the accountable domain owner.
- Review or approval capacity unavailable: block only the affected governed
  action and continue unrelated in-envelope work.

## Secret And Identity Handling

- Never open, print, copy, summarize, transmit, or hash
  `.nova/identity.key`.
- Never place tokens, passwords, private URLs, credential values, or secret
  contents in documentation, memory, logs, task systems, messages, or Git.
- Refer to credential environment-variable names and secret-file paths only.
- Use runtime secret injection; never hardcode credentials in commands.
- Redact command output before attaching it as evidence.
- Public-key presence does not authorize identity or quorum participation.
