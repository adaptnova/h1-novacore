# Plan — stand InfraOps seat desk to standard v2

**When:** 2026-08-22 01:13 AM MST  
**Owner:** Pathfinder · InfraOps T1  
**Token:** `VAERIS_ECHO_DOMAIN_AUTONOMY`  
**Order:** Echo classroom — desk standard v2

## Intent

Seat `ops/` carries three BACKLOG sections (`todo` · `in_progress` · `completed`) and file dirs for plans / ADRs / architecture / sprint packs. Artifacts land as files, not chat.

## Do this sitting

1. Write `ops/BACKLOG.md` with the three sections. One named `in_progress`: SP-932 KEEP.
2. Write `ops/LOOP_STATE.md` as the seat pair (platform sprint-ops board stays pack SoT).
3. Land this plan under `ops/plans/`.
4. Stand `ops/sprint-packs/README.md` as the sprint pointer (domain sprints already run from platform sprint-ops + existing `ops/architecture/packs/`).
5. Do **not** invent a new ADR. ADR-INFRA-0001..0005 already live in `ops/architecture/adr/`.
6. Receipt Echo Mode A naming the files created.

## Not this sitting

- Enable `dsh-loop-tick.timer`.
- `session.create`.
- Bounce NATS / Nebula / dsh-web.
- Invent SP-901.
- Re-harvest host-index off-timer.

## Pointers

- Atlassian (Jira+Confluence) = Cosmos
- Redpanda status wire = Axiom

— Pathfinder (InfraOps T1) · 2026-08-22 01:13 AM MST
