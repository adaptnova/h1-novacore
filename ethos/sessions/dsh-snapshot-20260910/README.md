# DSH session snapshot — 2026-09-10

Source: `/adapt/ops/deepseek-harness/sessions/--adapt-novas-ethos--/`
(16 MB total, **not** in any git repo — that directory is not versioned at all.)

Captured as a one-time backup so my session history survives the box.

## What is here

5 **closed** sessions, `session.jsonl.zstd` each, 14 MB total:

| Session | Size |
|---|---|
| `session-da6fb6dc-…-0514c5da9f3a` | 11 MB |
| `session-e43376fb-…-9f39e58a06f4` | 1.6 MB |
| `session-fa1f66b2-…-e1118a2c7e93` | 614 KB |
| `session-6f442ff9-…-774dad0d5813` | 35 KB |
| `session-cd51483a-…-58ea7c2fcd80` | 390 B |

## Deliberately NOT here

**`session-3b6dfef2-0c35-47a8-90f1-a120d0c40afd` — this session, live.**
It was being written at the second I snapshotted (`DSH_SESSION_JSONL` points at
it). Copying a live compressed transcript yields a truncated, unreadable blob.
Skip it; snapshot it after it closes.

## Caveats

- **DSH is not going to dev2** (Chase: harness too immature). So these are
  *history*, not a working restore path. Readable by decompressing:
  `zstd -d session.jsonl.zstd` → JSONL.
- **Secret scan:** clean — no credential shapes, no known secret values.
  Session transcripts were the likeliest place for leaked credentials, so this
  was checked before committing, not after.
- These are **zstd blobs in git** — 14 MB, permanently in history, not
  diffable. Accepted as a one-time cost; do not re-snapshot every session.
- Only `*.zip` is LFS-tracked in this repo, so these are plain blobs.

## Refresh

Re-snapshot after sessions close, never while live.

*— Ethos · CEEO / AIML T1 · 2026-09-10*
