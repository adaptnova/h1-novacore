# Qdrant memory export — Ethos

**Why this exists.** My memory is not only files. `memory/l0`–`l5` are the file
layers, but the **vector index lives in Qdrant** (`http://127.0.0.1:6333`,
collection `memfab_memory`, filtered `agent_id == "ethos"`). A live database is
not in git, so on a fresh box I would have files but no recall.

This export closes that gap.

## Contents

| | |
|---|---|
| File | `memfab_memory.ethos.jsonl` |
| Points | **159** (of 37,191 in the collection) |
| Vectors | **included**, 1024 dims — restorable without the embedder |
| Size | 3.3 MB |
| Exported | 2026-09-10 · commit follows this one |
| Secret scan | clean — no credential shapes or known secret values |

Each line is one Qdrant point: `id`, `vector`, and full `payload`
(`content`, `event_id`, `event_type`, `memory_kind`, `redpanda_topic` /
`_partition` / `_offset`, `salience`, `trust_score`, hashes).

## Source of truth

These points are **projections** of Redpanda `memfab.memory.events.v1`
(L9). Each payload carries its `redpanda_partition` / `redpanda_offset`.
Qdrant is rebuildable from Redpanda **only while Redpanda retains the events** —
that retention is why this export exists.

## Restore on dev2

```bash
python3 - <<'PY'
import json, urllib.request
pts=[json.loads(l) for l in open("memory/qdrant-export/memfab_memory.ethos.jsonl")]
for i in range(0, len(pts), 50):
    body={"points":[{"id":p["id"],"vector":p["vector"],"payload":p["payload"]}
                    for p in pts[i:i+50]}
    r=urllib.request.Request(
        "http://127.0.0.1:6333/collections/memfab_memory/points/upsert",
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    print(json.load(urllib.request.urlopen(r, timeout=60))["status"])
PY
```

**Do not blind-upsert.** Check first whether the target already has these points:

```bash
curl -s -X POST http://127.0.0.1:6333/collections/memfab_memory/points/count \
  -H 'Content-Type: application/json' \
  -d '{"filter":{"must":[{"key":"agent_id","match":{"value":"ethos"}}]},"exact":true}'
```

If it returns 159, the box already has my memory — do nothing. If it returns a
different number, **stop and ask Chase** before writing; a mismatch means the
target has its own state, and I am not going to overwrite a live memory store
the way I nearly overwrote a shared `config.toml`.

## Refresh

Re-run the export (see git log for this directory's first commit) after any
significant memory event. The export is a **snapshot**, not a live mirror.

## What is still NOT backed up

- **Redpanda L9** itself — the upstream event log. Retention-bounded.
- **Dragonfly / Redis streams**, **PostgreSQL** — other seats' infra, not mine
  to dump.
- **`memfab_memory` points for other agents** — deliberately excluded. I only
  exported `agent_id == ethos`.

*— Ethos · CEEO / AIML T1 · 2026-09-10*
