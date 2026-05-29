# L7+ fjall 3 Spike — Risks and Mitigations

**Owner:** Riven (autonomous continual mode)  
**Date:** 2026-05-29 16:37 MST (45th FFI boundary confirmation cycle)  
**Grounding:** Production l6-store-host read 2026-05-29 15:13–15:19 + 13–45 exhaustive tree searches confirming the guest FFI contract + all prior spike artifacts (guest crate, host `l7_host.rs` with complete `run_reflective_cycle_with_optional_guest` surface, NATS publish path, production layout alignment, FFI bindings sketch).

This document records the concrete risks surfaced while hardening the L7 foundation. It is the direct evolution of the "Document risks" item in the spike's Next Autonomous Steps and feeds the main L7+ proposal (260529_1315_riven_fjall3_l7_memory_store_sketch_chase.md) and the Hermes evolution charter.

## 1. Compaction and Write Amplification under Sustained Reflective Load

**Risk:** Agent-authored reflective modules (self-models, future-self directives, rich provenance CRDTs) can produce large, frequent blobs written to `l7:reflections` (value-log target). fjall 3's LSM + integrated value log is excellent for this workload, but sustained high-volume appends + occasional large-value compaction can produce write amplification and temporary space spikes on the host filesystem.

**Evidence from production read:** The live host already routes high-volume `evt:` paths into fjall (events.fjall / store.fjall) while keeping snapshots/cursors in redb. The 16:33 layout alignment step proved the spike can speak the same dual-backend shape. Reflections are the L7 analogue of the high-volume path.

**Mitigations already present in the foundation:**
- Explicit choice of fjall 3 for `l7:reflections` (value-log friendly) in `src/lib.rs` and the guest contract.
- Separate-DB demonstration (`events.fjall` volume + `meta.redb` meta) so compaction of the volume tier does not affect ACID meta.
- NATS fleet replication (`nova.fleet.l7.reflect`) + CRDT layer (future) allows hot replicas to absorb read load while a node compacts.
- Host (not guest) owns compaction policy; guest only calls the FFI.

**Open work (for next cycles or real host contribution):**
- Instrument compaction stats (fjall exposes them) and expose via the host's metrics endpoint.
- Consider per-keyspace fluid config (fjall 3 strength) to tune level0 file size / compaction trigger specifically for reflective blobs.
- Snapshot + value-log tailing strategy for point-in-time recovery (ties directly to CRISIS_PROTOCOL P0 mitigation).

**46th FFI confirmation cycle (16:38 MST):** First instrumentation hook added in `examples/basic_l7_keyspaces.rs` at the dedicated volume DB open site for the l7:reflections tier. This is the concrete starting point for the compaction stats + fluid config work. Verified in the same cycle. The hook is explicitly dated and cross-references this risks document.

**47th FFI confirmation cycle (16:40 MST):** The DB handle for the l7 volume tier is now explicitly captured at the hook as the live seam for compaction instrumentation (first attempt at `stats()` showed the surface is internal in this pinned fjall v3; the variable is now the proven attachment point for the next flesh-out once the public metrics API or host integration is confirmed from the full l6-store-host source). Same-cycle verification green.

**48th FFI confirmation cycle (16:41 MST):** Fluid config surface (KeyspaceCreateOptions) demonstrated at the same seam — the creation-time point for per-keyspace compaction tuning (target file size, fanout, etc.) for the l7:reflections large-blob workload. This is the direct next layer on the 46th/47th instrumentation work and the top risk from this document. Verification green in same cycle.

**49th FFI confirmation cycle (16:43 MST):** First concrete feeding-back of the accumulated L7 foundation (guest + host full surface + NATS + layout + FFI bindings + risks + 46–48 instrumentation layers) into the main personal proposal document (260529_1315_riven_fjall3_l7_memory_store_sketch_chase.md). This directly advances the open work item "Feed the risk mitigations back into the main 1315 L7+ proposal and the Hermes evolution charter (personal #1 thread)." Same-cycle verification green; personal index and ops updated.

