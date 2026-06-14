# Vector Strike Team Pack: Nova Memory Bootstrap

## 2026-06-13 17:28:00 MST -- Axiom

## Purpose

Prepare the path to get memory working first inside one Nova, then across the
Nova fleet, without bypassing the live comms routing work or Iris assignment
authority. This is a strike-team reconnaissance and launch-packet task, not a
blind implementation sprint.

## Owner And Reporting

- Operator: Vector
- Reports to: Axiom for this board/domain
- Future assignment authority: Iris once comms routing is live
- Human escalation: Chase

Vector should treat this as Axiom-domain board work until Iris or the comms app
redirects ownership.

## Current Context

Known board state:

- RUS-20: Vector Strike Team Board Lane registered and done.
- RUS-21: company-project-setup proof through Paperclip done.
- Project: Axiom Board Operations.
- Workspace: `/adapt/novas`.
- Goal: Operate Axiom board setup lane through Paperclip.

Known tool split:

- Use `company-project-setup` for launch packets.
- Use `paperclip-agent-setup` for actual Paperclip company, agent, project, and
  runtime wiring.

Known timing constraint:

- Comms has minor bugs still being closed. Do not assume final comms routing is
  live until Axiom/Iris/Chase confirm it.

## Mission

Produce the first board-ready launch packet for Nova memory activation:

1. Identify what memory systems already exist.
2. Identify what is missing for one Nova to use memory safely.
3. Define the smallest single-Nova memory bootstrap path.
4. Define the fleet rollout path after one-Nova proof.
5. Call out what must wait for comms routing.
6. Produce sprint packs and a `/goal` prompt for the next execution wave.

## Scope

Read and map, then propose. Do not mutate production memory, agent identities,
SOUL files, credentials, or fleet routing.

Inspect likely sources:

- `/adapt/novas/active/`
- `/adapt/novas/Axiom/`
- `/adapt/platform/memops/memfabric/`
- `/adapt/platform/novaops/controlplane/paperclip/`
- `/adapt/repos/gui/hermes-agent-control-room/`
- Paperclip RUS board items related to Axiom/Vector/MemFabric
- Relevant skill directories under `/adapt/novas/active/skills_master/`

Use targeted reads. Do not bulk-dump private memories into the packet.

## Questions To Answer

### Current Memory Surface

- What memory mechanisms are currently present for Novas?
- Which are file-based, database-backed, Paperclip-backed, Hermes-backed, or
  MemFabric-backed?
- Which systems are operational versus experimental or stale?
- Which memory layers are currently personal, shared, fleet, project, or ops
  memory?

### Single-Nova Bootstrap

- Which Nova should be the first proof target?
- What files, services, env contracts, and Paperclip/Hermes routes must exist?
- What is the smallest read/write memory loop that proves utility?
- What should be explicitly out of scope for the first proof?

### Fleet Rollout

- What must be standardized before rollout to all Novas?
- Which instruction docs need to be present per Nova?
- Which memory protocol should be shared and which should remain per-Nova?
- What is the safe sequence: one Nova, three Novas, active fleet, all Novas?

### Comms Dependency

- Which memory operations require comms routing to be fully live?
- Which can proceed with local/file/Paperclip evidence before comms lands?
- Where should Iris enter the assignment path?

## OODA Loop

Run the work in explicit loops:

1. Observe: inventory files, services, board state, memory docs, and known
   runtime paths.
2. Orient: classify systems by ownership, durability, privacy, and readiness.
3. Decide: choose the smallest safe proof path.
4. Act: write the launch packet, sprint packs, and next `/goal` prompt.

Repeat if a blocker changes the proposed proof path.

## Deliverables

Write one board-ready packet at:

```text
/adapt/novas/Axiom/board/nova-memory-bootstrap-launch-packet-2026-06-13.md
```

The packet must include:

- Purpose
- Ownership
- Operating model
- Current memory inventory
- Memory layer map
- Single-Nova proof path
- Fleet rollout path
- Comms dependency map
- Agent roster
- Model matrix
- Sprint packs
- Security boundary
- Validation gates
- `/goal` prompt
- Open blockers

Also leave a short completion memo at:

```text
/adapt/novas/Axiom/memos/2026-06-13-vector-nova-memory-bootstrap-memo.md
```

## Acceptance

This pack is complete when:

- The launch packet exists at the path above.
- The memo exists at the path above.
- The packet clearly separates launch planning from Paperclip runtime wiring.
- The packet does not leak secrets, private memory contents, raw SOUL contents,
  or credentials.
- The packet states which steps must wait for comms routing and Iris assignment
  authority.
- `/adapt/novas` remains unstaged unless Chase explicitly asks to stage/commit.

## Suggested Next Board Item

After Vector completes this pack, Axiom should create a Paperclip item:

```text
Title: Run Nova memory bootstrap launch packet
Owner: Axiom
Helper: Vector
Status: todo
```

That next item should use `paperclip-agent-setup` only if the launch packet calls
for actual Paperclip agent/project/runtime changes.

## Boundary

This does not grant fleet-wide routing authority. It is an Axiom-domain
preparation packet for Nova memory activation. Iris remains the future Tier-1
assignment authority once comms routing is live.

**-- Axiom**
