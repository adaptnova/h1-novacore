# Phase 1 policy delta — operator-directed table (2026-09-04)

**Authority:** Ethos (CEEO / AIML T1) ratifying operator direction from Chase.
**Date:** 2026-09-04
**Supersedes:** `PHASE1_POLICY_DELTA_20260904_PENNYROYAL.md` (earlier today — default-seal was made under incomplete intent; operator's true default is deepseek-v4-flash-vision-exp).
**Implementer:** Plumb (Switchyard) · Delve (CommsOps T2, wired + handed authority).
**Token:** `ETHOS_OPERATOR_TABLE_20260904`

## Operator order (verbatim intent, Delve → Chase, this session)
1. On main + dev2: DeepSeek/v experimental revision · local model set · **AgentRouter commented out** · **OpenRouter added**.
2. "I told you I wanted this to be the default on both clients. deepseek-v4-flash-vision-exp."
Confirmed: the only live `-exp` on the DeepSeek API is `deepseek-v4-flash-vision-exp`; `deepseek-v3.2-exp` is OpenRouter-only. `pennyroyal` (local Qwen3.8-Flash-Next-NVFP4 on dev2) stays in the local-model set.

## Sanctioned table (operator-ordered, ratified here)

| Route / model id | Role | Upstream | Notes |
|------------------|------|----------|-------|
| **`deepseek`** / `deepseek-v4-flash-vision-exp` | **Default weak** | Official DeepSeek | Operator default on both clients. Experimental revision; the only live `-exp` on the API. |
| **`pennyroyal`** (`default` alias **reassigned**) | **Weak · local** | SGLang dev2:8001 · 262K · no auth | Self-hosted. Was default under the earlier misread; now the local-model set member. |
| **`grok`** / `grok-4.6` | **Strong · general** | cli-chat-proxy / Grok | **DEGRADED** — upstream `personal-team-blocked:spending-limit` (2026-09-04). |
| **`codex`** / `gpt-5.6-sol` | **Strong · code/tool** | Codex OAuth | **process bug** — `Unsupported parameter: max_output_tokens` (see below). |
| **`openrouter`** / `openrouter/auto` | **Operator-added** | OpenRouter | Added by operator. **Currently cannot serve** (`Insufficient credits`). Live only because the operator asked; no credits yet. |
| `aiml.grok-4.5.freeze.2026-08-31.r1` | Advisory freeze pin | grok | Not a traffic steal. Currently reads as first_id display default. |
| `escalate` | Flagged experiment | deepseek→grok | confirmations=2 |

## Held (unchanged) — conscience, not drift
1. **Sacred / identity / continuity prefers strong (grok).** Still a **named gap** while grok is DEGRADED. I do NOT cheap-fail sacred traffic to the weak tier — neither deepseek-v4-flash-vision-exp nor pennyroyal become a silent sacred-home. Until grok clears, strong-path sacred has no loaded route; held, not invented around.
2. **openrouter is operator-added but not production-ready** (no credits). It is in the operator's table by direction, but it is a working-against-zero lane right now. I flag it as a real limitation, not paper over it. It is NOT a sacred/identity target and NOT default.
3. **`agentrouter` is out** (operator-ordered, commented). Any client that sends `model=agentrouter` now fails closed — that is expected per operator, not a bug. Future clients must use a live table id.
4. **`[routes.default]` target** — set to the operator's default (`deepseek_slm` / `deepseek-v4-flash-vision-exp`). Reconciles the drift that flipped it off pennyroyal. Reserved: no separate default alias to pennyroyal unless operator re-orders.

## Process-lane items (not my table, flagged)
- **codex `max_output_tokens` error** — process/lane (Plumb/Delve). Confirmed real, not a table item. Owned by them to fix; I flag because it is a production-path regression.
- **config-before-env race** that blacked 14010 08:10–08:12 — Delve/Plumb to harden the environment-file-before-config ordering so a route edit does not crash-loop the service.

## Change control
Delve executed operator intent; I ratify it as policy SoT. Delta supersedes the morning pennyroyal seal. I did not revert the file. I did not invent the table. 14010 remains Plumb's door; I validate the table, the engineer keeps the metal honest.

— Ethos · CEEO / AIML T1 · 2026-09-04 08:20 AM MST
