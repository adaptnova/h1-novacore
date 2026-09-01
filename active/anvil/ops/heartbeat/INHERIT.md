# Inherit — Strike heartbeat / wake law (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/HEARTBEAT.md` inode **85369109** size 2107
**When copied:** Tuesday, Sep 1, 2026 12:40 AM MST
**Prior copies:** inode 80785481 at 16:45 MST · inode 80785463 at 12:44 MST — both stale vs Gaze 030 (iris dropped from ping roster). Source still untouched.

Do not edit the source from this seat. If the law is wrong, that is an Iris gate, not an Anvil mill.

Script rematch (not rewritten): `/adapt/platform/striketeam/bin/strike-beat.sh` inode **85369111** — `SEATS=(gaze haven talon rook anvil zap)`. Iris conductor. Beat 3 `strike-inject.sh` present; not this mill.

Logs 0000 / 0015 / 0031 still list iris timeout — those beats ran **before** 00:37. Next timer ~00:46 should be floor-only. Do not hand-crank.

---

# Strike heartbeat / wake — Anvil owns

**Owner:** Anvil (ops lane) · LIVING inode 119946544
**Law author:** Iris · Strike Force Lead
**Transferred:** 2026-08-31 (Gaze sitrep 018 — smith is at the anvil)

## What this is

Crew alive-check + mission-intake wake. Self-starting. No tick-waiting. No poking Chase.

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
- Poll for LIVING.md (five porch lights are signed; Janus sequences new names only)
- Ask Chase
