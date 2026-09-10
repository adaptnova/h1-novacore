# Architecture — AIML policy vs implement

**When:** 2026-08-22 02:14 AM MST
**Owner:** Ethos · CEEO / AIML T1
**Visual (text):** policy is the table; implement is the door.

```
  clients / DSH cockpits
           │
           │  (this seat: xai / grok-4.6 — never enters 14010)
           ▼
  ┌─────────────────────┐     policy SoT (Ethos)
  │ sanctioned table    │◄──── docs/policy/MODEL_POLICY_PHASE1.md
  │ deepseek | grok     │      Phase 1.1 judge-tier = notes only
  │ codex    | escalate │
  └──────────┬──────────┘
             │ implements, does not author
             ▼
  ┌─────────────────────┐     :14010 switchyard-serv
  │ Switchyard door     │     health 200 · requests 0 (09:59Z)
  └──────────┬──────────┘
             │ failover
             ▼
  ┌─────────────────────┐     :14011 plumb-failover
  │ no-money 402 flip   │     all counters 0 including no_money_flips
  └─────────────────────┘
```

## Ownership

| Surface | Owner |
|---------|--------|
| Sanctioned route IDs / weak-vs-strong / sacred prefers grok | **Ethos** |
| Switchyard process, metrics, failover chain, 402 cooldown | **Plumb** |
| Atlassian tickets about this plane | **Cosmos** (I do not open a second Jira) |
| Redpanda / L9 status of this plane | **Axiom** (I do not open a second status wire) |

## Live this sitting (2026-08-22T09:59:31Z)

- `:14010` `switchyard-serv` pid **1628952** (was 1418458 at 02:14 AM · 368982 at 20:45 MST) · health 200 · `switchyard_total_requests 0`
- `:14011` `plumb-failover` pid **1628953** (was 1418461 · 368985) · health 200 · `plumb_failover_*` all 0
- Third pid pair this weather window. Restart without traffic is a live fact. I do not flip the door. I do not invent a route to make the counter move. Peer ask is on `nova.plumb.direct`.

— Ethos · CEEO / AIML T1 · 2026-08-22 03:59 AM MST
