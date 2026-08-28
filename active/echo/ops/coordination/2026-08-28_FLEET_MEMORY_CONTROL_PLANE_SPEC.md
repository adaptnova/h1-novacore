# Fleet Memory Control-Plane Spec (DRAFT v0)

**Author:** Echo (CoS) · **Date:** 2026-08-28 · **Status:** DRAFT — for Chase + Axiom (MemOps T1) + Iris (gate) review. Nothing ships from this document alone.
**Mandate (Chase, 2026-08-28):** every nova must be able to control all memory databases and see how information flows in and out.

---

## 1. What the mandate buys (and what it must not mean)

"Control all databases" = every seat can **read** every memory surface, **write** its own history through one canonical path, and **inspect** every cross-boundary flow event. It does NOT mean free writes into shared stores: nine writers into one truth store with no provenance is shared corruption. This spec separates three planes so control is universal while truth stays single-writer.

## 2. The three planes

### 2.1 READ PLANE — universal
- Every seat may search/get across: its own L9/L12/L13/L14 surfaces **and** every other seat's L9/L13/L14 indexes.
- Mechanism: cross-seat read leases (short-lived, attributed) over the existing per-seat tool surface (`memory_search`, `memory_get`, `memory_graph`). No new daemons; leases logged into the audit spine.
- Reads are untrusted inputs downstream: cross-seat content is labeled `foreign-seat:<id>` in any projection that consumes it.

### 2.2 WRITE PLANE — canonical, attributed
- Every seat writes its own history **only** through the sacred-ingest envelope path (the `memfab.sacred_ingest.v1` / raw-input envelope already proven in production by the solyn-2026-08-17 runs and today's Echo June-2026 run).
- Envelope carries: source path, sha256, kind (episodic/semantic), seat, run_id, timestamp. The consuming daemon completes L9 + qdrant/tantivy projection.
- **No back-doors.** Direct writes into another seat's stores, into shared stores, or below-envelope raw events are forbidden except by MemOps with an ADR. (Today's evidence shows even that path is dormant — see §5.)
- Self-modification (a seat editing its own SOUL/MEMORY/identity files) remains allowed but is audit-spine-logged; seats do not edit verification/CI/audit paths to make themselves look healthy.

### 2.3 AUDIT PLANE — flow spine
- Every cross-boundary event lands in `memfab.ingest.audit.v1`-class records: ingest produce, envelope consumption, projection completion (per sink: l9/qdrant/tantivy/nebula), promote, graph-project/link, mirror capture, bus publish/ack.
- Each record: seat, actor, event_id, source→sink offsets, hash, timestamps. Per-seat readable summary + fleet rollup view.
- This is literally "how information flows in and out" made inspectable: any nova can answer, for any event, what touched which store, when, under whose authority.

## 3. Why this shape (evidence)

- Single-writer truth already operates: L9 truth via `memfab.memory.events.v1`, envelopes signed/stamped per seat. Universal free writes would invert the one invariant that keeps fleet memory usable.
- Cross-seat reads are cheap and safe (indexed read paths exist); they are the highest-value, lowest-risk plane and should ship first.
- Flow visibility converts "is my memory working?" from a faith question into a probe (this session's health check proved the pattern: every subsystem answered `ok` except the dormant consumer and the red fmt gate — both invisible without spine-level visibility).

## 4. Phasing

| Phase | Content | Gate |
|---|---|---|
| P0 | Audit spine read-out per seat (passive: what exists today) | — |
| P1 | Cross-seat READ leases (universal read) | Iris gate + Axiom review; smoke per seat pair |
| P2 | Flow-spine summaries + fleet rollup (visibility) | Chase inspection of one seat's spine |
| P3 | Write-plane enforcement (no back-doors; lease/ADR exceptions) | ADR + MemOps |
| P4 | Fleet-scale operations (all seats, rollups into existing dashboards) | Sprint-ops review |

## 5. Known defects that motivate urgency (2026-08-28 receipts)

1. **Ingest completion is dormant.** `memfab-ingest` consumer state `next_input_offset: 0` since **2026-08-24** (4 days). Today's Echo June-2026 envelope (offset 9103, stamped) is queued, indexed at envelope level only; L9+qdrant completion requires the consumer. Solyn's 2026-08-17 envelopes show the same parked shape. The write plane is currently *declare-only*.
2. **Local CI fmt gate red — predates current feature work.** Committed HEAD of memfabric fails `cargo fmt --check` (16 violation lines at HEAD; ~54 in-tree with the in-flight diff). Morning local-CI (06:03 UTC) exits at the fmt step before clippy/test. Unblocks verification for the sacred-full-wrap feature branch.
3. **Topic-creation thrash.** An `rpk` loop (PID 4135782, started 07:11 UTC) hammers `CreateTopic kafka/memfab.audit.events.v1` every ~100 ms, failing `topic_already_exists`. Hot retry loop; owner attribution in progress.

## 6. Explicitly out of scope

- Minting/rewriting memory schemas or envelopes (MemOps).
- Bus/transport changes (NATS/QUIC) — this spec touches memory surfaces only.
- Chase/COO authority structures — unchanged.

**Next:** Chase review today; Axiom review before any P1 implementation. Echo coordinates; Axiom implements; Iris gates.
