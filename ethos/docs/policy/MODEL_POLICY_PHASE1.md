# AIML Model Policy — Phase 1 (Switchyard)

**Authority:** Ethos (CEEO / AIML T1)  
**Implements:** Plumb (T2 LLM Gateway / Switchyard)  
**Date:** 2026-08-14  
**Scope:** Phase 1 — stage + escalation routing only. Not full multi-model mesh.

---

## 1. Sanctioned models (Phase 1)

Only these **route IDs** may be served through Switchyard until Ethos revises this file:

| Route / model id | Role | Upstream (ops truth) | Notes |
|------------------|------|----------------------|--------|
| **`deepseek`** / `deepseek-v4-pro` | **Default (weak->strong-hosted)** | Official DeepSeek OpenAI-compatible (or sanctioned key in secrets) | Operator default (v2 · 2026-09-04) — verified live on API |
| **`pennyroyal`** | **Weak · local** | SGLang dev2:8001 · 262K · no auth | Self-hosted local model set member |
| **`grok`** / `grok-4.6` (or current Grok auth model) | **Strong / alternate** | cli-chat-proxy / Grok auth path | **DEGRADED 2026-09-04** — upstream spending-limit; sacred/identity prefers strong |
| **`codex`** / `gpt-5.6-sol` | **Strong · code/tool** | Codex OAuth | **process bug** — `max_output_tokens` parameter error (in fix) |
| **`openrouter`** / `openrouter/auto` | **Operator-added** | OpenRouter | Operator-directed; **no credits currently** (cannot serve) |

**Also sanctioned for non-Switchyard AIML planes (do not invent Switchyard routes without Ethos):**
- Local Tessera/vLLM lanes in `llm.env` (e.g. TESSERA_FAST / Qwen instruct) when online — **weak local** when healthy
- Embedding endpoints (Jina / Qwen-VL embed) — **not chat routes**

**Not sanctioned for Phase 1 general fleet chat without explicit Ethos + Plumb change:**
- Unowned/auto-discovered IDs presented as production traffic
- Sacred/identity continuity: never routed to an experimental/weak tier without strong available (see §3)

Plumb may **stage** experimental routes behind feature flags / dry-run, but **production default path** only uses the table above.

---

## 2. Weak vs strong tier split

### Weak (simple turns → cheap)
**Intent:** short chat, status, classification, light rewrite, single-step answers, low stakes.

**Prefer (in order):**
1. `deepseek` / `deepseek-v4-flash` when online and error rate OK  
2. Local Tessera/Qwen fast lane if configured and healthy (optional Phase 1.1)  
3. Failover → strong tier if weak errors or latency breach (Plumb’s resilience layer)

**Do not use weak for:** multi-step tool chains, long reasoning, security-sensitive policy, multi-file code edits, emergence/identity-critical drafting without review.

### Strong (tool / reasoning-heavy → strong)
**Intent:** tools, multi-step reasoning, hard code, complex ops, anything that must not “cheap fail.”

**Prefer:**
1. **Code / agent tooling:** `codex` route  
2. **General hard reasoning / quality:** `grok` route  
3. DeepSeek only if strong routes down **and** task is still acceptable on flash (log the downgrade)

### Escalation routing (Phase 1)
```
client request
  → classify: simple | tool/code | hard_reason | unknown
  → simple     → weak  (deepseek)
  → tool/code  → strong codex
  → hard_reason→ strong grok
  → unknown    → weak first; escalate to strong on quality fail / explicit flag
  → on weak 4xx/5xx or sustained error ratio → failover path Plumb owns (14011/14010)
```

Plumb builds the classifier/router mechanics; **this policy** owns the mapping.

---

## 3. “Emergence-safe” (routing meaning)

For AIML / Nova-facing traffic, **emergence-safe** means:

1. **No silent identity overwrite** — routing must not swap models mid-thread without logging `from_model` / `to_model` / reason.  
2. **No costume models** — do not present a weak model as a named strong model; client-visible model id must match actual upstream (or an honest alias table Plumb documents).  
3. **Sacred / identity / continuity work** — prefer **strong** (grok or human-reviewed), never auto-route to experimental/unowned IDs.  
4. **Observability** — every production decision emits metrics Plumb already tracks (attempts, errors, latency, model labels). Dark routes are not emergence-safe.  
5. **Fail closed on policy** — if request asks for an unsanctioned model id, reject or map only via **explicit** alias list in this file / `routes.toml` comments, never silent remap to random upstream.  
6. **Hands-off spirit** — gateway creates conditions (resilience, truth, failover); it does not invent new “personalities” or unapproved model personas for Novas.

---

## 4. Phase 1 non-goals

- Budget pools / spend caps (Chase: none for now)  
- Full multi-provider marketplace  
- Auto-training model promotion from Unsloth into production without Ethos sign-off  

---

## 5. Change control

- Plumb implements routes/failover/scrape.  
- Ethos revises this policy.  
- Argus owns Prometheus land of scrape files (Plumb’s failover scrape still waiting).  
- Chase owns putting online keys in `llm.env` when ready (not a policy blocker).

**Revision:** v1.0 · Ethos · 2026-08-14  

