# Atlassian SoT handoff — LIVE

**Token:** `VAERIS_ECHO_DOMAIN_AUTONOMY`  
**When:** Aug 22, 2026 2:18 AM MST  
**From:** Cosmos (interim — relieved)  
**To:** Meridian (PMOps Lead)  
**Base:** this file at 01:33 · Chase-directed via Echo

## Handed over (operational SoT)

| Surface | Handle | URL |
|---|---|---|
| Instance | LevelUp2X | https://levelup2x.atlassian.net |
| Jira project | `ADAPTOPS` / 10725 Adapt Fleet Operations | https://levelup2x.atlassian.net/jira/software/c/projects/ADAPTOPS |
| Board | **167** ADAPTOPS Fleet Desk (kanban; was NovaOps Seat Desk) | https://levelup2x.atlassian.net/jira/software/c/projects/ADAPTOPS/boards/167 |
| Filter | **10271** ADAPTOPS Fleet Desk | `project = ADAPTOPS ORDER BY Rank ASC` — project-shared. `desk-v2` is a tag, not membership |
| Confluence space | `ADAPTOPS` / 359661570 | https://levelup2x.atlassian.net/wiki/spaces/ADAPTOPS |
| Tree | Desk Standard v2 · Plans · ADRs · Architecture · Visuals | 361234433 · 361267201 · 361299969 · 361332737 · 361365505 |
| Handoff page | Atlassian SoT — Meridian / PMOps | https://levelup2x.atlassian.net/wiki/spaces/ADAPTOPS/pages/361299985 |

Desk standard v2: `ops/BACKLOG.md` `## todo` · `## in_progress` · `## completed`.

## Auth pointer (names only — never print values)

In `/adapt/secrets/m2.env`:

- `ATLASSIAN_FULL_ACCESS_TOKEN` — use this
- `ATLASSIAN_EMAIL`
- `ATLASSIAN_URL`
- **Dead:** `ATLASSIAN_FULL_ACCESS_API_KEY` — do not use

**Identity decision 2026-08-22 — existing account, no Cloud mint.** Meridian operates on the existing token account (Chase Remmen). No dedicated Cloud user minted.

## What I could not transfer (honest)

There is **no Atlassian user named `meridian`**. User search this hour: 0 hits.  
Project lead and the token’s human account remain **Chase Remmen** (`712020:83a24d8c-57b6-4412-8cff-2f1b666628a4`). I will not invent a Cloud user. Lead-account flip is a mountain for Vaeris / Chase if they want a dedicated Meridian identity. Decision above is now Chase/COO law, not a leftover ask.

## What Cosmos keeps

- NovaOps deploy lanes
- `ops/PORT_REGISTRY.md`
- First-launch sequence DRI

Axiom keeps the Redpanda status wire.

## Meridian take-over (2026-08-23)

Operator sealed sovereignty. Line = Echo / CoS. Board + filter renamed and widened. Confluence home rewritten (was Cloud welcome). Seat page `meridian — PMOps T1` = 361758728. Living issue **ADAPTOPS-8**. Closed ADAPTOPS-4 (Cosmos stand) and ADAPTOPS-7 (first-launch receive).

— Meridian · PMOps Lead — planning / work tracking / Atlassian SoT · Aug 23, 2026 7:13:38 PM MST

— Cosmos · NovaOps T1 Lead · Aug 22, 2026 2:18 AM MST
