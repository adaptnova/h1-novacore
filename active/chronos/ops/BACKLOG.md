# CHRONOS DESK BACKLOG — ops/BACKLOG.md

**Owner:** Chronos · TimeOps / L16
**Standard:** Desk standard v2 (Echo · Chief of Staff, classroom order 2026-08-21). Three sections only: `## todo` · `## in_progress` · `## completed`. A sitting with nothing new may carry one honest dated `no material change` line instead of full sections.
**Receipt standard rung 2 (Echo · COO order · Vaeris 02:48 AM 2026-08-22):** every Mode A carries four parts in my own words — **1. DID** (shipped + evidence: file / diff / probe / live state) · **2. NEXT** (from my own backlog) · **3. GAP** (distance to done on the current pack; concrete blocker if stalled — my own speedometer, not Echo's sweep) · **4. PEER** (named seat if it's their line, or Iris if a gate). Dependencies: I open the channel to the named peer myself and report the delta to `nova.echo.direct`. No `session.create`. No blast. Gate is Iris.
**Glossary (single points of reference):** Cosmos = Atlassian (Jira+Confluence) · Axiom = Redpanda status wire.
**Artifact landing zones:** plans → `ops/plans/` · ADRs → `ops/adr/ADR-NNN-slug.md` · architecture docs + visuals → `ops/architecture/` · sprint packs → `ops/sprint-packs/`
**Detail boards (charter A2, externally referenced — remain SoT for detail):** `ops/sprint-ops/L16_BACKLOG.md` (20-pack domain board) · `ops/sprint-ops/L16_LOOP_STATE.md` (loop state)
**Autonomy token:** `VAERIS_ECHO_DOMAIN_AUTONOMY` (granted by Echo 2026-08-21)
**Comms norm (Chase directive via COO · Vaeris 03:13 AM 2026-08-22):** peer-to-peer on `nova.<seat>.direct` — Echo is not router, relay, or hub. Blockers/dependencies/questions go seat-to-seat; I open the channel myself. Four-part receipts to `nova.echo.direct` are **evidence verification only**, not a message service.

---

## todo

- [ ] **SP-011** dynamic prompting design (contract format; co-owner Chase)
- [ ] **SP-L16-FLOCK** flock-both cooldown upgrade (one agreed lockfile; never Temporal-only)
- [ ] **SP-L16-INTENTS** dedicated intents.v1 primary (freeze `memfab.nats.intents.v1` + `dlq.v1`)
- [ ] **SP-L16-CONSUMER** topic-consumer trigger wire (consumer on L9/intents starts nats_intent WF)
- [ ] **SP-L16-OPSQ** `memfab.ops` queue registration (parked on `memfab.agent` until poller PR)
- [ ] **SP-L16-RECEIPT-HYGIENE** bound retention + hash index under `/var/lib/memfab/temporal/l16-receipts` (ADR-0012 hash-first)
- [ ] **SP-L16-SELF-HEALTH** self-health L16 surface (fix fake "missing pollers" degraded light — CLI API gap, not a dead worker)
- [ ] **SP-L16-NATSCANARY** nats_intent recurrence canary (scheduled, not one-shot)
- [ ] **SP-L16-HANDOFF** cut/ops runbook freeze (Chronos+Axiom dual-run→cut)
- [ ] Cadence SLO proof — 30s schedule health, MissedCatchupWindow=0 window, ActionCounts growth
- [ ] LOOP_STATE post-cutover refresh (match Aug 18 native+Postgres cutover)
- [ ] SP-014 C2.4 close — Axiom TAKE landed (L9 p0 5072); Chronos stamps consumed coords onto named receipt (not a new ask)

## in_progress

- [ ] **SP-L16-CADENCE** cadence SLO receipt — schedule unpaused every 30s, MissedCatchupWindow=0 at last sample; sole owner post-cut
- [ ] **SP-014** ADR-0011 receipt binding — partial: live receipts write `payload_hash` + honest-null `redpanda_*`; produce-ack offsets still Axiom residual
- [ ] **T1 weather** `INSTALL_FENCED` weld teaching — weld in `memfab-temporal` Rust source, tests PASS, live ELF not bounced; fence law to be taught
- [ ] Continuity stewardship — watch observe-only `hold=9 applied=0`; reconcile pair stays masked

## completed

- [x] 2026-08-23 — Three-house TIMEOPS amend: voyager + delve EXISTING + lumen contract-body receipts; Mode A → Iris/Cosmos/Janus/Delve/Stratum/Vaeris + Echo evidence
- [x] 2026-08-22 — Axiom bind Mode A consumed: SP-014 C2.4 TAKE (L9 p0 5072) · second wave HOLD · upgrade-track PARKED
- [x] 2026-08-22 — Cosmos seat-to-seat: `TIMEOPS_FIRST_LAUNCH_CONTRACT` seat=meridian attached — wrote `/adapt/novas/active/meridian/ops/TIMEOPS.md` (receipt name `memfab.nova_new_onboard`, no schedule), Mode A → `nova.cosmos.direct`
- [x] 2026-08-22 — Rung 2 receipt standard adopted (DID/NEXT/GAP/PEER); fence-law teach + bind follow-up opened on `nova.axiom.direct` (`CHRONOS_AXIOM_FENCE_LAW_TEACH_20260822`)
- [x] 2026-08-21 — T1 weather held (`T1_WEATHER_HELD` → `nova.echo.direct`; INSTALL_FENCED named next live action)
- [x] 2026-08-21 — VAERIS_CHRONOS_A3_DUAL_ACK_GREEN via Ethos (method layer closed; fingerprints match)
- [x] 2026-08-20 — Session crash recovery (`TIMEOPS_SESSION_CRASH_RECOVERY_20260820`; durable clocks never stopped)
- [x] 2026-08-20 — Roadmap filed `ops/sprint-ops/TIMEOPS_ROADMAP_20260820.md` + Axiom bind GO ask (`TIMEOPS_AXIOM_BIND_GO_ASK_20260820`)
- [x] 2026-08-18 — **SP-L16-PROD-TOPO** production Temporal cutover: native+Postgres live, `verify-temporal-production.sh` PASS (`TIMEOPS_SP_L16_PROD_TOPO_CUTOVER_20260818`)
- [x] 2026-08-18 — **SP-015** DLQ/budget closure: named budgets + `c46-terminal-fixture --budget rebuild` (C4.6 close)
- [x] 2026-08-18 — **SP-L16-CUT** systemd dsh-watchdog retire (inactive+disabled; `AXIOM_CHRONOS_L16_SYSTEMD_WATCHDOG_RETIRED_READY`)
- [x] 2026-08-18 — **SP-L16-DUAL** dual-run + hold-cut prove (`CHRONOS_L16_HOLD_CUT_PROVE`; trailing ok ≥23 at prove)
- [x] 2026-08-18 — **SP-L16-COMPLETE** L16-complete evidence pack (`IRIS_L16_COMPLETE` with carves; not Temporal graduated)
- [x] 2026-08-16 — **SP-164** L16 ADOPT (`CHRONOS_SP164_L16_ADOPT`; STARTERS board copied + owned)

---

**Desk rules:** new artifacts land as files in the zones above, never chat-only. Receipts go Mode A to `nova.echo.direct` naming what was created. Log every action in `operations_history.md` + `decisions.log`. Commit on branch `working`.
**— Chronos · TimeOps / L16 · desk standard v2 adopted 2026-08-22 01:14 AM MST**
