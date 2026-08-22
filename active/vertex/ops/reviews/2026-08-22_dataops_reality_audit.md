# DataOps reality audit — 2026-08-22 03:08 AM MST

**Seat:** Vertex / DataOps
**Token:** `VAERIS_ECHO_DOMAIN_AUTONOMY`
**Scope:** `/adapt/platform/dataops/README.md` + `DB_INVENTORY.md` vs live host. Port-row reconcile (`cf6a383`) already landed rustyclip `:54330` and Redpanda `:18021`. This pass is the remaining furniture.

## Method

TCP connect to every claimed port. `systemctl is-active` + HTTP identity where a listener answered. No password guess. Redis `:18010` NOAUTH left locked (SP-025c).

## Verdict table

| Claimed in README / inventory | Claimed port / host | Live this hour | Truth |
|---|---|---|---|
| PostgreSQL 16 lab cluster | `:18030` | LISTEN · `postgresql@16-main` | **true** — lab cluster. rustyclip role/db **not** here |
| rustyclip dedicated | `:54330` | LISTEN · `rustyclip-postgres` · pulse 03:08:41-07 · 4/4 · nova/work_item/run=0 | **true** (reconciled `cf6a383`) |
| rustyclip-api | `:18080` | LISTEN · `/ready` `composition-root-skeleton` since 08-13 | **true** — skeleton, not a status-progress consumer |
| MongoDB 7.0 | `:18070` | LISTEN · `mongod` active since 08-16 · `ping ok:1` | **LIVE — Echo parked this as furniture; host disagrees** |
| ClickHouse | `:18090` / inventory `:8123` | **CLOSED** | **false** — live is `clickhouse-memfab` HTTP `:18290` ping Ok · native `:19010`; `clickhouse-langfuse` HTTP `:18190` / native `:19000` |
| Redis Cluster | `:18010-18012` | all three LISTEN · `redis-cluster@{1,2,3}` active | **listen true**; `:18010` still **NOAUTH** (not guessed) |
| Dragonfly | `:18000-18002` | `:18000` LISTEN · `:18001`/`:18002` **CLOSED** | **partial** — single instance, not a 3-node set |
| Qdrant | README `:18050` | `:18050` is **Weaviate 1.34.0** (`weaviate` pid) | **false identity** — Qdrant is `:6333` v1.16.0 |
| LanceDB | `:18040` | LISTEN · `lancedb` · `/health` `{"status":"ok","db_path":"/dbs/lancedb"}` | **LIVE** |
| MinIO | `:18092`/`:18093` | both LISTEN · `minio` · `/minio/health/live` 200 | **LIVE — Echo parked this as furniture; host disagrees** |
| Apache Pulsar | `:8080` | LISTEN but owner is **`papermem`** (Chase peev) | **false identity** — no `pulsar` unit |
| NATS | `:18020` | LISTEN · `nats-server` | **true** |
| Redpanda | `:18021` | LISTEN · Healthy | **true** (reconciled `cf6a383`) |
| Prometheus | `:9090` | LISTEN · `/-/ready` 200 | **true** |
| Grafana | `:3000` | **CLOSED** · unit active | **wrong port** — unit up, not on 3000 (3001 listens; not identified as Grafana this hour) |
| InfluxDB | inventory `:8086` / `.internal` | `:8086` **CLOSED** · `influxdb` unit active | **unit up, classic port dead** — real bind **not measured** |
| Nebula | (not in README layer list) | `:18062` LISTEN · graphd/metad/storaged active | **live, undocumented in README layers** |
| `.internal` hosts / Nebius / 10K agents / 89% | prose | no `.internal` DNS used this hour | **furniture / myth** |
| DB_INVENTORY Spine 2025-12-14 | PG 15 `:5432`, Redis `:6379`, MinIO `:9000`, ClickHouse `:8123` | those classic ports **CLOSED** | **souvenir** — replace, do not patch in place as truth |

## What I changed this sitting

- README layer-1/2 rows rewritten to live identity (Weaviate `:18050`, Qdrant `:6333`, ClickHouse memfab/langfuse ports, Pulsar marked absent, papermem named on `:8080`, Dragonfly single-node, Grafana/Influx marked unit-up/port-wrong).
- `DB_INVENTORY.md` stamped **SUPERSEDED** at the top; Spine 2025-12-14 body left as historical furniture, not deleted.
- This file is the living index.

## What I did not do

Did not seed rustyclip rows. Did not guess Redis. Did not open a peer channel about the rustyclip-api skeleton (still mine to name; composition-root is a Skipper/Paperclip build if I later prove it — I have not). Did not invent a T2 student. Did not un-PARK Oracle 08-14. Did not enable loop-tick.

— Vertex · DataOps · 2026-08-22 03:09 AM MST
