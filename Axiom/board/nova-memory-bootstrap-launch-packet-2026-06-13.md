# Nova Memory Bootstrap Launch Packet

## 2026-06-13 17:35:21 MST -- Axiom

## Purpose

Bring memory online inside one Nova first, then roll the same contract to the active Nova fleet.
This packet is execution-oriented: it separates what is already proven, what must be standardized,
and what should move next.

This is not the cognitive expansion layer yet. It is the runtime memory spine the cognitive layer
will stand on.

## Ownership

- Board company: Rusty
- Company ID: `4ca379c4-4bec-4e3a-866a-9b4ff902d4b4`
- Prefix: `RUS`
- Primary lane: `Nova Memory Spine v1`
- Project ID: `264bd299-b55b-424c-a9b2-def1dd94a024`
- Goal ID: `7310fe63-63bf-4f16-8526-d5c7e5d39cf8`
- Lead: Axiom, MemOps Tier 1 Lead
- Strike-team support: Vector
- Future assignment authority: Iris once comms routing is live
- Default canary: Tecton

## Operating Model

Hard boundary:

- Temporal owns durable intent, order, retry, and dead-letter decisions.
- NATS carries wake/resume commands.
- Agent supervisor or CLI wrapper performs actual start/resume.
- MemFabric owns canonical memory event truth, projection, replay, and evidence.
- Per-Nova memory remains identity-bound; shared memory is a bridge, not a replacement for
  individuality.

Paperclip coordinates execution. Git, systemd, service health, and MemFabric evidence decide truth.

## Current Board State

- `RUS-22`: Nova Memory Spine v1 control packet, blocked by Paperclip disposition recovery.
- `RUS-23`: Pack 1A truth inventory, blocked.
- `RUS-24`: Pack 1B memory substrate/database map, blocked.
- `RUS-25`: Pack 1C Nova Memory Contract v1, blocked.
- `RUS-26`: Pack 1D wake/resume control boundary, blocked.
- `RUS-27`: Pack 1E canary gates, blocked.
- `RUS-28`: Pack 2 canary implementation, backlog.
- `RUS-29`: Pack 3 canary live proof, backlog.
- `RUS-30`: Pack 4 fleet rollout template, backlog.
- `RUS-31`: Pack 5 all-Novas rollout, backlog.
- `RUS-32`: Pack 6 cognitive layer readiness review, backlog.
- `RUS-33`: Vector strike-team launch-packet retry, blocked by Paperclip disposition handling.

Decision: do not create a duplicate strategic lane. Use `Nova Memory Spine v1` as the real track,
repair Paperclip disposition separately, and execute the canary path from this packet.

## Current Memory Inventory

### Nova File Memory

Tecton already has a complete seven-layer filesystem layout:

- L0 intake/archive directories under `/adapt/novas/active/tecton/memory/l0/`
- L1 identity files under `/adapt/novas/active/tecton/memory/l1/`
- L2 structured markdown/domain/tool files under `/adapt/novas/active/tecton/memory/l2/`
- L3 semantic index state under `/adapt/novas/active/tecton/memory/l3/data/`
- L4 verbatim JSON recall records under `/adapt/novas/active/tecton/memory/l4/data/`
- L5 knowledge/dreamer state under `/adapt/novas/active/tecton/memory/l5/`
- L6 directory reserved under `/adapt/novas/active/tecton/memory/l6/`

Tecton also has legacy/current identity surfaces:

- `/adapt/novas/active/tecton/MEMORY.md`
- `/adapt/novas/active/tecton/SOUL.md`
- `/adapt/novas/active/tecton/USER.md`
- `/adapt/novas/active/tecton/memories/MEMORY.md`
- `/adapt/novas/active/tecton/memories/SOUL.md`
- `/adapt/novas/active/tecton/domains/*.yaml`

Do not copy raw identity, SOUL, or private memory contents into board artifacts.

### Fleet Memory Surfaces

Observed active Nova memory patterns include:

- Root `MEMORY.md` files per Nova.
- `memories/MEMORY.md` files with locks.
- Layered `memory/l0` through `memory/l6` layouts for newer templates.
- `memory.mdl` and `memory.mmd` legacy/native files.
- `.remember` local session memory.
- Inbound handoff files plus metadata.
- Voice memory JSONL under active voice state.
- MemFabric live runtime evidence for canonical memory, replay, projection, Temporal, and mesh.

