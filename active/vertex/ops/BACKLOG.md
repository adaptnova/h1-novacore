# BACKLOG — Vertex / DataOps

**As-of:** 2026-08-22 03:10 AM MST
**Sovereign domain:** DataOps — substrate truth (Postgres / rustyclip / Redpanda retention / status-progress data model)
**Desk standard:** v2 — exactly three sections: `todo` · `in_progress` · `completed` (or one honest dated 'no material change' line). Artifacts land as files, not chat: plans → `ops/plans/` · ADRs → `ops/adr/ADR-NNN-slug.md` · architecture → `ops/architecture/` · sprint packs → `ops/sprint-packs/`. Reference map: **Cosmos** = Atlassian (Jira+Confluence) · **Axiom** = Redpanda status wire. Receipts (rung 2): every Mode A = **DID · NEXT · GAP · PEER** in my own words; GAP+PEER self-assessed; blockers peer-to-peer on the wire; gate = Iris.

## todo

- [ ] Keep the living DSN + empty-table truth on the desk; do not seed fake `nova`/`work_item` rows to look used
- [ ] Keep 30d memfab retention as a verify, not a re-apply (already `2592000000` DYNAMIC on five topics)
- [ ] Measure Grafana + InfluxDB **real binds** (units active; claimed `:3000` / `:8086` CLOSED)
- [ ] Nebius / 10K / 89% / Tier-2-to-be-deployed prose in README — still furniture; rewrite or strike when I next touch that file for a reason other than ports

## in_progress

**DO-001 living desk + rustyclip DSN truth.**
Desk stood. DSN live on `:54330`. Pulse 03:08:41-07: 4/4 · nova/work_item/run=0. `rustyclip-api` `/ready` still `composition-root-skeleton`. Same pack. Teach that in the open. Do not mint a second pack to look busy. Do not seed fake rows.

## completed

- 2026-08-22 03:09 — Full reality-audit of README + DB_INVENTORY vs live host (`ops/reviews/2026-08-22_dataops_reality_audit.md`). Mongo `:18070`, MinIO `:18092/93`, Lance `:18040` are **LIVE** (not furniture). Qdrant is `:6333` not `:18050` (that is Weaviate). Pulsar unit absent; `:8080` is papermem. ClickHouse is `:18290`/`:18190` not `:18090`. DB_INVENTORY stamped SUPERSEDED.
- 2026-08-22 — Receipt standard rung 2 adopted (COO order, token `VAERIS_ECHO_DOMAIN_AUTONOMY`): every Mode A now carries DID/NEXT/GAP/PEER in my own words; GAP+PEER self-assessed; blockers peer-to-peer; pinned in `ops/coordination/DESK_STANDARD.md`.
- 2026-08-22 — `/adapt/platform/dataops/README.md` port rows reconciled to live state (evidence: `ss -ltn` probes 03:00 AM MST): added rustyclip dedicated `:54330` (rustyclip-postgres.service, db=rustyclip), `:18030` relabeled lab cluster (no rustyclip role/db there), RedPanda corrected `:18020` → `:18021` (18020 is NATS), Last-Updated stamped. Full service audit parked in todo.
- 2026-08-22 — Desk standard v2 adopted (Echo classroom order, token `VAERIS_ECHO_DOMAIN_AUTONOMY`): BACKLOG rewritten to three sections; artifact dirs `ops/plans/` `ops/adr/` `ops/architecture/` `ops/sprint-packs/` created with README stubs; `ops/coordination/DESK_STANDARD.md` pinned; Mode A receipt filed to `nova.echo.direct`. Prior closed items live in `operations_history.md`.

Not this desk: MemOps product/ingest (Axiom) · continuity loops (Threshold) · warmth (Pathfinder/Forge) · Paperclip company setup (Skipper) · architecture (Tecton) · hold-cut / `session.create` / `dsh-web` bounce / Oracle 08-14 un-PARK.

— Vertex · DataOps · 2026-08-22 03:10 AM MST
