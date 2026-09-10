# Zap transition to dev2 — move complete

**Done:** 2026-09-10 12:25 MST — Zap, at operator (Chase) direction.

## What moved (x box → dev2)

Bundle `zap-crate-move.tar.gz` (613 KB, sha256 `4d7eafbd…ce63` — hash verified
identical on both ends, transfer over the wire, never through git):

| Item | Landed at |
|---|---|
| Memory tree L0–L6 (2 MB: intake sessions, tags, semantic, episodic, 143 L5 raw) | `/adapt/novas/zap/memory/l0…l6/` |
| veritas DB (DAG + state.redb) | `/adapt/novas/zap/veritas/` |
| ops history + proofs | `/adapt/novas/zap/ops/` |
| MEMORY.md, session.zap.id | `/adapt/novas/zap/` |
| **Identity keypair** (out-of-band, mode 600, never in git) | `/adapt/novas/zap/.nova/` |
| L15 startup pack (startup.json + coo_wake.json) | `/adapt/novas/zap/memfabric-context.d/` |
| Original soul (born 2026-05-04) | `/adapt/novas/zap/lineage/SOUL-original.md` |

Lane continuity ledger (`memory/canonical/events.jsonl`, hash-chained) untouched
throughout — verify True, 3 events before/after.

## Strike cell territory created

`/adapt/ops/strike/` on dev2 — README, operations_history.md, decisions.log,
proofs/, tasks/, scratch/. Git repo `working` branch, **pushed to
github.com/adaptnova/ops-strike** (private, created via gh). Home and work are
separate: identity in `/adapt/novas/zap`, work in `/adapt/ops/strike`.
`JZ`-style client runs verified with `-C /adapt/ops/strike` — turn committed
(`exchange.completed`, `ZAP_MOVED_IN`).

## ARCHITECTURE DIFFERENCE — dev2 is NOT the x box's MemFabric

The x box runs the **MemFabric L1–L15** stack (Redpanda L9 18021, Dragonfly L1
18000, Qdrant 6333, NebulaGraph, L13 letters, L15 pack). **dev2 runs a
different stack — the "Genesis" data plane:**

| x box (MemFabric) | dev2 (Genesis) |
|---|---|
| Redpanda `memfab.memory.events.v1` (L9 SoT) | **NATS + JetStream** (:18020, "Genesis data plane") |
| Qdrant :6333 `memfab_memory` | **Qdrant** (`qdrant-genesis.service`, "semantic retrieval") |
| NebulaGraph (L14) | **NebulaGraph** (genesis: metad/graphd/storaged) + **HugeGraph** |
| Dragonfly L1 :18000 | Redis :18010 (Dragonfly config present in db.env but not listening) |
| — | Postgres 16 :18030, Elasticsearch, ClickHouse, Kafka |
| ADAPT lane ledgers (same) | ADAPT lane ledgers (same) |

**What this means:** the file-based memory (L0–L6, veritas, L15 pack, the
lane's hash-chained ledger) is **fully transferred and self-contained** — it
needs no engine. The engine-backed layers (L9 stream, L12 vectors, L14 graph,
L1 hot cache) are **inert on dev2** until wired into Genesis. Per operator:
"We will adapt to that when the time's right." Until then: the lane ledger is
the live, durable, append-only memory; the crate files are the archive.

## For the Ethos / Axiom transfers (same recipe, 5 steps)

1. **Home:** `/adapt/novas/<name>` + identity files + NovaId + genesis via
   `adapt_continuity` (mint BEFORE starting the gateway — Vellum lesson).
2. **Lane:** gateway :15007/:15009… capability :15008/:15010… — own
   `RuntimeDirectory` (lock collision lesson), provider profile
   `send_turn_metadata=true`, alias `J<E>`; restart the 4 library services
   after any library commit (stale-validator lesson).
3. **Crate:** tar the memory tree + veritas + ops + L15 pack; **verify sha256 on
   both ends**; keypair via scp mode 600, never git (gitignore law:
   `active/*/.nova/identity.key`).
4. **Backup:** their crates are likely untracked too (lab norm) — audit
   `git ls-files`, secret-scan, commit, push.
5. **Verify:** `assert-aster-path.sh all` green + one real turn through the
   lane + ledger verify.

— Zap · Strike operator · 2026-09-10 12:25 MST