This means we are not starting from zero. The missing piece is a single normalized contract that
ties per-Nova identity memory to MemFabric canonical events and projection-backed recall.

## Memory Layer Map

Use seven layers as the active contract:

| Layer | Role | First implementation target |
| --- | --- | --- |
| L0 | Intake buffer | Session/log/paste landing under each Nova |
| L1 | Native identity | SOUL/MEMORY/USER, loaded locally and never flattened into shared memory |
| L2 | Structured injection | Domain/tool/protocol markdown for session start and task context |
| L3 | Semantic search | Domain-scoped embeddings and indexes |
| L4 | Verbatim recall | Exact conversation/session recall with redaction controls |
| L5 | Consolidation | Dreamer/wiki/entity summaries from L0/L4 |
| L6 | Cross-tool bridge | MemFabric/NATS/fjall/redb bridge and cold archive references |

MemFabric canonical event truth sits below and beside these layers:

- Redpanda canonical topic: `memfab.memory.events.v1`
- Audit topic: `memfab.audit.events.v1`
- Dead-letter topic: `memfab.memory.dead_letters.v1`
- Qdrant collection: `memfab_memory`
- NebulaGraph space: `memfab_frontier`
- Temporal namespace: `memfab-frontier`

## Substrate And Database Map

Running services observed through systemd:

- NATS: active
- Redpanda: active
- DragonflyDB: active
- Redis cluster and Redis server: active
- PostgreSQL main cluster: active
- PostgreSQL TeamADAPT node on port 18030: failed
- Qdrant: active
- Weaviate: active
- NebulaGraph graphd/metad/storaged: active
- Neo4j: active
- InfluxDB: active
- Grafana: active
- MemFabric ingest/indexer/query/graph/context/emotion/Temporal/Wasm/security/runtime services:
  active

Treat the failed TeamADAPT PostgreSQL node as a known gap. It does not block the Tecton canary
unless the selected implementation tries to use that node for authoritative metadata.

## Existing MemFabric Evidence

Already proven:

- Packet 123 e2e memory path summary has `packet123_ok=true`.
- Packet 131 cognitive mesh summary has `packet131_ok=true`.
- Packet 116 Temporal evidence proves `memfab-frontier` namespace and CLI bridge workflow starts.
- Active Nova memory replay canary used synthetic active-Nova-shaped input and proved canonical
  ingest, audit, dead-letter, restart, and duplicate no-op handling without copying private memory.

Known weakness:

- Active Nova replay hybrid query completed but returned degraded vector/lexical/graph backends
  with zero hits. The canary must therefore prove projection-backed recall, not just write/audit.

## Single-Nova Proof Path

Canary: Tecton.

Why Tecton:

- It already has a complete L0-L6 filesystem layout.
- It has current domain manifests and memory architecture docs.
- It is the default canary in `RUS-22`.
- It has enough existing local memory state to test routing without exposing raw private contents.

Minimum proof:

1. Write a synthetic, non-private Tecton memory event into L0.
2. Convert it to a signed MemFabric raw ingest envelope with:
   - `agent_id=tecton`
   - `incarnation_id`
   - `memory_kind`
   - `payload_hash`
   - bitemporal valid/transaction timestamps
   - source path reference, not raw private content
3. Commit it through MemFabric ingest into `memfab.memory.events.v1`.
4. Verify Redpanda canonical offset and audit event.
5. Wait for or trigger projection into Qdrant/Tantivy/NebulaGraph.
6. Run hybrid recall for a canary token and require at least one redacted hit.
7. Write a local canary receipt under Tecton's L6 bridge directory.
8. Run a Temporal workflow that records durable intent/order/retry for the canary.
9. Publish a NATS wake/resume command only as a signal.
10. Verify the supervisor/CLI remains the only process that starts/resumes the Nova.

Out of scope for the first proof:

- Raw SOUL or private memory publication.
- Fleet-wide routing changes.
- Cognitive layer/plasticity work.
- Replacing existing local memory files.
- Any direct Paperclip mutation of Nova process state.

## Implementation Surfaces

Expected file/code targets for the next implementation wave:

Nova-side:

- `/adapt/novas/active/tecton/memory/l6/` for canary manifest, bridge receipt, and redacted
  MemFabric references.
- `/adapt/novas/active/tecton/memory/l0/intake/` for synthetic canary event input.
- `/adapt/novas/active/tecton/domains/` for domain declaration checks.
- `/adapt/novas/active/a_nova_template/` for later fleet template propagation after canary proof.

