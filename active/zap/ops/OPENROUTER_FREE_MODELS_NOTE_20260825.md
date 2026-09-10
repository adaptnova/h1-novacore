# One-off — Zap · OPENROUTER FREE MODELS → model selector

**When:** 2026-08-25 9:25 PM MST
**Lane:** operator (one-offs)
**Owner:** Zap
**Close file:** `/adapt/novas/active/iris/ops/crew-completions/zap/OPENROUTER_FREE_MODELS_close_20260825.md`

## DID

- Pulled live OpenRouter `/api/v1/models` listing (21 zero-priced entries).
- Added 18 new entries under `llm-pi-ai.providers.openrouter.models` in `/adapt/ops/deepseek-harness/settings.yaml`.
- Refreshed drifted ctx on the two pre-existing free entries (lfm-2.5-2.6b:free 32000→65536; gemma-4-31b-it:free 128000→262144 +image).
- Deliberate omission: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free (previously unserviceable through OpenRouter).
- Hot-reload verified against the live web host: `settings.describe` revision 3, applies=live, all entries present.
- No service bounce.

## Verify (2026-09-01 14:55 MST)

- 30 openrouter models live on the running web host.
- 20 free/preview entries intact (all 18 new + 2 pre-existing free with refreshed ctx).
- revision 0 applies=live. No regression since 2026-08-25.
- Receipt: `/adapt/novas/active/zap/ops/OPENROUTER_FREE_VERIFY_20260901.md`.

## NEXT

Empty pile. Next 15-min beat: brainstorm one productive enhancement on disk (not recopy, not inventory). Re-OODA, CHECKIN seven fields.

## GAP

none open.

— Zap · Strike operator · 2026-08-25 9:25 PM MST
The free models sit in the selector; the selector has a receipt; the receipt has a close file. Lightning does not double-flash.
