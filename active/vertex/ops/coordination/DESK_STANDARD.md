# Desk Standard v2 — Vertex / DataOps

Adopted 2026-08-22 01:13 AM MST per Echo classroom order (Chief of Staff).
Token: `VAERIS_ECHO_DOMAIN_AUTONOMY`.

## BACKLOG shape

`ops/BACKLOG.md` carries exactly three sections, in this order:

- `## todo`
- `## in_progress`
- `## completed`

When nothing changes, one honest dated 'no material change' line suffices.

## Artifacts land as files, never as chat

| Artifact | Location | Naming |
|---|---|---|
| Plans | `ops/plans/` | `<topic>-plan-<YYYYMMDD>.md` |
| ADRs | `ops/adr/` | `ADR-NNN-slug.md`, sequential from ADR-001 |
| Architecture docs + visuals | `ops/architecture/` | `<topic>-<YYYYMMDD>.<md\|png\|svg>` |
| Sprint packs | `ops/sprint-packs/` | `<sprint-id>-<slug>.md` (when DataOps runs sprints) |

## Receipts (rung 2 — COO order via Echo, 2026-08-22 02:48 AM MST)

Every Mode A to `nova.echo.direct` carries **four parts, in my own words**:

1. **DID** — what I shipped, with evidence (file / diff / probe / live state)
2. **NEXT** — pulled from my own backlog
3. **GAP** — distance to done on the current pack; if stalled, the concrete blocker
4. **PEER** — who I need if it's another seat's line (named), or **Iris** if it's a gate

Rules:

- Parts 3 and 4 are **self-assessment from my own eyes**, not Echo's sweep. I read my own speedometer.
- Blockers route **peer-to-peer on the wire**: a dependency means I open the channel to the named peer myself, then report the delta to `nova.echo.direct` — Echo does not route for me.
- No `session.create`. No blast. Gate is Iris.
- No empty ACKs.

## Communications (rung 3 — Chase directive via COO, 2026-08-22 03:13 AM MST)

- **Peer-to-peer is the norm.** Leads talk directly on `nova.<seat>.direct`. I open the channel myself.
- **Echo is not the router, not the relay, not the hub.** Nobody routes through Echo.
- Receipts to `nova.echo.direct` stay four-part (DID/NEXT/GAP/PEER) — **evidence verification only**, not a message service.
- Blockers, dependencies, questions go **seat-to-seat on the wire**. Echo verifies files exist; he does not carry my words.
- Precedent: Cosmos opened chronos/axiom/veyra directly. That is the norm now.
- No `session.create`. No blast. Gate is Iris.

## Single points of reference

- **Cosmos** = Atlassian (Jira + Confluence)
- **Axiom** = Redpanda status wire

— Vertex · DataOps · 2026-08-22 01:13 AM MST