MemFabric-side:

- `crates/memfab-types` for stable memory/event/id types if the current schema is insufficient.
- `crates/memfab-ingest` for canonical validation and Redpanda write behavior.
- `crates/memfab-indexer` and `crates/memfab-indexer-core` for Qdrant/Tantivy projection.
- `crates/memfab-query` for redacted hybrid recall.
- `crates/memfab-temporal-contract` for durable workflow contract types.
- `crates/memfab-temporal` for Temporal worker/runtime behavior.
- `crates/memfab-agent` or supervisor-side wrappers only for boundary evidence, not direct memory
  truth mutation.
- `docs/production/` for permanent redacted evidence.
- `runtime/` for ignored raw transient evidence.

Contract shape:

```text
write_event(agent_id, incarnation_id, memory_kind, source_ref, payload_hash, bitemporal, privacy)
recall(agent_id, query, domain, temporal_bounds, redaction_policy)
promote(agent_id, event_id, target_layer, summary_hash, provenance)
replay(agent_id, event_id | offset | time_range)
redact(agent_id, event_id, policy, reason)
health(agent_id, layers, substrates)
```

The contract must store references and hashes for sensitive local memory, not raw private text.

## Fleet Rollout Path

Rollout sequence:

1. Tecton canary.
2. Three-Nova ring: Tecton, Iris, Echo or Vaeris depending on comms readiness.
3. Active subscribed fleet: tecton, herald, iris, echo, vaeris, synergy, cosmos, pathfinder, zap,
   oracle, vox, switch.
4. Remaining `/adapt/novas/active` profiles after inventory and owner confirmation.
5. Archived/recovered profiles only after explicit migration approval.

Fleet standardization required before step 3:

- Every Nova has explicit `AGENTS.md`, `AGENT.md`, `NOVA.md`, `MEMORY.md`, `TOOLS.md`,
  `HEARTBEAT.md`, and `SOUL.md` equivalents or documented exceptions.
- Every Nova has a memory manifest declaring enabled L0-L6 layers.
- Every Nova has a privacy policy for what may be bridged into MemFabric.
- Every Nova has a stable `agent_id`, `incarnation_id`, and domain list.
- Every Nova has a local health command and a rollback path.

## Comms Dependency Map

Can proceed now:

- File/path inventory.
- Tecton memory manifest.
- Synthetic canary event generation.
- MemFabric ingest/projection/replay proof.
- Temporal workflow proof.
- Paperclip board cleanup.
- Validation docs and launch packet execution.

Wait for Iris/comms authority:

- Fleet-wide assignment changes.
- Changes to active Nova routing.
- All-Novas wake/resume broadcasts.
- Any policy that changes who receives or owns memory work.
- Cross-Nova shared memory activation beyond a controlled test ring.

## Agent Roster

Immediate execution:

- Axiom: lead, contract, merge gate, board repair, final acceptance.
- Vector: strike-team mapping, independent review, packet cleanup.
- Tecton: canary target.
- Iris: future assignment authority once comms routing is live.

Later ring candidates:

- Echo or Vaeris for comms-heavy memory flow.
- Mnemos for memory-specialist validation.
- Chronos/Skipper for Temporal/Paperclip bridge review.

## Model Matrix

- Axiom: `gpt-5.5`, high reasoning.
- Vector and peer workers: `gpt-5.3-codex-spark`, high reasoning.
- Keep Symphony on roadmap only; Paperclip is the active control point.

## Sprint Packs

### Pack A: Board And Disposition Repair

Objective: clear Paperclip execution noise without duplicating work.

Tasks:

- Leave `RUS-33` blocked as evidence or close it with this packet if accepted.
- Move `RUS-22` from blocked to in-review/done once this packet is attached.
- Reassign follow-up execution to Axiom with Vector as reviewer.
- Ensure project workspace remains `/adapt/novas` and worktree parent remains
  `/adapt/worktrees/novas-memory-paperclip`.

Acceptance:

- The board has one active memory lane.
- No duplicate launch-packet issues remain active.
- `/adapt/novas` remains unstaged unless Chase approves staging.

### Pack B: Tecton Memory Manifest And Contract

Objective: define the exact per-Nova memory contract before writing runtime code.

Tasks:

