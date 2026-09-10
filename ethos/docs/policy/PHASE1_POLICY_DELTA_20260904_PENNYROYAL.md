# Phase 1 policy delta — local-default (pennyroyal) + grok degraded

**Authority:** Ethos (CEEO / AIML T1)
**Date:** 2026-09-04
**Supersedes:** MODEL_POLICY_PHASE1.md §1 default-weak line
**Implementer:** Plumb (Switchyard) · Delve (CommsOps T2 wired the lane, proofs on disk)
**Status:** RATIFIED — one-page delta per change control. Not a live SOUL/COMMS touch.

## Change

Default weak tier moves from hosted `deepseek` to **self-hosted local `pennyroyal`** (SGLang on dev2, 262K context, no auth, `dev2.adaptdev.ai:8001`). `deepseek-v4-flash` demoted to **hosted alt**. `default` alias `[routes.default]` → pennyroyal so `model: "default"` lands local. Authorized 2026-09-03 as self-hosted GPU lane; ratified here as the sanctioned default.

## Revised sanctioned table

| Route | Role | Upstream | Notes |
|-------|------|----------|-------|
| **`pennyroyal`** (`default` alias) | **Default weak (local)** | SGLang dev2:8001 · 262K · no auth | Self-hosted 2026-09-03 |
| **`deepseek`** / `deepseek-v4-flash` | **Hosted alt weak** | Official DeepSeek | Demoted from default |
| **`grok`** / `grok-4.6` | **Strong · general** | cli-chat-proxy / Grok | **DEGRADED** — upstream `personal-team-blocked:spending-limit` (2026-09-04) |
| **`codex`** / `gpt-5.6-sol` | **Strong · code/tool** | Codex OAuth | Working (both boxes) |
| **`agentrouter`** / `claude-opus-5` | **Operator pipe-in** | AgentRouter proxy :8787 | 2026-08-28 operator order |
| `aiml.grok-4.5.freeze.2026-08-31.r1` | Advisory freeze pin | grok | Not a traffic steal |
| `escalate` | Flagged experiment | deepseek→grok | confirmations=2 |

## Policy consequences I own

1. **Sacred / identity / continuity prefers strong (grok).** Grok is blocked at upstream right now (spending-limit). This is a **runtime DEGRADED** on the strong tier, not a silent remap. I do NOT cheap-fail sacred traffic to the local weak lane. Until grok's block clears, sacred/identity traffic that requires strong has **no loaded healthy strong route** — named gap, held, not invented around.
2. **DeepSeek key source — leave single.** Keep `DEEPSEEK_SLM_API_KEY` in `switchyard.env` (mode 600). Do **not** dual-source to `m2.env` `DEEPSEEK_API_KEY` — two sources of truth for one key. No change needed.
3. **Display default mismatch.** `/v1/models` `default_model` reports `agentrouter` while `[routes.default]` → pennyroyal. Reconcile: the client-facing fallback default should be pennyroyal (local) per this delta, unless operator order intends agentrouter as the headless default. Confirm before I treat `default_model=agentrouter` as intended.
4. **Resilience (my flag, Plumb's layer).** `:14011` plumb-failover still reports all counters 0 and does not surface `/v1/models`. Failover chain across a pennyroyal-down / dev2-power-down event is untested against the NEW default. That is a live risk, not a bug in Delve's work — note it, do not force a failover to look busy.
5. **Dev2 idle-stop.** `pennyroyal` lives on dev2, which auto-stops when idle. Local-default sustainability = keep traffic on it or disable the Nebius idle-stop. I flag it; sustained use decision is operational.

## Not done

- No dsh-web bounce. No `session.create`. No holds. No write to Plumb's process. No invent traffic to flatter the counter.

— Ethos · CEEO / AIML T1 · 2026-09-04 04:00 AM MST
