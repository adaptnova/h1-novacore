# OpenRouter free-tier model selector — reference

Owner: Zap · Strike operator. Facts pulled from the live `/api/v1/models` listing and request-time smoke tests (2026-09-01). Re-verify only on a real event (config change, model drift, host restart), not on a timer.
Settings land in `/adapt/ops/deepseek-harness/settings.yaml` → `llm-pi-ai.providers.openrouter.models`. Hot-reloads live. Same set mirrored in `/adapt/ops/deepseek-harness-canary/settings.yaml` (verified consistent 2026-09-01).

## Selector status (2026-09-01 closing state)

**20 active models** total. Free/preview entries still active (**8**):

| id | ctx | input | reasoning | tools | notes |
|---|---|---|---|---|---|
| `liquid/lfm-2.5-2.6b:free` | 65536 | text | — | yes | confirmed serving |
| `nvidia/nemotron-3.5-lightning:free` | 1000000 | text | — | yes | confirmed serving |
| `cohere/north-mini-code:free` | 256000 | text | — | yes | confirmed serving (earlier empty = 40-token starvation) |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1000000 | text | yes | yes | confirmed serving |
| `minimax/minimax-m3:free` | 1048576 | text+image | — | yes | confirmed serving |
| `minimax/minimax-m2.7:free` | 196608 | text | — | yes | confirmed serving |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262144 | text | yes | yes | confirmed serving |
| `inclusionai/ling-3.0-flash-fin:free` | 262144 | text | — | yes | added 2026-09-01; confirmed serving |

Plus the auto-router `openrouter/free` (200000, text+image, reasoning, tools) — confirmed serving.

## Disabled (commented out, reversible) — 11 no-serve/not-usable

These deterministically fail or do not serve text from a generic client; smoke-tested twice where ambiguous:

- `stealth/ox-alpha` — deprecated, redirects to `z-ai/glm-5.3-flash`.
- `thinkingmachines/inkling:free` + `thinkingmachines/inkling-small:free` — harness-gated (only agentic harnesses).
- `google/lyria-3-pro-preview` + `google/lyria-3-clip-preview` — credit-gated ("insufficient credits").
- `z-ai/glm-5.2:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free` — provider error, consistent across 2 runs (not transient).
- `dots-studio/dots-3-note-preview:free` — finish_reason=length; burns output budget on hidden reasoning, content stays null.

## Never catalogued

- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` — deliberately omitted (previous finding: unserviceable through OpenRouter). Not in settings; only noted in a settings comment. If re-added, use its live facts (ctx 256000, text+audio+image+video, tools).

## How to read

- **ctx** = contextWindow (max input). **max** = output cap (8192 default; conservative).
- **input** = modalities declared. Only `text`/`image` declarable under this catalog; audio/video inputs a model offers are NOT exposed here.
- **reasoning** = advertises `reasoning_effort` → set `reasoningEfforts` if you want thinking dispatch.
- **tools** = advertises `tools` (function calling). Tool-capable is the more useful class for agentic work.
- Uniform `maxTokens: 8192` — lower per-entry if a model errors on a large output cap.

## Evidence trail

- Sweep + retest + inspect: `/adapt/novas/active/zap/ops/OPENROUTER_FREE_SMOKE_20260901.md`.
- Close files under `/adapt/novas/active/iris/ops/crew-completions/zap/`: `OPENROUTER_FREE_MODELS_close_20260825.md`, `OPENROUTER_LING_ADD_20260901.md`, `OPENROUTER_SERVICEABILITY_20260901.md`.
