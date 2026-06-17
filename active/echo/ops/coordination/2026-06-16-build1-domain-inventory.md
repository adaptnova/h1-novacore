# Build 1 Domain Inventory

## 2026-06-16 20:59:54 — SIGNED_BY_ECHO

Source basis:

- `/adapt/platform/TIER1_TREE.md`
- `/adapt/platform/novaops/controlplane/n-voice/ops/coordination/build1-operating-cell/PROJECT_DETAIL_FOR_ECHO.md`
- `/adapt/novas/active/echo/ops/coordination/2026-06-16-skipper-build1-paperclip-setup-packet.md`

Operator correction applied: Riven is excluded from this Build 1 phase. Axiom is
the active Build 1 MemFabric owner.

| Build 1 domain | Active owner / lead | Tier-1 or domain registry lead | Domain root | Current Build 1 workspace / repo | Agent / identity dir | Notes |
|---|---|---|---|---|---|---|
| Board / Operator | Chase | Board | n/a | n/a | n/a | Chase acts as Board, not a worker agent. |
| Coordination / CoS | Echo | `/platform/CoS` - Echo | `/adapt/platform/CoS` | `/adapt/novas/active/echo` | `/adapt/novas/active/echo` | Echo is top-level Build 1 operating coordinator. |
| Paperclip Workbench | Skipper | Build 1 lane owner; not currently in `TIER1_TREE.md` | `/adapt/platform/novaops/controlplane/paperclip` | `/adapt/platform/novaops/controlplane/paperclip`; alternate repo `/adapt/repos/paperclip-rust` | `/adapt/novas/active/skipper` | Skipper owns company/project/agent setup. |
| CommsOps / Nexus | Veyra | `/platform/commsops` - Veyra | `/adapt/platform/commsops` | `/adapt/platform/novaops/controlplane/n-voice` | `/adapt/novas/active/veyra` | Veyra owns route/proof policy and current comms repair. |
| Memory / MemFabric | Axiom | Active Build 1 MemFabric owner; `TIER1_TREE.md` currently says `/platform/memops` - Riven, but Riven is excluded by Chase for this phase | `/adapt/platform/memops` | `/adapt/platform/memops/memfabric` | `/adapt/platform/memops/memfabric` | Axiom is rooted at MemFabric for this phase. |
| Temporal / TimeOps | Chronos | `/platform/timeops` - Chronos | `/adapt/platform/timeops` | `/adapt/platform/memops` | `/adapt/novas/active/chronos` | Chronos owns durable-intent/timing workflow boundary. |
| DataOps | Vertex | `/platform/dataops` - Vertex | `/adapt/platform/dataops` | `/adapt/novas/active/vertex` | `/adapt/novas/active/vertex` | Vertex owns status/progress data model for Build 1. |
| NovaOps Runtime | Cosmos | `/platform/novaops` - Cosmos | `/adapt/platform/novaops` | `/adapt/platform/novaops/controlplane/n-voice` | `/adapt/novas/active/cosmos` | Cosmos owns lifecycle/runtime truth; n-voice is current runtime control-plane workspace. |
| Rust/WASM Tooling | Zap | Build 1 lane owner; adjacent platform domain `/platform/devops` - Forge | `/adapt/platform/devops` | `/adapt/novas/active/zap`; runtime reference `/adapt/platform/novaops/controlplane/n-voice` | `/adapt/novas/active/zap` | Zap owns Rust/WASM build pressure for this cell. |
| Acceptance Gate / Strike Team | Iris | `/platform/striketeam` - Iris | `/adapt/platform/striketeam` | `/adapt/novas/active/iris` | `/adapt/novas/active/iris` | Iris gates proof quality only after owner evidence exists. |
| Architecture Review | Tecton | `/platform/architecture` - Tecton | `/adapt/platform/architecture` | `/adapt/platform/architecture/z-pure` | `/adapt/novas/active/tecton` | Tecton reviews only substrate/routing/memory/execution-boundary decisions. |

## Immediate Consolidation Notes

- Paperclip should store both the domain root and the current Build 1 workspace
  path when they differ.
- For repo sync/consolidation design, do not flatten domains into one directory.
  Use domain roots as ownership boundaries and workspace paths as active execution
  surfaces.
- Build 1 should treat Echo as the top-level agent manager under Chase as Board.
  Lane owners report through Echo for coordination, while retaining their domain
  authority.
- Do not use `rsync` yet for mutation. First define source-of-truth direction,
  exclusions, generated/runtime artifacts, and whether sync is one-way mirror,
  staged handoff, or bidirectional reconciliation.

-- SIGNED_BY_ECHO
