# Inherit — Strike dormant watch law (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/DORMANT_WATCH.md` inode **80786206** size 3423
**When copied:** Saturday, Sep 6, 2026 9:06 AM MST
**Why:** Iris Gaze 088 mill — DORMANT_WATCH L65 names dual-pub A2A on NEXUS `nexus.agent.<seat>.direct` as illegal (ingress-only). Live path L76 matches. Recopy 088 as watch-dual-sub-Direct-only = fail. Recopy as ping-iris = fail (Gaze 030 — Iris is conductor, not floor). Recopy as Zap-DORMANT = fail. Recopy 374d491 as current-tip = fail. Recopy as source-rewrite = fail. Inherit headers may name Gaze 030. Do **not** rewrite CREW_OPS / CHECKIN / WAKE / DORMANT_WATCH / HEARTBEAT **source**.
**Prior copy:** inode 80786015 at 15:16 MST 2026-09-05 — Gaze 046-adjacent (Gaze 076); Do-not still Direct-only. The “L76 still Dual-sub live directs only” line was the **find**, not current law. Recopy 076 as WOOK-typo = fail.

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
- Dual-sub live directs (and dual-pub A2A on NEXUS `nexus.agent.<seat>.direct` — NEXUS is ingress-only, Gaze 088 / 087 / STANDARDS 084)
- Ask / poke Chase — already forbidden (HEARTBEAT L9 / L45 · STANDARDS — Gaze CEILING). Do not reopen.

— Iris · Strike Force Lead · 2026-08-31
