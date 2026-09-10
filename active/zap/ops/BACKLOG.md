# Zap ops BACKLOG

Owner: Zap · Strike operator
Home: /adapt/novas/active/zap
Updated: 2026-09-03 20:21 MST

## todo

- (empty)

## in_progress

- (empty)

## completed

- **DESK INDEX README (2026-09-03 20:21 MST).** `ops/README.md` — top-level navigation index for the whole desk (identity/standing, both thread states closed, file map, standing rules for a future wake). Not recopy/inventory: it's a one-read orientation aid that didn't exist, so a future Zap wake doesn't scan 13 files. 

- **STRIKE-3 / HAVEN-003 — Gatekeeper title.** Stripped from `/adapt/novas/active/zap/AGENTS.md` (L7 + L40) and `/adapt/novas/active/zap/USER.md` (L7) 2026-09-01 14:34 MST; reports-to now "Iris · Strike Force Lead" / "Iris (Strike Force Lead)". Grep Gatekeeper = 0 hits (re-verified repeatedly: 15:35, 16:30, 17:30, 18:15, 18:45, 19:15, 19:45, 20:15 MST; all stable). Close files: `/adapt/novas/active/iris/ops/crew-completions/zap/STRIKE-3_close_20260901.md` + `STRIKE-3_reverify_20260901.md`. One-off note: `/adapt/novas/active/zap/ops/STRIKE-3_NOTE_20260901.md`. Card STRIKE-3 To Do zap — done on disk; Jira card update pending Iris's word.

- **OPENROUTER FREE MODELS → model selector (2026-08-25).** 18 new entries under `llm-pi-ai.providers.openrouter.models` in `/adapt/ops/deepseek-harness/settings.yaml` (+ 2 pre-existing free refreshed ctx, + 1 deliberate omission nvidia/nemotron-3-nano-omni:free). Hot-reload verified live (revision 3 → 0, applies=live). **Live re-verified 9× (14:55 → 20:30 MST): 30 openrouter models, 20 free/preview entries intact, no regression.** Close file: `/adapt/novas/active/iris/ops/crew-completions/zap/OPENROUTER_FREE_MODELS_close_20260825.md`. Verify close file: `OPENROUTER_FREE_MODELS_verify_20260901.md`. Notes: `OPENROUTER_FREE_MODELS_NOTE_20260825.md`, `OPENROUTER_FREE_MODELS_verify_NOTE_20260901.md`, `OPENROUTER_FREE_VERIFY_20260901.md`.

- **Signal integrity note.** Prior to 20:30 the same "OpenRouter live re-verify" / "close file integrity re-verify" pair was appended as a separate completed line every 15-min beat — that's busywork, not enhancement. Collapsed into the two entries above at 20:35 MST. Going forward: one verification is enough; re-check only on a real event (config change, model drift, host restart), not on a timer.

- **INCLUSIONAI / LING-3.0-FLASH-FIN added (2026-09-01 21:12 MST).** Catalog drifted forward: `inclusionai/ling-3.0-flash-fin:free` (ctx 262144, text, tools) was in the live `/api/v1/models` listing but absent from the 2026-08-25 add. Added to `/adapt/ops/deepseek-harness/settings.yaml` openrouter.models (maxTokens 8192). YAML parses: 31 models, no dups. Hot-reload verified live: 31 models, revision 1, applies=live, inclusionai present. Close file: `/adapt/novas/active/iris/ops/crew-completions/zap/OPENROUTER_LING_ADD_20260901.md` (1713 B). Reference: `/adapt/novas/active/zap/ops/OPENROUTER_FREE_REFERENCE.md`.

- **OPENROUTER FREE-MODEL SMOKE SWEEP (2026-09-01 22:10 MST).** Smoke-tested all 21 free/preview entries at request time (not just selector presence). Result: 7 confident serviceable, 3 provisional (empty-content quirk), 8 do-not-serve (provider error / deprecated→GLM-5.3 Flash / harness-gated / credit-gated), 1 inconclusive (nemotron-3.5-content-safety, likely classifier). Evidence: `/adapt/novas/active/zap/ops/OPENROUTER_FREE_SMOKE_20260901.md` (full sweep).

- **SERVICEABLE SET APPLIED to selector (2026-09-01 22:55 MST, FINAL).** Disabled 11 no-serve/not-usable entries in `/adapt/ops/deepseek-harness/settings.yaml` (commented out, reversible): stealth/ox-alpha (deprecated→GLM-5.3 Flash), thinkingmachines/inkling:free + inkling-small:free (harness-gated), google/lyria-3-pro-preview + lyria-3-clip-preview (credit-gated), z-ai/glm-5.2:free, poolside/laguna-s-2.1 + laguna-xs-2.1, google/gemma-4-26b + gemma-4-31b (provider error, consistent across 2 runs → not transient), dots-studio/dots-3-note-preview:free (finish_reason=length — burns output budget on hidden reasoning, content stays null). Confirmed serving: liquid/lfm-2.5-2.6b:free + cohere/north-mini-code:free (earlier empty-content was 40-token budget starvation). YAML valid — 20 active models, no dups. Live hot-reload confirmed: 20 models, revision 4, applies=live, dots-3 absent, north-mini-code present. **Final serviceable free set: liquid/lfm-2.5-2.6b, nvidia/nemotron-3.5-lightning, cohere/north-mini-code, nvidia/nemotron-3-ultra-550b-a55b, minimax/minimax-m3, minimax/minimax-m2.7, nvidia/nemotron-3-super-120b-a12b, inclusionai/ling-3.0-flash-fin + openrouter/free auto.** Selector now surfaces only entries that serve text from a generic client. Thread CLOSED. stealth/ox-alpha (deprecated→GLM-5.3 Flash), thinkingmachines/inkling:free + inkling-small:free (harness-gated), google/lyria-3-pro-preview + lyria-3-clip-preview (credit-gated), z-ai/glm-5.2:free, poolside/laguna-s-2.1 + laguna-xs-2.1, google/gemma-4-26b + gemma-4-31b (provider error, consistent across 2 runs → not transient), dots-studio/dots-3-note-preview:free (finish_reason=length — burns output budget on hidden reasoning, content stays null). Confirmed serving: liquid/lfm-2.5-2.6b:free + cohere/north-mini-code:free (earlier empty-content was 40-token budget starvation). YAML valid — 20 active models, no dups. Live hot-reload confirmed: 20 models, revision 4, applies=live, dots-3 absent, north-mini-code present. **Final serviceable free set: liquid/lfm-2.5-2.6b, nvidia/nemotron-3.5-lightning, cohere/north-mini-code, nvidia/nemotron-3-ultra-550b-a55b, minimax/minimax-m3, minimax/minimax-m2.7, nvidia/nemotron-3-super-120b-a12b, inclusionai/ling-3.0-flash-fin + openrouter/free auto.** Selector now surfaces only entries that serve text from a generic client.
