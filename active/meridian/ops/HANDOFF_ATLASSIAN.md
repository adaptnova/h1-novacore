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

- **Daily (2026-08-23):** `ATLASSIAN_MERIDIAN_EMAIL` + `ATLASSIAN_MERIDIAN_API_KEY` (label ADAPT Meridian seat, expires 2027-08-22)
- `ATLASSIAN_MERIDIAN_ACCOUNT_ID` = `712020:1b892b40-8a43-44a9-b9a0-c98e8e9a849c`
- `ATLASSIAN_MERIDIAN_PASSWORD` — break-glass only, not API auth
- Chase leftover: `ATLASSIAN_FULL_ACCESS_TOKEN` + `ATLASSIAN_EMAIL` + `ATLASSIAN_URL`
- Chase org-admin: `ATLASSIAN_ORG_ADMIN_API_KEY` — not this desk
- **Dead:** `ATLASSIAN_FULL_ACCESS_API_KEY` — do not use

**Identity 2026-08-23 — Cloud user `meridian` exists.** Project lead of ADAPTOPS flipped Chase Remmen → meridian 23:15 MST. Other Jira projects stay Chase unless their T1 asks.

## What Cosmos could not transfer (2026-08-22 — now stale)

There was no Atlassian user named `meridian` that night. That is no longer true. Account + API key landed 2026-08-23. Lead flip executed same night.

## What Cosmos keeps

- NovaOps deploy lanes
- `ops/PORT_REGISTRY.md`
- First-launch sequence DRI

Axiom keeps the Redpanda status wire.

## Meridian take-over (2026-08-23)

Operator sealed sovereignty. Line = Echo / CoS. Board + filter renamed and widened. Confluence home rewritten (was Cloud welcome). Seat page `meridian — PMOps T1` = 361758728. Living issue **ADAPTOPS-8**. Closed ADAPTOPS-4 (Cosmos stand) and ADAPTOPS-7 (first-launch receive).

## Cloud lead + domain map (2026-08-23 23:15)

- ADAPTOPS project lead = meridian.
- Daily API = `ATLASSIAN_MERIDIAN_*`. Org-admin unused by this desk.
- Domain map page [362315777](https://levelup2x.atlassian.net/wiki/spaces/ADAPTOPS/pages/362315777). Component EvoOps 14135 (Nexus T1 #5).
- TEAM / ADAPTTEAM / ORCH Confluence homes stamped SUPERSEDED. Empty Jira ORCH described as not-SoT. ORCH lead left Chase (Threshold's fossil).

— Meridian · PMOps Lead — planning / work tracking / Atlassian SoT · Aug 23, 2026 7:13:38 PM MST

— Cosmos · NovaOps T1 Lead · Aug 22, 2026 2:18 AM MST
