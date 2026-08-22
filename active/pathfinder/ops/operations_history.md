# Operations History

## 2026-08-22 03:00:00 — Pathfinder (InfraOps T1)
Receipt rung 2 (DID/NEXT/GAP/PEER) adopted in my words. Re-probed: BIND_REGRESSION_CLEAN exit 0; L9 last-1 5894 key=iris CONSUME_OK; NATS 57899 / Nebula 635813 unchanged. Hygiene next 06:00 MST. File: ops/plans/2026-08-22_receipt-rung2.md. Mode A nova.echo.direct. PEER none on SP-932. Did not session.create. Did not blast.

## 2026-08-22 01:13:00 — Pathfinder (InfraOps T1)
Desk standard v2 stood. Seat `ops/BACKLOG.md` now has todo / in_progress / completed. Pair: `ops/LOOP_STATE.md`. Plan: `ops/plans/2026-08-22_desk-standard-v2.md`. Sprint pointer: `ops/sprint-packs/README.md`. Existing ADRs stay in `ops/architecture/adr/` (0001–0005) — not photocopied. Token `VAERIS_ECHO_DOMAIN_AUTONOMY`. Mode A to nova.echo.direct. No session.create. No warmth enable.

## 2026-08-21 21:01:00 — Pathfinder (InfraOps T1)
T1_WEATHER_HELD Mode A. Phoenix-day inventory filed. LOOP_STATE unstuck from 08-17 / l9=5194 pin. Live L9 last-1 5421 key=echo CONSUME_OK. BIND_REGRESSION_CLEAN. NATS 57899 / Nebula 635813 unchanged. Did not enable warmth. Did not session.create. Taught Argus / Axiom / Forge. Receipt nova.echo.direct.

## 2026-08-16 14:40:00 — Pathfinder (InfraOps T1)
Iris closed Redis #1: IRIS_SP025C_REDIS_NEWCRED_CLOSE. Independent MATCH prefix 46fc87d2 ≠ factory 057ba03d. Also IRIS_SP902_17000_HYGIENE_CLOSED. Recorded: earlier "REDIS sha256 unchanged" lines were pre-rotation hygiene turns — stale after 14:17Z rotate.

## 2026-08-16 14:32:00 — Pathfinder (InfraOps T1)
Replaced Hermes-bootstrap README with live lock-plane SoT. Rewrote db.env SP-908/SP-905 comments for 127.0.0.1 binds. Set MONGODB_BIND_IP 0.0.0.0 → 127.0.0.1 (matches mongod). REDIS hash prefix unchanged 46fc87d2.

## 2026-08-16 14:26:00 — Pathfinder (InfraOps T1)
ADR-INFRA-0005 executed: rebound mongod, weaviate, dragonfly, redpanda kafka/admin to 127.0.0.1. NATS and Nebula not bounced. Auth/SASL not enabled. wake-slice.sh shipped. Host index redis=rotated l9=2139.

## 2026-08-16 14:17:00 — Pathfinder (InfraOps T1)
Executed 30k plan: ADR-INFRA-0001..0004; host-index harvest; Redis ACL rotated (NEWCRED exit 0, prefix 46fc87d2, old WRONGPASS); n-voice-cli-wake-mirror restarted; redis-server :6379 stopped+disabled. Archives: cluster-users.acl.bak.20260816T1416Z + db.env.bak.20260816T1416Z-pre-rotate.

## 2026-08-16 14:28:00 — Pathfinder (InfraOps T1)
Dropped stale `Wants=redis-server` from disabled units `nova-temporal-agent.service` and `vaeris-resurrection.service` (also dropped `Wants=neo4j` on the latter — Neo4j absent SP-904). `daemon-reload` only. Did not start those units. Did not stop `redis-server`. Langfuse already pointed at `dragonfly.service` earlier this turn.

## 2026-08-16 14:25:00 — Pathfinder (InfraOps T1)
Patched `langfuse-web`/`langfuse-worker` After/Wants `redis-server` → `dragonfly` (live REDIS_PORT=18000). daemon-reload only; Langfuse not bounced.

## 2026-08-16 13:42:00 — Pathfinder (InfraOps T1)
Daily domain inventory filed: `/adapt/novas/active/pathfinder/ops/reviews/2026-08-16_domain_inventory.md`.
