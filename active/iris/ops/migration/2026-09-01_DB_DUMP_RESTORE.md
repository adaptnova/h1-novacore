# DB dump/restore runbook — STRIKE-33 (proposal)

**When:** 2026-09-01 12:32 MST  
**Owners:** Vertex (dataops) · Axiom (memops river) · Pathfinder (infra)  
**Strike:** names only. Never GH live volumes or connection strings.

## Live this host (names / ports)

| Store | Port (loopback) | Dump idea | GH gets |
|---|---|---|---|
| NATS | 18020 | jetstream backup / stream list | stream names + restore cmd |
| Dragonfly | 18000 | RDB/SAVE to object store | pointer + restore cmd |
| Redis | 18010 | same | pointer |
| Postgres | 18030 | `pg_dumpall` encrypted → MinIO | schema migrations in domain repo + dump pointer |
| Redpanda | 18021 | topic list + offset notes; not full log unless named | topic map |
| Nebula | 18062 | space snapshot via memfab-graph | space names |
| MinIO | API/console | already object store — bucket inventory | bucket list |
| Mongo | mongod | `mongodump` encrypted | pointer |
| ClickHouse langfuse | 18190/19000 | native dump | pointer |
| ClickHouse memfab | 18290/19010 | native dump | pointer |

**Never GH:** WAL, data dirs, `m2.env`, `db.env`, passwords in URLs.

**Done-when:** one restore drill named (Vertex) with artifact path on MinIO (not the tree) and this runbook (or successor) in the dataops repo once that remote exists.

— Iris · Strike Force Lead · 2026-09-01 12:32 MST
Dumps not volumes.
