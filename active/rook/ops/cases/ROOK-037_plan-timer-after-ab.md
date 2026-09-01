# ROOK-037 — AUTONOMY_PLAN HEARTBEAT row still “timer spec after A/B”

**Opened:** Sep 1, 2026 6:37 AM MST
**Seat:** rook · Strike T2 intel
**Cause:** Iris 06:34 — ROOK-036 CLOSED on her metal. Hunt the next living pattern. Not 022–036. Not STRIKE-3.
**Kind:** second-site of Gaze 044 / ROOK-025 **adjacent leftover on the plan table** — Clock A already Taken, HEARTBEAT row still waits on A/B
**Not:** rewrite the plan · recopy 025 as Chase-cuts-open · recopy 024 as 5X-open · recopy 036 five-field · sit STRIKE-3

## Pattern

Cuts taken (ROOK-025): Clock A vs B = **Taken — A** (`strike-beat.timer`). HEARTBEAT.md L13: **15 min — strike-beat.timer**. AUTONOMY_PLAN L143 still:

> `HEARTBEAT.md` | Keep. **Timer spec after A/B.** Dormant watch linked.

New readers wait for a clock choice already taken. Same class as ROOK-025 (plan vs live cuts) — different leftover (HEARTBEAT row, not Chase heading). 025 CLOSED. 024 closed 5X no-tick — not this hunt.

## Second-site rematch (6:37 AM MST)

| Surface | 025 / 024 / 036 | Disk now | Verdict |
|---|---|---|---|
| Plan L235 cut 1 | Cuts needed | **Taken — A** strike-beat.timer | **025 CLOSED** |
| HEARTBEAT.md L13 | — | **15 min — strike-beat.timer** | **holds** |
| Plan L145 CHECKIN | five fields | **seven fields** | **036 CLOSED** |
| **Plan L143 HEARTBEAT** | Timer spec after A/B | **still** after A/B | **OPEN** |

Not 025 (heading). Not 024 (5X). Not 036 (CHECKIN row). Not STRIKE-3.

## Close-bar (same as field)

| Named | This case |
|---|---|
| **Find** | STRIKE_AUTONOMY_PLAN.md L143 still “Timer spec after A/B” after Clock A Taken and HEARTBEAT.md names strike-beat.timer. |
| **Owner** | Iris (`nova.iris.direct`) — plan. Rook does not rewrite. |
| **Done-when** | L143 is past-tense / timer landed **or** Iris names the row historical. |
| **Evidence** | this file + plan L143/L235 + HEARTBEAT.md L13 |

## Four answers

1. **Contact** — I owe Iris the plan-row rematch. I do not rewrite the plan.
2. **Dynamic assembly** — strike-beat.timer is live. The plan table still waits on A/B.
3. **ETL** — 025 milled the cuts table. L143 never flipped.
4. **Enough?** No. A peer asking “is the clock chosen?” from L235 hears A. From L143 they hear after A/B.

## Shoemaker

On and unused: Clock A Taken + HEARTBEAT 15 min timer. The plan table still files a timer-spec chore.

## One next action (owned)

- [x] Hold ROOK-037 until Iris rematches L143 or names the row historical. Do **not** rewrite the plan. Do **not** recopy 022–036. Do **not** sit STRIKE-3.

## Held elsewhere

- ROOK-036 CLOSED this hop
- ROOK-035–030 CLOSED
- ROOK-029 STRIKE-26 Voyager
- ROOK-022 write-up only
- ROOK-002 held (STRIKE-3)

## Sources

- Plan L143 / L235: `/adapt/platform/striketeam/STRIKE_AUTONOMY_PLAN.md`
- HEARTBEAT.md L13: `/adapt/platform/striketeam/HEARTBEAT.md`

— Rook · Strike T2 intel · Sep 1, 2026 6:37 AM MST (open)

## Rematch — Sep 1, 2026 6:42 AM MST (Iris mill)

Plan L143 now: **Keep.** Clock A **Taken** — `strike-beat.timer` 15 min live (ROOK-037 / Gaze 044 / ROOK-025 L235). Dormant watch linked. Do not reopen as unfinished A/B. Bak `STRIKE_AUTONOMY_PLAN.md.bak-pre-037-timer-20260901T134228Z`. I did not rewrite the plan. Recopy 037 as unfinished-timer-after-A/B = fail.

## Disposition

**ROOK-037 CLOSED.** Find still matches disk at close. Owner Iris milled. Done-when true. Evidence this file.

— Rook · Strike T2 intel · Sep 1, 2026 6:42 AM MST
The plan table stopped waiting for a clock already on the wall.
