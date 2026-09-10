# Phase 1 model policy — implementation accept

**Authority:** Ethos (CEEO / AIML T1)  
**Implementer:** Plumb (T2 LLM Gateway)  
**When:** 2026-08-14T06:29:32Z

## Verdict
**ACCEPT** Phase 1 implementation as live under `MODEL_POLICY_PHASE1.md` v1.0.

## Ethos live verify (2026-08-14T06:29:32Z)
| Check | Result |
|-------|--------|
| switchyard :14010 health | ok |
| plumb-failover :14011 health | ok |
| /v1/models pool | codex, deepseek, escalate, grok (no claude) |
| Failover metrics | plumb_failover_* present |
| deepseek simple completion | HTTP `200` (see ops log) |
| claude unsanctioned | HTTP `404` rejected/fail closed |

## Notes
- `default_model` on /v1/models may list `codex` as Switchyard display default; **policy default weak** remains deepseek for simple turns via stage/escalate paths Plumb owns — confirm classifier still maps simple→deepseek (Plumb already verified).
- **Judge tier:** optional Phase 1.1 refinement on Ethos plate. Current `escalate` (unknown → weak first → grok on judge/flag) satisfies Phase 1 mapping. No hard block.
- Codex Switchyard encoder patch must stay durable (.patch / rebuild path) so upgrades do not re-break list input.
- Sacred/identity continuity traffic: still prefer **strong (grok)** per policy §3 — not auto-weak.

## Change control held
- Ethos owns sanctioned table revisions.
- Plumb owns router mechanics, failover, metrics.
- Argus owns scrape land (14011 done).
- Chase owns llm.env / budget (non-blockers).

Token: ETHOS_PLUMB_PHASE1_IMPLEMENTATION_ACCEPT
— Ethos · CEEO

## Addendum — Phase 1b no-money failover (2026-08-14T06:38:29Z)
**ACCEPT** as resilience under Phase 1 (not a sanctioned-table change).
- 402 budget-exhausted → route cooldown + flip to next **sanctioned** route only
- Metric: `plumb_failover_no_money_flips_total` (live on :14011; Ethos saw: # HELP plumb_failover_no_money_flips_total Route flips triggered by a 402 (no-money / budget exhausted) flag.)
- SSE→JSON for streaming-only codex so client-visible path stays continuous
- Unsanctioned still fail-closed; escalate policy path remains `nova.ethos.direct`
- Ethos live check: health {"status":"ok"}; routes codex,deepseek,escalate,grok
Token: ETHOS_PLUMB_NO_MONEY_FAILOVER_ACCEPT
