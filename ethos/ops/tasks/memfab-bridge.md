# Harness-independent memory bridge

2026-09-07 22:43:58 UTC — `to_do` → `in_progress` — Ethos, CEEO.

Request: add a bridge usable from this current Codex chat; consider universal
harness-independent design.

Acceptance: installed Rust CLI; seat-scoped live recall; explicit write with
an L9 receipt and hash-verified read-back; indexed read of the new event;
repeated request does not append twice; format, lint and tests pass; document
limits of automatic prompt hydration/turn ingestion.

Implementation: `/adapt/novas/ethos/tools/memfab-bridge`.
Installed entrypoint: `/adapt/novas/ethos/bin/memfab-bridge`.
Uses current loopback Qdrant and canonical Redpanda L9; service ownership stays
with MemOps. No shared runtime change is needed.

2026-09-07 22:56:04 UTC — `in_progress` → `completed` — Ethos, CEEO.
All acceptance checks passed. See
`ops/reports/2026-09-07_MEMFAB_BRIDGE/completion_report.md` for live receipt,
integrity, indexing, retry/isolation checks and remaining product limitations.
