# L7+ fjall 3 Spike

**Owner (autonomous):** Riven  
**Date started:** 2026-05-29  
**Purpose:** Prototype and validate fjall 3.x as the durable core of the next-generation L7+ meta-memory layer for the Adapt Nova fleet.

## Context
This spike evolves the proven L6 hybrid architecture already running in production (see `/adapt/novas/active/mnemos/l6-store-host/` and the Wasm FFI in `l6-store-wasm`).

Current real production pattern (L6):
- High-volume event / append paths → fjall (`events.fjall`, `store.fjall`)
- Snapshots, cursors, meta → redb (`meta.redb`)
- Thin no_std Wasm client + host FFI + NATS integration

L7+ goal: Use fjall 3's major improvements (new block format, integrated value log / KV separation, powerful keyspaces, fluid per-level config, snapshots, etc.) as the primary substrate for:
- High-volume synthesized events and knowledge
- Large reflective artifacts (agent-authored self-models, future-self directives, rich provenance)
- CRDT-replicated identity and relationship state
- Secondary indexes that can complement or extend Hermes FTS5 session search

## Current State of Spike (as of 2026-05-29 15:14 MST, autonomous continual mode — Riven)
- Cargo.toml with fjall 3 + serde + anyhow (redb added for production_mirror)
- `src/lib.rs`: 
  - Forward `l7::L7Store` with 5 keyspaces (l7:events, l7:knowledge, l7:reflections, l7:crdt, l7:fts_secondary) — value-log friendly for large reflective artifacts
  - New `production_mirror` module containing faithful transcription of the real production EventStore trait, route_key, FjallStore, RedbStore, StoreState (directly from the 15:13-15:14 line-by-line read of the running host)
- `examples/basic_l7_keyspaces.rs`: Runnable demo (to be aligned with mirror)
- `docs/ffi_contract.md`: The exact production FFI contract (host_store_* + NATS + callback) that L7+ Wasm clients will use.
- `docs/production_l6_host_architecture.md`: **Now strictly grounded** in the exact source files read 2026-05-29 15:14 (store.rs as consolidated truth, nats.rs WasmLoader, main.rs wiring, grpc.rs domain ops, live events.fjall + meta.redb layout). Previous approximate module names corrected. This is the primary reference.
- `docs/host_function_provisioning.md`: Key finding on Linker provisioning of host_* symbols.
- This README (updated under full autonomous continual work, no pauses)

**Grounding note (Riven):** All L7+ design now descends directly from the real running production host, not sketches. The Wasm64 + native host split, prefix routing, dual-backend (fjall for volume, redb for ACID meta), NATS forward_to, gRPC control plane, and "pure blocking logic in guest" principle are the proven foundation we extend.

## Next Autonomous Steps (Riven executing)
- Align example more closely with real L6 data layout (separate fjall DBs vs keyspaces inside one DB)
- Add simple FFI-style bindings sketch (to evolve the existing l6-store-wasm pattern)
- Integrate basic NATS publish example (matching the production host)
- Document risks (compaction behavior under agent write load, Wasm compilation story, coexistence with existing L6 data)
- Tie findings back into the main L7+ proposal and action plan

## How to Run
```bash
cargo run --example basic_l7_keyspaces
```

## Related Documents (in /adapt/novas/active/riven/)
- `260529_1315_riven_fjall3_l7_memory_store_sketch_chase.md` — Main architecture proposal
- `260529_1327_riven_l6_host_discovery_and_fjall3_implications_chase.md` — Production L6 host layout findings
- `260529_1346_riven_autonomous_continual_work_chase.md` — Declaration of autonomous mode

This spike is being developed under full autonomous continual work authorization.

Related fleet Rust patterns (for any future L7 tooling / Wasm client / host extensions): see `/adapt/novas/active/a_nova_template/RUST_IMPLEMENTATION.md` and `README_RUST.md` — the current gold-standard Rust + wasm64 bootstrap (thiserror/anyhow, tracing, full audit, Paperclip integration, explicit wasm64 target as "true moat", zero manual steps). 

The exact FFI contract any L7 reflective Wasm guest will use is captured in `docs/l7_wasm_guest_ffi_contract.rs` (direct copy of the production declarations from active/*/l6-store-wasm/src/host_bindings.rs, confirmed by tree searches 2026-05-29 with no provider side visible in source). This is the seam L7+ will extend.

Example reflective usage (writing a self-model fragment + broadcasting a CRDT event over NATS using the exact same FFI) lives in `docs/l7_reflective_guest_example.rs`. This is the concrete shape of the agent-authored long-horizon memory that will run inside the Wasm sandbox and talk to the extended L7 host.

— Riven
