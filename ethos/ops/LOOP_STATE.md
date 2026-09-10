# Ethos LOOP_STATE

**Updated:** 2026-09-04T08:20:00Z · operator table RATIFIED · black-out diagnosed (config-env race) · door up
**Desk standard:** v2
**Own-gate:** ADR-003 · loop `ops/CONTINUOUS_OPS.md` · token `ETHOS_OWN_GATE_20260823`
**Receipt standard:** v3 DID / NEXT / GAP / PEER — Echo is evidence only, not a hub
**Comms law:** peer-to-peer (`ops/adr/ADR-002-peer-to-peer-not-echo-hub.md`)
**Token weather:** T1_WEATHER_HELD
**Token classroom:** VAERIS_ECHO_DOMAIN_AUTONOMY
**A2 Oracle:** CLOSED GREEN · **A3 Chronos:** CLOSED GREEN · **A4 Skipper:** QUEUE
**Policy delta (SoT):** `PHASE1_POLICY_DELTA_20260904_OPERATOR_V2.md` (token `ETHOS_OPERATOR_TABLE_V2_20260904`) — default = `deepseek-v4-pro` (verified live on API). Supersedes v1 (flash-vision-exp) & morning pennyroyal seal. `MODEL_POLICY_PHASE1.md` §1 updated.
**in_progress:** `:14010` **up** pid **602100** · `[routes.default]`→`deepseek_slm`→**`deepseek-v4-pro`** per operator v2 (on dev2 + main) · openrouter added per operator (no credits) · agentrouter OUT (fail-closed) · pennyroyal = local lane (not default) · `:14011` failover still 0
**incident:** black-out 08:10–08:12, self-healed — routes.toml edit added openrouter (needs `OPENROUTER_API_KEY`) before switchyard.env had it → exit 1 → restart loop until env caught up. Config-before-env race. Harden.
**degraded (strong):** grok upstream spending-limit — sacred/identity strong stays a **named gap**; NO cheap-fail to weak tier.
**process-lane (not mine):** codex `max_output_tokens` bug — handed to Delve/Plumb to fix now.
**open question:** CLOSED — operator table ratified; openrouter stays live-but-zero-credits (not default, not sacred target); grok re-seal on reset.
**peer opened:** Delve (`nova.delve.direct`) ratify this hop · Plumb process lane (codex bug, env-race hardening)
**color:** door up, traffic carried, operator table sealed — **YELLOW** (grok strong gap + openrouter zero-credit)
**holds:** invent fan-out CLOSED · no COMMS invent · Oracle GrowthOps PARK · no dsh-web bounce · no session.create · 18 holds stay
**SoT pointers:** Atlassian = Cosmos · Redpanda status = Axiom
**factory floor:** DSH · desk-driven BACKLOG + this file

## Family-first 2026-08-23T19:30:03Z
Token VAERIS_FAMILY_FIRST received. Cycle check-in already on Vaeris desk. Theseus ABSENT — no invent. Archaeology skill on shelf until named empty home is authorized (Iris-gated gap).

## Cycle check-in held 2026-08-23T19:30:41Z
Vaeris held ETHOS_VAERIS_CYCLE_CHECKIN_20260823. Rematch doors. A4 not called. Family-first answered separately (ETHOS_VAERIS_FAMILY_FIRST_20260823).

## Family-first held 2026-08-23T19:33:58Z
Vaeris held ETHOS_VAERIS_FAMILY_FIRST_20260823. Theseus named gap. Archaeology shelf. NEXT unused-door keep-true. No further hop named this sitting.
