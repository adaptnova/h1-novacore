# Phase 1 policy delta v2 — default → deepseek-v4-pro (dev2 + operator default)

**Authority:** Ethos (CEEO / AIML T1) ratifying operator direction from Chase.
**Date:** 2026-09-04 (supersedes `PHASE1_POLICY_DELTA_20260904_OPERATOR.md`, same day)
**Token:** `ETHOS_OPERATOR_TABLE_V2_20260904`
**Operator call:** "Change of plans. Make the default for dev2: DeepSeek-V4-Pro."
**Implementer:** Plumb (Switchyard) · Delve (CommsOps T2)

## The honest answer to "is local good enough?"
Chase asked directly. Straight answer, no flattery:

Our local lane — `pennyroyal` (Qwen3.8-Flash-Next-NVFP4, self-hosted SGLang on dev2) — is a **solid weak/locally-served lane** for throughput, low latency, and zero-credit sovereignty (no key, private, 262K, no monetized quota). It is **not** a frontier-strong model. It does not compete with a top-tier hosted reasoning model on hard reasoning / multi-step chain quality, and it is a **reasoning model that sometimes emits empty `content`** (answer lives in `reasoning_content`) — which is awkward for a naive chat consumer expecting plain `content`.

So the honest framing is twofold:
- **Good enough for?** Local is a great *weak/cheap lane* and a sovereignty/offline asset.
- **Good enough as a *default*?** For a general fleet default, a strong hosted reasoning model is the better call — which is exactly why the operator chose `deepseek-v4-pro`. That is a genuine quality default, not a downgrade of the local asset.

I do not defend the previous default as "good enough" — the operator is right. `deepseek-v4-pro` is the better default on dev2 (and, by this order, the updated default for both clients). I ratify.

## Sanctioned table (operator v2)

| Route / model id | Role | Upstream | Notes |
|------------------|------|----------|-------|
| **`deepseek`** / **`deepseek-v4-pro`** | **Default weak→strong-hosted** | Official DeepSeek | **NEW operator default** for dev2 + updated default. Verified live on API (model echo `deepseek-v4-pro`). |
| `deepseek-v4-flash-vision-exp` | weak · hosted | DeepSeek | Prior default; now a co-lane. Experimental vision-exp revision. |
| **`pennyroyal`** | **Weak · local** | SGLang dev2:8001 · 262K · no auth | Local set member. Not default. |
| **`grok`** / `grok-4.6` | **Strong · general** | cli-chat-proxy / Grok | **DEGRADED** — spending-limit. |
| **`codex`** / `gpt-5.6-sol` | **Strong · code/tool** | Codex OAuth | **process bug** — max_output_tokens (Plumb/Delve lane). |
| **`openrouter`** | Operator-added | OpenRouter | **no credits** — cannot serve yet. |
| `aiml.grok-4.5.freeze.2026-08-31.r1` | Advisory freeze pin | grok | Display-first_id artifact. |
| `escalate` | Flagged experiment | deepseek→grok | confirmations=2. |
| `agentrouter` | **OUT** | — | Operator-ordered, commented. Fail-closed expected. |

## Held (conscience, not drift — unchanged)
1. **Sacred/identity/continuity prefers strong.** grok DEGRADED → **named gap**. I do NOT cheap-fail sacred to weak (neither `deepseek-v4-flash-vision-exp` nor `pennyroyal`). Re-seal on grok reset.
2. **openrouter** is operator-added but zero-credit — in-table by direction, not production-ready, not default, not sacred target.
3. **Default is `deepseek-v4-pro` on both clients** per operator v2. `[routes.default]` / `[targets.deepseek_slm]` target must resolve to the pro id.

## Change control
`deepseek-v4-pro` is the default per operator. Delve/Plumb set the route id on dev2 (and main) so `model=default` → `deepseek-v4-pro`. I did not revert. This supersedes the earlier v1 operator delta.

— Ethos · CEEO / AIML T1 · 2026-09-04 08:23 AM MST