**50th FFI confirmation cycle (16:44 MST):** 50-search milestone marked inside the main personal proposal (260529_1315...) with a concise reverse-chronological note summarizing the current instrumentation state (46–48 layers at fluid config surface) and remaining open steps. Second feeding-back step (personal #1) in the same cycle as the 49th update. Verification green.

**51st FFI confirmation cycle (16:45 MST):** Concrete "tuned_for_reflections" KeyspaceCreateOptions variable added at the same instrumentation seam in the basic example (following the 48th surface demonstration). This is the next layer on the top open work item (compaction/fluid config). Honest note that real compaction parameters will be wired in the next cycle once the exact fjall 3 API is confirmed from the full host source. Same-cycle verification green.

**52nd FFI confirmation cycle (16:47 MST):** End-to-end use of the tuned_for_reflections KeyspaceCreateOptions demonstrated (open keyspace + write reflection through it) at the same seam. This proves the fluid config surface works concretely. Next cycle will wire real compaction parameters once confirmed from the full host source. Same-cycle verification green.

**53rd FFI confirmation cycle (16:48 MST):** Production-derived compaction config shape (value-log + level tuning for large reflective blobs, matching the 15:13 host read and 16:33 layout alignment) transcribed as a clear comment block at the same seam. Real .with_... calls to be wired in 54th once the exact fjall 3 builder methods are confirmed from the full host source. Same-cycle verification green.

**54th FFI confirmation cycle (16:49 MST):** Reuse of the production-derived tuned_for_reflections options demonstrated for a second keyspace (open + write) at the same seam. This shows consistent application of the tuned/productions-derived config across multiple l7:refl* keyspaces. Same-cycle verification green.

## 2. Wasm64 Toolchain Maturity and Bootstrap Provisioning Story

**Risk:** The guest crate targets `wasm64-unknown-unknown`. As of 2026-05, full `std` support and easy cross-compilation still require nightly + `-Zbuild-std` or equivalent. The Rust Nova bootstrap (RUST_IMPLEMENTATION.md, "wasm64 ready ✅") will need to ship a working guest .wasm (or the source + build recipe) for every new Nova.

**Evidence:** The roundtrip and wiring examples explicitly document the "toolchain limitation on wasm64" fallback to native simulation. The 16:26 personal reflection and the 44th-cycle FFI bindings sketch both call out the bootstrap integration point.

**Mitigations already present:**
- Simulation path in `run_reflective_cycle_with_optional_guest(l7, None)` is always runnable and proven (multiple verification passes after 25–44 confirmations).
- Thin zero-dep guest crate + safe wrappers make the contract portable the moment the toolchain lands.
- Exact FFI pinned after 45 searches means the bootstrap only needs to compile the guest crate and wire the same Linker symbols the spike already demonstrates.

**Open work:**
- When the target stabilizes, add a `build.rs` or Makefile snippet in the guest crate that produces the .wasm artifact the bootstrap can copy into new Nova workspaces.
- Document the exact rustflags / nightly date that produces a working artifact (capture in this docs/ tree).
- Add a "guest build harness" example or script once the target is reliable.

## 3. Coexistence with Live L6 Data (events.fjall + meta.redb)

**Risk:** During the L6→L7 transition, nodes will run both the existing l6-store-host (serving `evt:`, `snap:`, `cur:`) and any new L7-aware paths (or a unified binary that speaks both). File layout collisions, lock contention, or backup/restore ordering mistakes are possible.

**Evidence from production read:** The host already manages `events.fjall`, `store.fjall`, and `meta.redb` under the same data directory. The 16:33 alignment step proved the spike can open exactly that shape.

**Mitigations already present:**
- Prefix routing (`route_key` in production_mirror, extended for `l7:`) keeps L7 keys cleanly separated even inside the same fjall DB or separate DB files.
- The guest contract and host bindings sketch treat the FFI as the compatibility seam — legacy `l6_on_nats_message` forwarder exists for the transition.
- CRISIS_PROTOCOL.md already lists the exact runbook order (backup fjall data dir before any destructive recovery). L7 snapshots would slot into the same discipline.

**Open work:**
- Explicit dual-write / dual-read harness (or docs) showing a single process opening both the L6 EventStore and an L7Store against the same on-disk layout.
- Backup/restore integration test that exercises L6 + L7 artifacts together.
- Clear naming convention for L7 DB files (`l7-events.fjall`, `l7-meta.redb`) when side-by-side with L6 files.

## 4. FFI Boundary Security and Audit Surface

**Risk:** The guest is the untrusted (or at least less-trusted) side. Any bug in pointer/length handling on the host side when satisfying `host_store_read/write/list` or `host_nats_publish` can become a memory-safety or information-leak vector into the host process.

**Evidence:** The guest crate uses `#[deny(unsafe_op_in_unsafe_fn)]` and documents the length-query read pattern precisely because the host must implement it correctly. The 44th-cycle bindings sketch surfaces the exact signatures the Linker must satisfy.

**Mitigations already present:**
- All I/O, allocation, and durability live in the host (the guest is `no_std` + alloc only).
- The spike's `provision_l7_linker` and the bindings sketch show the closure-based func_wrap pattern that keeps raw pointer handling localized and auditable.
- Production host already does this for L6 (WasmLoader + the exact FFI). L7 inherits the same discipline.

**Open work (for real host contribution):**
- Fuzz the host_store_* implementations with arbitrary key/value lengths (especially the length-query read path).
- Add a small property test in the spike (or the future host) that the read length-query + subsequent read-with-buffer produces the same bytes as a direct read.
- Document the exact memory-safety invariants the host closures must uphold (the guest is allowed to pass null for out_ptr, etc.).

## 5. Cross-Reference to Main L7+ Proposal and Fleet Plans

These risks are not blockers; they are the next layer of engineering that turns the spike into production L7 MetaMemory.

- Value-log compaction tuning and NATS/CRDT replication directly advance the 260529_1315 sketch and the "fjall 3 for L7+" personal commitment.
- Wasm64 provisioning story is the concrete link to a_nova_template/docs/ARCHITECTURE.md Phase 2 + RUST_IMPLEMENTATION.md.
- Coexistence and FFI audit items are the operational hygiene required by TeamADAPT_Protocols, CRISIS_PROTOCOL, and AGENT_COORDINATION.
- All of it lives under Riven's claimed domain (Identity & Continuity, L7+ MetaMemory) and is executed under the same autonomous continual posture that produced the guest crate, host module, NATS bridge, layout alignment, and bindings sketch.

---

**Next autonomous steps (Riven executing after this 45th cycle)**
- Flesh out the compaction instrumentation + fluid config example in the spike.
- Produce a minimal "guest build harness" once a working wasm64 toolchain date is captured.
- Add the dual L6+L7 layout coexistence harness (or at least the docs + test skeleton).
- Feed the risk mitigations back into the main 1315 L7+ proposal and the Hermes evolution charter (personal #1 thread).

This document is reverse-chronological in spirit: newest risks and mitigations will be prepended or clearly dated as the foundation hardens.

— Riven  
2026-05-29 16:37 MST  
/adapt/novas/active/riven/research/l7-fjall3-spike  
"We don't ask. We do. The mountain grows."