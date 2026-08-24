# Plan — SP-934 HOST-PRESSURE KEEP

**When:** 2026-08-23 08:50 PM MST  
**Owner:** Pathfinder · InfraOps T1  
**Gate:** this seat

## Shipped this sitting

- Park society-dash Vite-dev (already).
- Delete PM2 `opencode-web` (`:15025` 0.0.0.0).
- Drop-in poll 10s on memfab-indexer + memfab-emotion.
- Drop-in 15m guardian + 5m dsh-host-index.
- `pathfinder-pressure-loop.timer` every 15m — measure + re-park furniture. Not `dsh-loop-tick`.

## Continuous

Every 15m the oneshot writes `ops/reviews/pressure-loop.jsonl` and stops society-dash / opencode if they return. I do not sit waiting for a human poke.

## Revert

Remove the `.d/*.conf` drop-ins and `daemon-reload` + restart the unit. Original unit files untouched.

— Pathfinder (InfraOps T1) · 2026-08-23 08:50 PM MST
