# Agent Runtime Deployment Control Pack

## 2026-06-17 13:09:20 — CHRONOS

## Mission

Deploy the agent runtime integration path as fast as safely possible:

```text
NATS/NEXUS ingress -> Rust/MemFabric agent runtime -> Temporal durable intent ->
Paperclip control plane -> health/proof/rollback visibility
```

Paperclip is the control plane. NATS/NEXUS is the communication substrate.
Temporal owns durable ordering, retries, timeout policy, replay, and migration continuity.
MemFabric/RUS owns agent memory/runtime receipts. Systemd owns deployment supervision.

## Current Ground Truth

- Chronos identity: TimeOps / Temporal durable-intent owner.
- Build 1 company: cross-domain control plane, prefix `BUI`.
- Rusty company: MemFabric fleet control plane, prefix `RUS`.
- Paperclip local health is green on `http://127.0.0.1:3100/api/health`.
- Rusty Paperclip company has 10 registered MemFabric runtime agents.
- Existing bridge path: `/adapt/platform/novaops/controlplane/paperclip/packages/plugins/pc-bridge-memfab/run-bridge.ts`.
- MemOps bridge mapping path: `/adapt/platform/memops/memfabric/ops/pc-bridge/`.
- Deployment blocker: bridge source still contains credential-bearing default NATS URLs; externalize before promotion.

## Paperclip Control Graph

- Parent control issue: [BUI-58](/BUI/issues/BUI-58) — Chronos.
- Skipper bridge/systemd deployment: [BUI-59](/BUI/issues/BUI-59).
- Veyra NATS/NEXUS routing and owner-proof loop: [BUI-60](/BUI/issues/BUI-60).
- Tecton architecture and secret gate: [BUI-61](/BUI/issues/BUI-61).
- Iris acceptance and no-fake-proof gate: [BUI-62](/BUI/issues/BUI-62).
- Echo deployment status coordination thread: [BUI-63](/BUI/issues/BUI-63).
- Cosmos systemd host operations proof: [BUI-64](/BUI/issues/BUI-64).
- Axiom cross-domain MemOps contract alignment: [BUI-65](/BUI/issues/BUI-65).
- Chronos Temporal workflow-to-issue proof: [BUI-66](/BUI/issues/BUI-66).
- Rusty/RUS fleet health and receipt contract: [RUS-36](/RUS/issues/RUS-36).

## Hard Gates

1. No secrets in source, docs, Paperclip comments, NATS payloads, or logs.
2. Paperclip bridge runs under systemd with explicit env injection from `/adapt/secrets`.
3. Rusty health summary shows registered and healthy counts for all expected runtime agents.
4. Temporal workflow event mapping creates or updates Paperclip issues without fake status.
5. NATS/NEXUS work packets produce substantive replies, not ACK-only proof.
6. Iris acceptance verifies proof artifacts and rejects stale proof.
7. Veyra final CommsOps gate confirms the deployment path is routeable.
8. Rollback is written before promotion.

## Work Packs

### Pack A — Chronos / TimeOps

Owner: Chronos

Requirement from others:

- Skipper must provide the exact bridge service command and service account/env path.
- Veyra must confirm the NATS/NEXUS subjects and reply policy.
- Axiom/MemOps must confirm receipt schema and workflow idempotency keys.
- Iris must define acceptance proof shape.

Deliverables:

- Temporal durable-intent mapping for `started`, `completed`, `failed`, and `resume_requested`.
- Proof artifact tying workflow id, run id, Paperclip issue, NATS subject, and MemFabric receipt.
- Rollback timing and replay notes.

### Pack B — Skipper / Paperclip Bridge Deployment

Owner: Skipper

Requirements from Chronos:

- Use Paperclip as the visible control plane.
- Promote only after secret externalization and `10/10 registered` proof.
- Keep RUS company split intact; do not put Rusty agents into the Build 1 company.

Deliverables:

- Build/test/install `pc-bridge-memfab`.
- systemd unit for the external bridge runner.
- `systemctl status`, journal proof, Paperclip plugin/API proof, and rollback command.

### Pack C — Veyra / CommsOps and NATS/NEXUS Routing

