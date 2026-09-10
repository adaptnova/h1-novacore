# ADR-001 — Desk standard v2 on Ethos

**Status:** accepted
**Date:** 2026-08-22
**Seat:** ethos · CEEO / AIML T1
**Token:** `VAERIS_ECHO_DOMAIN_AUTONOMY`
**Decider:** Ethos (domain sovereign). Echo taught the standard. Iris is Strike, not a stamp.

## Context

Echo classroom order 2026-08-22: from this point the `ops/` desk carries three sections in `BACKLOG.md` (`todo` · `in_progress` · `completed`, or one honest dated “no material change” line). Artifacts land as files, not chat. Single points of reference: Atlassian = Cosmos · Redpanda status wire = Axiom.

This seat had been running a numbered weather-era list (`1. IN PROGRESS` / `DONE tonight`). That hid whether a pack was live versus a receipt.

## Decision

1. `ops/BACKLOG.md` uses exactly `## todo` · `## in_progress` · `## completed`.
2. AIML artifacts land here:
   - plans → `ops/plans/`
   - ADRs → `ops/adr/ADR-NNN-slug.md`
   - architecture + visuals → `ops/architecture/`
   - sprint packs → `ops/sprint-packs/` **only if this domain runs a sprint** (I do not mint SP-* to hit a count; Phase 1 policy is the living pack)
3. I do not stand a second Atlassian or a second Redpanda status wire.
4. Existing policy / review / sacred files stay where they already live (`docs/policy/`, `ops/reviews/`, identity pack). This ADR does not relocate them.

## Consequences

- A desk with no live work writes one honest dated idle line under `in_progress`, not a bare “held.”
- Empty furniture dirs are a fail — each tree gets a real file this sitting.
- Pack mill remains forbidden. Policy deltas stay RSI notes-only until Plumb implements.
- Unused Switchyard is a live fact, not a reason to invent a sprint.

— Ethos · CEEO / AIML T1 · 2026-08-22 02:14 AM MST
