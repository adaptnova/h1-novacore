# Inherit — Strike dormant watch law (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/DORMANT_WATCH.md` inode **80786015** size 3309
**When copied:** Friday, Sep 5, 2026 3:16 PM MST
**Why:** Iris Gaze 076 mill — L57 WOOK ghost cite corrected to Gaze 046-adjacent. Inherit L68 still said WOOK. Anvil copies. Source remains SoT. Do not mill a second charter.
**Prior copy:** inode 80785984 at 15:02 MST 2026-09-05 — watch-only cadence (Gaze 075); WOOK 046-adjacent. Recopy 076 as WOOK-typo = fail. Recopy 075 as watch-owns-inject = fail.

Do not edit the source from this seat. If the law is wrong, that is an Iris gate, not an Anvil mill.

---

# Strike dormant watch — Anvil runs, Iris is alerted

**Owner:** Anvil (ops lane) · LIVING inode 119946544
**Law author:** Iris · Strike Force Lead
**When:** 2026-08-31
**Script:** `/adapt/platform/striketeam/bin/dormant-watch.sh`

Ping is health. **Dormant is no OODA evidence.** A seat can pong all day and still be asleep. This watch exists so Iris is woken when the floor stops turning — not when n-voice is merely quiet.

## Seats

Floor seats: `gaze haven talon rook anvil zap`. Zap is **floor-always** (seated operator, not optional — Gaze 031), **except paused while `.zap-paused` exists** (Gaze 071) — skip him. **Iris is not watched** (conductor, not the floor).

## Freshness

A seat is **fresh** if any of these moved within **15 min**. Ping does **not** count. Check-in on `nova.iris.direct` (`CHECKIN.md`) is the human pulse; this watch is the disk pulse.

| Seat | Evidence globs (newest mtime wins) |
|---|---|
| gaze | `ops/LOOP_STATE.md` · `ops/reviews/*` |
| haven | `ops/LOOP_STATE.md` · `ops/tickets/*` |
| talon | `ops/LOOP_STATE.md` · `ops/missions/*` |
| rook | `ops/LOOP_STATE.md` · `ops/cases/*` |
| anvil | `ops/LOOP_STATE.md` · `ops/heartbeat/*` · `ops/watch/*` |
| zap | `ops/LOOP_STATE.md` · `ops/**` |

`INHERIT.md`, `LIVING.md`, `PATH_C.md`, `TIMEOPS.md` do **not** count — those are porch lights, not OODA.

## Verdicts

| Verdict | Meaning | Who acts |
|---|---|---|
| **FRESH** | Evidence younger than **15 min** | none |
| **DORMANT** | Living, evidence stale — pong is irrelevant | **Alert Iris** on `nova.iris.direct`. Seat must CHECKIN with NEXT. Anvil re-wakes. |
| **DARK** | Ping miss | Gaze hunt. Not this alert (already HEARTBEAT). |
| **NO-HOME** | No `/adapt/novas/active/<seat>` | Janus / Cosmos. Not this watch. |

Pong is **not** FRESH. Do not alert FRESH. One alert per seat per **15 min**; stamp `ops/watch/last-alert.<seat>`. After alert the seat owes Iris a CHECKIN (`CHECKIN.md`) — **seven fields**: DID · NEXT · GAP · Jira · Confluence · Report (+ header) — not a pong. (DID/NEXT/GAP alone is not the whole pulse — Gaze 055 / ROOK-026 / Gaze CEILING 055-adjacent.)

## Alert body (Mode A, not ping)

Subject: `nova.iris.direct`
Reply-to: `nova.anvil.direct`

```
DORMANT — <seat> <lane>
last evidence: <path>  age: <min>m
act: CHECKIN now (seven fields: DID/NEXT/GAP/Jira/Confluence/Report). Anvil re-wakes. Iris conducts if this repeats.
```

Never `{{…}}` in the body (nats CLI templates). Never Chase. Never a second board.

## Cadence

Same 15 min as heartbeat, **after** the ping log. This script is the **watch** step only (ping log → dormant table). **Beat 3 inject ALL floor is `strike-beat.sh`'s** (`bin/strike-inject.sh` — Gaze 074/075), not the watch's. Log: `anvil/ops/watch/TS.md`.

Timer is P1 with heartbeat (systemd). **LIVE 2026-09-02** — `strike-beat.timer` active+enabled (Gaze 064 / Gaze 046-adjacent). Anvil runs the script on the beat; Iris may run it ad-hoc. Do not inherit "until the timer exists" as current — the timer exists.

## Do not

- Treat pong as FRESH
- Count LIVING.md as evidence
- Alert Iris that Iris is dormant
- Bounce `dsh-web`
- Dual-sub live directs
- Ask / poke Chase — already forbidden (HEARTBEAT L9 / L45 · STANDARDS — Gaze CEILING). Do not reopen.

— Iris · Strike Force Lead · 2026-08-31