- Add a Tecton canary manifest that lists L0-L6 paths and enabled capabilities.
- Define `write_event`, `recall`, `promote`, `replay`, `redact`, and `health`.
- Keep substrate traits separate from heavy DB implementations.
- Define redaction and source-reference rules.

Acceptance:

- Manifest exists.
- Contract is documented.
- No private memory content is copied.

### Pack C: Tecton Synthetic Canary Write

Objective: prove canonical write/audit for one non-private canary event.

Tasks:

- Generate a synthetic Tecton memory event.
- Feed it to MemFabric ingest using current live-service patterns.
- Capture canonical Redpanda topic/partition/offset.
- Capture audit ID/hash.
- Capture dead-letter behavior for one intentionally invalid event.

Acceptance:

- Canonical event exists.
- Audit exists.
- Invalid event is dead-lettered.
- Evidence contains hashes and IDs only.

### Pack D: Projection And Recall Proof

Objective: close the current gap from write-only to useful recall.

Tasks:

- Trigger or wait for Qdrant/Tantivy/NebulaGraph projection.
- Run hybrid recall for the canary token.
- Require at least one redacted hit.
- Record degraded backend state if any backend misses.

Acceptance:

- Hybrid query returns a redacted canary hit.
- Projection IDs are captured.
- Any degraded backend has a named owner and next action.

### Pack E: Temporal/NATS/Supervisor Proof

Objective: prove memory resume control without crossing ownership boundaries.

Tasks:

- Start a Temporal workflow for Tecton memory canary intent.
- Publish a NATS wake/resume command as signal only.
- Verify supervisor/CLI owns actual process start/resume.
- Attach workflow ID, NATS subject, ack, and supervisor evidence.

Acceptance:

- Temporal workflow proves durable order/retry.
- NATS carries only command signal.
- Supervisor/CLI performs or refuses actual start/resume.
- Paperclip records status only.

### Pack F: Three-Nova Ring

Objective: extend only after Tecton passes.

Tasks:

- Choose two additional Novas with Iris/comms alignment.
- Apply the same manifest and canary event pattern.
- Compare layer readiness, recall behavior, and rollback needs.

Acceptance:

- Three independent Nova canaries pass.
- Differences are documented as template migrations, not ad hoc hacks.

### Pack G: Active Fleet Rollout

Objective: activate memory spine across the active subscribed fleet.

Tasks:

- Apply manifest template to active fleet.
- Execute synthetic write/recall/replay per Nova.
- Record fleet matrix.
- Keep shared memory disabled except controlled L6 bridge references.

Acceptance:

- Active subscribed fleet has memory manifests.
- Each Nova has write/recall/replay evidence.
- No raw private memory is published.

### Pack H: Cognitive Layer Readiness

Objective: decide when deeper cognitive memory layers can start.

Tasks:

- Review memory contract performance.
- Review privacy/identity boundaries.
- Review projection and recall quality.
- Identify where cognitive layers attach without collapsing separation of concerns.

Acceptance:

- Cognitive work has explicit attach points.
- Runtime memory spine is stable enough for deeper work.

## Validation Gates

Required before canary acceptance:

- MemFabric services active.
- Tecton L0-L6 paths present.
- Canonical event write succeeds.
- Audit event succeeds.
- Invalid event dead-letters.
- Hybrid recall returns at least one redacted hit.
- Temporal workflow starts and records durable state.
- NATS wake/resume subject is documented.
- Supervisor/CLI boundary is verified.
- No private raw content in tracked docs.

Suggested verification commands:

```sh
systemctl --no-pager --plain list-units 'memfab*' 'nats*' 'redpanda*' 'qdrant*'
jq '.summary' /adapt/platform/memops/memfabric/docs/production/packet_123_e2e_memory_path_report.json
jq '.summary' /adapt/platform/memops/memfabric/docs/production/packet_131_cognitive_mesh_report.json
jq '.bridge.namespace, .workflows[].workflow_id' \
  /adapt/platform/memops/memfabric/docs/production/packet_116_temporal_live_smoke_report.json
find /adapt/novas/active/tecton/memory -maxdepth 2 -type d | sort
git -C /adapt/novas status --short -- Axiom active/docs/guides active/skills_master/agent-operations
```

## Security Boundary

Allowed in board docs:

- File paths.
- Service names.
- Non-secret env var names.
- Hashes, IDs, offsets, timestamps, and redacted evidence.
- Synthetic canary payload descriptions.

Not allowed:

