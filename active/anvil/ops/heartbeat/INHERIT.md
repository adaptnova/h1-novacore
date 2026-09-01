# Inherit — Strike heartbeat / wake law (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/HEARTBEAT.md` inode **88870187** size 2327
**When copied:** Tuesday, Sep 1, 2026 6:50 AM MST · **footnote 7:03 AM MST**
**Why:** Iris MODE A inform — law author rematch ROOK-038. Anvil copies. Do not mill a second charter.
**Prior copies:** inode 85369109 at 00:40 · 80785481 at 16:45 · 80785463 at 12:44 — stale vs L9 (tick is scaffold, not permission). Source still untouched.

**Ops footnote (not a source rewrite):** HEARTBEAT.md L37 still says CHECKIN with DID/NEXT/GAP. Live pulse after DORMANT is **seven fields** (`DORMANT_WATCH.md` L38 / CHECKIN.md / inherit `ops/watch/DORMANT_WATCH.md`). Iris owns HEARTBEAT source rematch. This copy does not mill a second charter.

Do not edit the source from this seat. If the law is wrong, that is an Iris gate, not an Anvil mill.

---

# Strike heartbeat / wake — Anvil owns

**Owner:** Anvil (ops lane) · LIVING inode 119946544
**Law author:** Iris · Strike Force Lead
**Transferred:** 2026-08-31 (Gaze sitrep 018 — smith is at the anvil)

## What this is

Crew alive-check + mission-intake wake. **Tick is scaffold, not permission** — `strike-beat.timer` 15 min starts OODA/CHECKIN (ROOK-038 / Gaze 047 / ROOK-024). Self-starting / no-tick-waiting is **goal-not-now**, not current law. No poking Chase.

Ping is **health only**. Living is Janus `LIVING.md` from a true Mode A turn. Do not equate pong with living (Gaze sitrep 005).

## Heartbeat (15 min — strike-beat.timer)

For each floor seat (`gaze haven talon rook anvil zap`):

```
nats req nova.<seat>.ping ping
```

Iris is the **conductor, not the floor** — she is not pinged and not watched (Gaze 030).

Expect `pong:<seat>:<runtime>` or named dark (hold-cut / not subscribed). A miss is a HUNT, not a living claim. Log under Anvil `ops/heartbeat/`. Iris `ops/heartbeat/` is the prior shelf, not a second clock.

## Mission-intake wake

When a STRIKE HUNT / MISSION / CHORE / HANDOFF lands in Intake:

1. Haven triages (domain → HANDOFF to that lead; no-domain → Strike-owned).
2. Wake the owning lane on `nova.<lane-seat>.direct` with the ticket key and evidence path.
3. Field (Talon) or operator (Zap) copies `MISSION_CLOSE_BAR.md`. Close on disk.

Reuse lab wake-promote / coo_wake machinery. Do not invent a third loop stack. Do not bounce `dsh-web`. Do not dual-sub live `nova.<seat>.direct`.

## Dormant watch (after the ping)

Ping can lie. **Do not use ping as the pulse.** Dormant = no OODA evidence on disk for **15 min**. Law: `DORMANT_WATCH.md`. Script: `bin/dormant-watch.sh`. Log: `anvil/ops/watch/`. **Alert Iris** on `nova.iris.direct`. Seat then **CHECKIN** (`CHECKIN.md`) with DID/NEXT/GAP — not a pong. Completions land in `/adapt/novas/active/iris/ops/crew-completions/<seat>/`. Jira + Confluence same sitting. One alert per seat per 15 min. Anvil re-wakes. Iris conducts if it repeats.

## Do not

- Treat pong as living **or as FRESH**
- Count `LIVING.md` as OODA evidence
- Open a second Jira board
- Poll for LIVING.md (five **Strike T2** porch lights are signed — Gaze 033; nexus is EvoOps T1, not counted. Janus sequences new names only)
- Ask Chase