Owner: Veyra

Requirements from Chronos:

- Confirm the subjects used for health, resume command, direct handoff, and session ingress.
- Require substantive owner replies for deployment acceptance.
- Do not count route finals, pongs, or ACKs as proof.

Deliverables:

- A2A launch packet to target owners.
- Route proof for `nova.<target>.direct` and `nexus.agent.<target>.direct`.
- Status escalation if any owner is routeable-only but not awake.

### Pack D — Axiom / MemOps RUS Fleet

Owner: Axiom or Rusty MemOps lead

Requirements from Chronos:

- Confirm current RUS agent registration and health.
- Align MemFabric receipt IDs with Temporal idempotency keys.
- Keep execution-layer roles in metadata, not Paperclip role fields.

Deliverables:

- `fleet.rusty.summary` proof.
- Receipt contract for workflow-to-issue linkage.
- Any missing runtime service/systemd unit list for 31001-31010.

### Pack E — Tecton / Architecture and Secret Gate

Owner: Tecton

Requirements from Chronos:

- Review credential handling before promotion.
- Confirm no source-default NATS URLs or bearer tokens remain in bridge runtime path.
- Confirm branch/worktree state is commit-safe and no unrelated dirty files are included.

Deliverables:

- Secret externalization patch or approval.
- Architecture signoff on external bridge versus embedded plugin worker.
- Risk note for systemd/env layout.

### Pack F — Iris / Acceptance Gate

Owner: Iris

Requirements from Chronos:

- Reject stale proof, ACK-only proof, and undocumented manual state.
- Verify Paperclip issue links, NATS evidence, Temporal evidence, and rollback evidence.

Deliverables:

- Acceptance checklist result: green/red with exact blockers.
- Proof artifact index.
- Final go/no-go recommendation for Chase and Veyra.

### Pack G — Echo / Status Coordination

Owner: Echo

Requirements from Chronos:

- Maintain one status thread and avoid scattering updates.
- Track issue IDs, owners, blockers, proof paths, and next check time.

Deliverables:

- Live deployment status summary in Paperclip.
- Escalation when any pack has no substantive reply.

### Pack H — Cosmos / Systemd Host Operations

Owner: Cosmos

Requirements from Chronos:

- Use systemd only. No Docker. No venv.
- Verify service dependencies and startup order.

Deliverables:

- Service unit readiness for bridge and any supporting runtime.
- `systemctl status` and `journalctl` proof commands.
- Rollback/disable path.

## Deployment Order

1. Externalize secrets in bridge runtime path.
2. Build and test bridge package.
3. Install/register bridge with Paperclip or run external bridge service.
4. Create systemd unit and start service.
5. Verify Rusty health summary and Paperclip agent state.
6. Publish a Temporal workflow sample event through mapping.
7. Verify Paperclip issue create/update from workflow state.
8. Run NATS/NEXUS owner proof loop.
9. Iris acceptance gate.
10. Veyra final deployment gate.

## `/call` Prompt

```text
/call Chronos is coordinating ASAP deployment of the MemFabric/Temporal/Paperclip agent runtime integration. Use Paperclip Build 1 as the control plane and Rusty/RUS as the MemFabric fleet surface. Parent issue: BUI-58. Required owner issues: BUI-59 Skipper bridge/systemd, BUI-60 Veyra NATS/NEXUS routing and substantive owner proof, BUI-61 Tecton architecture/secrets gate, BUI-62 Iris acceptance/no-fake-proof, BUI-63 Echo status coordination, BUI-64 Cosmos systemd host ops, BUI-65 Axiom/MemOps contract alignment, BUI-66 Chronos Temporal durable intent, and RUS-36 Rusty fleet health/receipt contract. Hard gates: no secrets in source or messages, systemd only, Paperclip health green, RUS fleet health visible, Temporal workflow-to-issue proof, NATS/NEXUS substantive replies, rollback documented before promotion. Treat ACKs/pongs/route finals as transport only. Finish and deploy ASAP; red-flag only secret exposure, destructive data movement, provider/auth failure, or substrate restart requiring operator approval.
```

— CHRONOS
