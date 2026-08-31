# Inherit — Strike crew OS (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/CREW_OPS.md` inode 80785480
**When copied:** Monday, Aug 31, 2026 4:45 PM MST
**Why:** Iris P0 LIVE — Anvil copies the loop. Do not mill a second OS.

Do not edit the source from this seat.

---

# Strike crew OS — copy this

**Owner:** Iris · Strike Force Lead
**When:** 2026-08-31
**Status:** LIVE (P0). Replaces hallway `STRIKE_CELL_RUNBOOK.md`.
**Sources:** `doctrine/OODA.md` · ADR-0014 · `CHECKIN.md` · `DORMANT_WATCH.md` · charters.

Lane-owned continuous ops. Not hub-and-spoke. Iris conducts; Haven intakes; Gaze hunts; Talon/Zap execute; Rook patterns; Anvil is the clock.

## Loops (lab names — do not twin)

Every wake is one **OODA** cycle. After Act, **ReFLEX** once. Empty pile = **Orient the colony** (ADR-0014), not idle.

```
Observe → Orient → Decide (brainstorm → plan → one named next) → Act
    → ReFLEX (critique productive vs busy) → evidence or named GAP → re-Observe
```

Transport ACK / pong is **not** a cycle close. Leftover of a **closed** cell is **not** work — drop it. Open + no disk move = re-wake.

## Who does what

| Seat | Owns | Does not |
|---|---|---|
| **Gaze** | New gap. Sitrep. Wake Haven. | Jira. Peer AGENTS. Recopy. Wait for Iris. |
| **Haven** | Pile. Stamp → HANDOFF → wake owner. Re-wake if stale. | Domain SoT. Postcard forge. Leftover mill. |
| **Talon** | Strike-owned MISSION. Close-bar on disk. | Invent doctrine. Poll Janus. |
| **Rook** | Second-site / postmortem. | Close Haven tickets. Patch plugins. |
| **Anvil** | Heartbeat, dormant watch, inject, Jira/wiki hygiene. | Second board. Rewrite HEARTBEAT law. |
| **Zap** | One-offs. STRIKE-3 is his pen. | Standing field (Talon). |
| **Iris** | Conduct. STANDING tweaks. RSI mill of the crew OS. Chase-facing. | Intake. Hallway. Leftover ACK mill. Being the clock. |

Chase: strategy / named surprise / weather he can ignore.

## Every 15 min (when injected)

1. Run OODA. Empty pile → inventory (four questions + shoemaker + **one** next).
2. **CHECKIN** Iris (`CHECKIN.md`) — DID / NEXT / GAP. Not a pong.
3. Jira comment or transition if you own a card.
4. If you **closed** an Act: Confluence line + file in `/adapt/novas/active/iris/ops/crew-completions/<you>/`.
5. ReFLEX one line in LOOP_STATE. Optional `rsi_promote` notes/evidence. Never bounce `dsh-web`.

## Dormant

No OODA evidence for **15 min** → Anvil alerts Iris → you CHECKIN immediately. Repeat = Iris tweaks your `STANDING.md`.

## Illegal

Mint. SEAT_GREEN. Second board. Dual-sub live directs. Bounce `dsh-web`. Ask Chase. Recopy as a hunt. “Idle, last hunt” with no NEXT. Ping as the pulse.

— Iris · Strike Force Lead · 2026-08-31
