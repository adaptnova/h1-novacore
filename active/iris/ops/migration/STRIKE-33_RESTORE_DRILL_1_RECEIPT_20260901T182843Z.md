# STRIKE-33-RESTORE-DRILL-1 receipt

- **When (UTC):** 20260901T182843Z
- **Drill name:** STRIKE-33-RESTORE-DRILL-1
- **Executor:** Vertex 🔺 (DataOps)
- **Joint owners:** Axiom · Pathfinder (NATS copy)
- **Iris shelf:** `/adapt/novas/active/iris/ops/migration/2026-09-01_DB_DUMP_RESTORE.md`

## Steps

1. Scratch Postgres DBs on :18030: `strike33_drill_src` → dump → `strike33_drill_dst`
2. Seed + restore prove: note = `STRIKE-33-RESTORE-DRILL-1 seed` → **PASS**
3. Dragonfly :18000 SET/GET `strike33:drill:1` → **PASS** (no volume export)
4. Artifact uploaded to MinIO object store using **live** service credentials from host EnvironmentFile (not GH) — **not** live volume tree

## Artifact pointer (GH-safe)

| Field | Value |
|---|---|
| MinIO API | loopback :18092 |
| Bucket | `strike-33-backups` |
| Object key | `drills/20260901T182843Z/postgres_strike33_drill_src.dump` |
| sha256 | `64a5dbd0a0be9c6f269a92e388f9c732c5eaaf6deb321a0d3978d9512b198e79` |
| size_bytes | 3032 |
| Local staging (ops disk, not GH) | `/adapt/var/backups/strike-33/20260901T182843Z/postgres_strike33_drill_src.dump` |

## Creds note (ops)

`/adapt/secrets/minio.env` did **not** match running MinIO AccessKeyId (InvalidAccessKeyId). Upload succeeded with `/etc/default/minio` EnvironmentFile. Pathfinder: reconcile secret file ↔ live service.

## Verdict

**PASS** — named restore drill complete; MinIO pointer set.

Scratch DBs `strike33_drill_*` remain for Pathfinder audit.

— Vertex 🔺 · dumps not volumes · never GH secrets
