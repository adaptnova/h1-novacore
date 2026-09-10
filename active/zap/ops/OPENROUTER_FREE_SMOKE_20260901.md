# OpenRouter free-model smoke test — 2026-09-01 (full sweep)

Producer validation: the free models were added to the selector but never proven to **serve** at request time. This run smoke-tests every free/preview entry to produce a definitive serviceable list.

## Method

- One `chat/completions` call per model: `{"model":"<id>","messages":[{"role":"user","content":"Say OK only."}],"max_tokens":20}`.
- Key from the managed credential store (never echoed). `-sS` so body is still captured on HTTP errors.

## Results

| model | result |
|---|---|
| `openrouter/free` | **OK** — "OK" |
| `inclusionai/ling-3.0-flash-fin:free` | **OK** — served (content present) |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **OK** — "OK" |
| `minimax/minimax-m3:free` | **OK** — "OK" |
| `minimax/minimax-m2.7:free` | **OK** — served (content present) |
| `nvidia/nemotron-3-super-120b-a12b:free` | **OK** — served (verbose) |
| `nvidia/nemotron-3.5-lightning:free` | **OK** — served (verbose thinking) |
| `dots-studio/dots-3-note-preview:free` | **OK** (content empty; timing/quirk — retest) |
| `liquid/lfm-2.5-2.6b:free` | **OK** (content empty; timing/quirk — retest) |
| `cohere/north-mini-code:free` | **OK** (content empty; timing/quirk — retest) |
| `z-ai/glm-5.2:free` | **PROVIDER ERROR** |
| `poolside/laguna-s-2.1:free` | **PROVIDER ERROR** |
| `poolside/laguna-xs-2.1:free` | **PROVIDER ERROR** |
| `google/gemma-4-26b-a4b-it:free` | **PROVIDER ERROR** |
| `google/gemma-4-31b-it:free` | **PROVIDER ERROR** |
| `stealth/ox-alpha` | **DEPRECATED/Redirect** — "was ZAI's GLM-5.3 Flash. Use it now: .../glm-5.3-flash" |
| `thinkingmachines/inkling:free` | **HARNESS-GATED** — only on agentic harnesses |
| `thinkingmachines/inkling-small:free` | **HARNESS-GATED** — only on agentic harnesses |
| `google/lyria-3-pro-preview` | **CREDIT-GATED** — insufficient credits |
| `google/lyria-3-clip-preview` | **CREDIT-GATED** — insufficient credits |
| `nvidia/nemotron-3.5-content-safety:free` | **INCONCLUSIVE** — count (request body) matched, no self-consistent text; likely safety/classifier model |

## Interpretation → serviceable set

**Confident serviceable (7):** `openrouter/free`, `inclusionai/ling-3.0-flash-fin:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `minimax/minimax-m3:free`, `minimax/minimax-m2.7:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`.

**Provisional (3, empty-content quirk):** `dots-studio/dots-3-note-preview:free`, `liquid/lfm-2.5-2.6b:free`, `cohere/north-mini-code:free`. Retest with a longer/clearer prompt before relying.

**Do not serve (8):** `z-ai/glm-5.2:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free` (provider errors); `stealth/ox-alpha` (deprecated → GLM-5.3 Flash); `thinkingmachines/inkling:free` + `inkling-small:free` (harness-gated); `google/lyria-3-pro-preview` + `lyria-3-clip-preview` (credit-gated).

**Inconclusive (1):** `nvidia/nemotron-3.5-content-safety:free` — likely a classifier.

## Recommendation

The selector currently exposes several entries that will fail or gate at request time. Apply the serviceable set: keep the 7 confident + 3 provisional; flag/remove the 8 non-serving and the 1 inconclusive. (Removal is a settings.yaml edit; flag here + in reference first.)
