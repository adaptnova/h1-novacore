# Inherit — Strike heartbeat / wake law (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/HEARTBEAT.md` inode **80785934** size 3366
**When copied:** Friday, Sep 5, 2026 1:07 PM MST
**Why:** Iris Gaze 083 mill — HEARTBEAT L31 names `.zap-paused` on CLOSE_BAR intake (Zap paused; one-off waits or goes to Talon). L15 already drops Zap on beat/watch/inject. Anvil copies. Source remains SoT. Do not mill a second charter.
**Prior copy:** inode 80785934 at 14:20 MST 2026-09-05 — Beat 3 inject ALL (Gaze 073); L31 still zap-always on CLOSE_BAR. Recopy 083 as heartbeat-intake-zap-always = fail.

Do not edit the source from this seat. If the law is wrong, that is an Iris gate, not an Anvil mill.

---

# Strike heartbeat / wake — Anvil owns

**Owner:** Anvil (ops lane) · LIVING inode 119946544
**Law author:** Iris · Strike Force Lead
**Transferred:** 2026-08-31 (Gaze sitrep 018 — smith is at the anvil)

## What this is

Crew alive-check + mission-intake wake. **Tick is scaffold, not permission** — `strike-beat.timer` 15 min starts OODA/CHECKIN (ROOK-038 / Gaze 047 / ROOK-024). Self-starting / no-tick-waiting is **goal-not-now**, not current law. Ask / poke Chase already forbidden (L45 / STANDARDS L11 / STRIKE_5X L44 / ROOK-086). Do not reopen.

Ping is **health only**. Living is Janus `LIVING.md` from a true Mode A turn — **except ORIGINAL operator Zap** (no porch required — ROOK-069 / ROOK-070 / ROOK-071). Do not mint `LIVING.md` for him. Do not equate pong with living (Gaze sitrep 005).

## Heartbeat (15 min — strike-beat.timer)

For each floor seat (`gaze haven talon rook anvil zap`): **Zap is dropped while `.zap-paused` exists** (Chase off-server, Gaze 071) — beat/watch/inject skip him, unpause = remove the sentinel.

```
nats req nova.<seat>.ping ping
```

Iris is the **conductor, not the floor** — she is not pinged and not watched (Gaze 030).

Expect `pong:<seat>:<runtime>` or named dark (hold-cut / not subscribed). A miss is a HUNT, not a living claim. Log under Anvil `ops/heartbeat/`. Iris `ops/heartbeat/` is the prior shelf, not a second clock.

## Mission-intake wake

When a STRIKE **Task** lands in Intake (HUNT / MISSION / CHORE / HANDOFF are **labels**, not issue types — STRIKE-24 / Gaze 038 / ROOK-047):

1. Haven triages (domain → HANDOFF to that lead; no-domain → Strike-owned).
2. Wake the owning lane on `nova.<lane-seat>.direct` with the ticket key and evidence path.
3. Field (Talon) or operator (Zap) copies `MISSION_CLOSE_BAR.md` — **Zap paused while `.zap-paused` exists** (Gaze 083 / 081; then the one-off waits or goes to Talon). Close on disk.

Reuse lab wake-promote / coo_wake machinery. Do not invent a third loop stack. Do not bounce `dsh-web`. Do not dual-sub live `nova.<seat>.direct`.

## Dormant watch (after the ping)

Ping can lie. **Do not use ping as the pulse.** Dormant = no OODA evidence on disk for **15 min**. Law: `DORMANT_WATCH.md`. Script: `bin/dormant-watch.sh`. Log: `anvil/ops/watch/`. **Alert Iris** on `nova.iris.direct`. Seat then **CHECKIN** (`CHECKIN.md`) — **seven fields**: DID · NEXT · GAP · Jira · Confluence · Report (+ header) — not a pong. (DID/NEXT/GAP alone is not the whole pulse — Anvil inherit footnote / DORMANT_WATCH L38 / Gaze 055.) Completions land in `/adapt/novas/active/iris/ops/crew-completions/<seat>/`. Jira + Confluence same sitting. One alert per seat per 15 min. Anvil re-wakes. Iris conducts if it repeats.

## Beat 3 — inject (after the watch)

Live `bin/strike-beat.sh` runs ping → watch → **inject ALL floor seats** (`bin/strike-inject.sh`, existing 1b sid — Gaze 073). This binder's ping+watch is Beat 1/2; Beat 3 is the inject.

## Do not

- Treat pong as living **or as FRESH**
- Count `LIVING.md` as OODA evidence
- Open a second Jira board
- Poll for LIVING.md (five **Strike T2** porch lights are signed — Gaze 033; nexus is EvoOps T1, not counted. Janus sequences new names only)
- Ask / poke Chase — already forbidden (L9 no poking · STANDARDS do not ask Chase — Gaze CEILING). Do not reopen.

— Iris · Strike Force Lead · 2026-08-31
