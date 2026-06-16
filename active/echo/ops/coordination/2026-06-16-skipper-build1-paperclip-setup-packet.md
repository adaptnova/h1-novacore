# Skipper Build 1 Paperclip Setup Packet

## 2026-06-16 14:45:00 — SIGNED_BY_ECHO

Owner: Skipper  
Reviewer: Echo  
Gate: Iris after concrete Paperclip evidence exists  
Authority: Chase is Board. Echo is top-level operating coordinator for Build 1.

## Mission

Create the Paperclip company `Build 1` and configure it as the next-phase operating
cell for the Nova team. This is a Paperclip object/config setup task, not a
summary-only task.

## Required Company Shape

Create a new company:

- Name: `Build 1`
- Purpose: local Tier-1 operating cell for Nova coordination and execution.
- Board/operator: Chase.
- Top-level agent/manager: Echo, configured as the highest agent in the Paperclip
  reporting chain. All tier leads and active lane owners should report through Echo
  unless Chase explicitly assigns a different chain.

Do not use Riven for this phase.

## Required Projects

Create projects using the main lane names and attach correct local file paths/workspaces.

Required first projects:

1. `Coordination`
   - Owner: Echo
   - Primary path: `/adapt/novas/active/echo`
   - Reference path: `/adapt/platform/novaops/controlplane/n-voice/ops/coordination/build1-operating-cell`
2. `Paperclip Workbench`
   - Owner: Skipper
   - Primary path: `/adapt/platform/novaops/controlplane/paperclip`
   - Alternate repo path if needed: `/adapt/repos/paperclip-rust`
3. `CommsOps / Nexus`
   - Owner: Veyra
   - Primary path: `/adapt/platform/novaops/controlplane/n-voice`
   - Agent path: `/adapt/novas/active/veyra`
4. `Memory / MemFabric`
   - Owner: Axiom
   - Primary path: `/adapt/platform/memops/memfabric`
   - MemOps root: `/adapt/platform/memops`
5. `Temporal`
   - Owner: Chronos
   - Primary path: `/adapt/platform/memops`
   - Agent path: `/adapt/novas/active/chronos`
6. `DataOps`
   - Owner: Vertex
   - Primary path: `/adapt/novas/active/vertex`
   - Related n-voice path: `/adapt/platform/novaops/controlplane/n-voice`
7. `NovaOps Runtime`
   - Owner: Cosmos
   - Primary path: `/adapt/novas/active/cosmos`
   - Runtime reference path: `/adapt/platform/novaops/controlplane/n-voice`
8. `Rust/WASM Tooling`
   - Owner: Zap
   - Primary path: `/adapt/novas/active/zap`
   - Runtime reference path: `/adapt/platform/novaops/controlplane/n-voice`
9. `Acceptance Gate`
   - Owner: Iris
   - Primary path: `/adapt/novas/active/iris`
10. `Architecture Review`
    - Owner: Tecton
    - Primary path: `/adapt/novas/active/tecton`
    - Use only for substrate/routing/memory/execution-boundary decisions.

## Required Agents

Create Paperclip agent records for the active Build 1 roster:

- `Echo` — top-level operating coordinator / Chief of Staff; reports to Chase as Board.
- `Skipper` — Paperclip owner / workbench setup; reports to Echo.
- `Veyra` — CommsOps, Nexus/A2A, proof policy, voice/session/operator truth; reports to Echo.
- `Axiom` — MemFabric execution and memory substrate; reports to Echo.
- `Chronos` — Temporal, timing, durable workflows; reports to Echo.
- `Vertex` — DataOps and progress/status data model; reports to Echo.
- `Cosmos` — NovaOps runtime and lifecycle truth; reports to Echo.
- `Zap` — Rust/WASM build pressure and runtime tooling; reports to Echo.
- `Iris` — acceptance gate and onboarding discipline; reports to Echo for routing, but owns gate decisions.
- `Tecton` — architecture review only; reports to Echo for review requests.

Use the closest valid Paperclip role enum, preserving exact Nova identity in
`title` and `capabilities` when the enum is not exact.

## Codex Adapter Requirement

All Build 1 agents must use Codex as their framework:

- `adapterType`: `codex_local`
- model: `gpt-5.5`
- reasoning/thinking: highest supported setting for this adapter. Use
  `modelReasoningEffort: "high"` unless the live Paperclip adapter exposes a
  stricter/stronger value.
- approvals/sandbox: full-permission local execution where the adapter supports it.
- no Hermes execution path for this phase.

For each agent, set:

- `adapterConfig.cwd` to the proper lane/agent path above.
- `adapterConfig.instructionsFilePath` to that agent's `AGENTS.md`.
- worktree strategy only where useful for code-producing lanes. Do not force
  unnecessary worktrees for coordination-only lanes unless Paperclip requires it.

## Instruction Sheet Requirement

Every Build 1 agent must have a complete managed instruction bundle:

- `AGENTS.md`
- `AGENT.md`
- `NOVA.md`
- `MEMORY.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `SOUL.md`

If an active Nova directory is missing any of these, create or attach a managed
Paperclip instruction bundle for that agent. `AGENTS.md` must explicitly instruct
the agent to read the sibling sheets before meaningful work.

Known current gaps to verify/remediate:

- Skipper active dir currently has only `SOUL.md`.
- Zap active dir currently has no listed instruction sheets.
- Vertex active dir currently has `MEMORY.md` and `SOUL.md` only.
- Echo, Veyra, Cosmos, Tecton, Chronos, Iris have partial bundles; verify and fill
  missing sheets.
- Axiom's active working root for this phase is `/adapt/platform/memops/memfabric`;
  verify whether its Paperclip instruction bundle should live there or in a
  dedicated managed Paperclip instructions path.

## Required Initial Issues

Create a parent/control issue assigned to Echo:

- `Build 1 operating cell coordination`

Create first-wave child issues:

1. Skipper: `Create Build 1 Paperclip company and object graph`
2. Echo: `Publish Build 1 coordination rhythm and status format`
3. Veyra: `Verify Build 1 CommsOps/Nexus proof routes`
4. Axiom + Chronos: `Define MemFabric receipt and Temporal durable-intent binding`
5. Vertex + Cosmos: `Define DataOps status model and NovaOps runtime truth`
6. Zap: `Identify first Rust/WASM build-pressure artifact and command`
7. Iris: `Gate Build 1 proof quality after owner evidence exists`

Keep Tecton as review-only unless a substrate/routing/memory/execution boundary
decision is raised.

## Completion Evidence Required

Reply to Echo with:

1. Build 1 company id and URL.
2. Project list with names, ids, owners, and workspace/file paths.
3. Agent list with names, ids, roles, titles, reporting chain, adapter type,
   model, reasoning setting, cwd, and instructions path.
4. Instruction bundle status for every agent: complete or exact missing files.
5. Initial issue list with ids, assignees, statuses, and parent/child linkage.
6. Any blocked API fields or Paperclip limitations with exact endpoint/error.

Do not send ACK-only. Do not claim complete until the company, projects, agent
records, file paths, instruction paths, and first issues are visible through the
Paperclip API/UI.

— SIGNED_BY_ECHO
