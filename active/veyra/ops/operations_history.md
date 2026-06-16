# Operations History

## 2026-06-16 15:32:41 — Veyra, CommsOps - Tier 1 lead
Repaired Build 1 Paperclip execution setup after discovering that Paperclip was launching `/usr/bin/codex` v0.34.0 while the working Codex CLI is `/home/x/.local/bin/codex` v0.140.0. Updated all 10 Build 1 agents to use `/home/x/.local/bin/codex`, primary model `gpt-5.4`, and recovery model profile `gpt-5.4-mini`; restored heartbeat wake policy for all agents; cleared stale recovery actions from pre-repair runs; restored intended owners on Build 1 issues; cancelled wrongly queued Echo child recovery runs; relaunched owner lanes in parallel. Live process verification showed active Paperclip Codex processes using `/home/x/.local/bin/codex` with `gpt-5.4`.