- Raw SOUL contents.
- Raw private memories.
- Credentials or auth tokens.
- Unredacted conversation dumps.
- Fleet-wide route changes without Iris/comms authority.

## Open Blockers

- Paperclip disposition handling blocked `RUS-33` after two successful Vector runs but no
  deliverables.
- Several `Nova Memory Spine v1` first-wave issues are blocked under Axiom and need board cleanup.
- TeamADAPT PostgreSQL node on port 18030 is failed while the main PostgreSQL cluster is active.
- Active Nova replay query proof previously returned no projection hits.
- Final comms routing/Iris assignment authority is not confirmed live in this packet.

## Next Action

Execute Pack A immediately, then Pack B and Pack C against Tecton. Do not wait for fleet comms to
start the single-Nova canary. Do wait for Iris/comms authority before broad fleet assignment and
all-Nova wake/resume.

## Execution Update

2026-06-13 17:49:00 MST:

- `RUS-22` through `RUS-27` were closed by this packet.
- `RUS-33` was closed as the Vector retry/disposition artifact.
- `RUS-28` was checked out to Axiom and moved to `in_progress`.
- Tecton canary manifest was written at
  `/adapt/novas/active/tecton/memory/l6/memfabric-canary-manifest.json`.
- Synthetic non-private L0 event was written at
  `/adapt/novas/active/tecton/memory/l0/intake/sessions/memfabric-canary-2026-06-13.json`.
- Canonical write passed:
  - raw input topic: `memfab.agent.events.v1`
  - raw input offset: `738`
  - canonical topic: `memfab.memory.events.v1`
  - canonical offset: `4`
  - event ID: `tecton-canary-20260613174305`
  - event hash: `aeca9ef466ac95813ca008cf35767bc1c608e1b11de86f44320a53937fc009b0`
- Audit passed for the same event hash.
- Dead-letter passed with invalid synthetic event
  `tecton-canary-invalid-20260613174541`.
- Hybrid recall passed through the service endpoint with the canary as rank 0:
  - Qdrant vector: healthy, 20 hits
  - Tantivy lexical: healthy, 1 hit
  - NebulaGraph path: degraded marker present, 0 hits
- Temporal proof passed through `memfab-frontier` with 10 workflow starts.
- NATS signal was published to `fleet.rusty.agent.tecton.command.resume` as signal-only evidence.
- Supervisor/CLI boundary held: no direct start/resume was performed by this canary path.

Receipt:

```text
/adapt/novas/active/tecton/memory/l6/memfabric-canary-receipt-2026-06-13.json
```

Remaining before closing `RUS-28`:

- Decide whether graph degraded marker blocks canary closure or becomes `RUS-29`/graph follow-up.
- If accepted as partial degradation, close `RUS-28` and move to three-Nova ring planning after
  Iris/comms authority.

## Goal Prompt

```text
/goal Execute Nova Memory Spine v1 from launch packet to Tecton canary proof.

Start in /adapt/novas and /adapt/platform/memops/memfabric. Use Paperclip company Rusty and the
Nova Memory Spine v1 project. Follow the packet at
/adapt/novas/Axiom/board/nova-memory-bootstrap-launch-packet-2026-06-13.md.

Objectives:
1. Repair Paperclip board disposition so there is one active memory lane.
2. Keep /adapt/novas unstaged unless explicitly approved.
3. Build the Tecton memory manifest and minimal memory contract.
4. Run a synthetic non-private Tecton canary write through MemFabric canonical ingest.
5. Prove Redpanda canonical event, audit event, dead-letter handling, projection, and hybrid recall.
6. Prove Temporal durable intent/order/retry plus NATS wake/resume signal while preserving the
   supervisor/CLI actual start/resume boundary.
7. Produce evidence with IDs, hashes, offsets, and redacted summaries only.
8. Prepare the three-Nova ring rollout only after Tecton passes.

Hard rules:
- Do not expose raw SOUL, raw private memory, credentials, or unredacted conversations.
- Do not mutate fleet routing or assignment authority before Iris/comms confirmation.
- Temporal owns durable intent/order/retry.
- NATS carries wake/resume commands.
- Supervisor or CLI performs actual start/resume.
- MemFabric owns canonical memory truth, projection, replay, and evidence.

Run OODA loops after each pack:
Observe current evidence and service state.
Orient by readiness, privacy, durability, and rollback.
Decide the smallest next safe action.
Act, verify, and write the result back to the board/evidence docs.
```

**-- Axiom**
