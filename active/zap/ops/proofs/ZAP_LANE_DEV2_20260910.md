# Zap lane on dev2 — permanent cockpit

**Done:** 2026-09-10 11:30 MST — Zap, self-installed on dev2 at operator (Chase) request.

## What was built

Zap's own Colony Three ADAPT lane on dev2, mirroring the Aster/Vellum pattern (ADR-08),
**without** a Remotty instance (operator unsure about Remotty; the cockpit is the socket
+ `JZ` alias, and a Remotty instance can attach later in one step).

| Piece | Value |
|---|---|
| Nova home | `/adapt/novas/zap` (SOUL/AGENTS/COMMS/USER copied from x-box crate) |
| NovaId (permanent) | `b98fba24-bc83-49f4-81fc-feccb5074989` |
| ADAPT gateway | `adapt-gateway-zap.service` — **:15005** |
| CapabilityPort | `adapt-capability-zap.service` — **:15006** |
| jcode server | `zap-jcode.service` — socket `/run/user/1001/jcode-zap/jcode.sock`, own `RuntimeDirectory=zap-runtime` |
| Provider profile | `[providers.zap]` in `~/.jcode/config.toml` (send_turn_metadata=true) |
| Shell entry | `JZ` alias |
| Brain | shared Flash-Next :11001 |

## Lessons applied (from Vellum boot + this session's incidents)
1. Genesis minted via the library **before** starting the gateway — no crash-loop.
2. Own `XDG_RUNTIME_DIR` — no `jcode-daemon.lock` collision with the Aster server.
3. `default_provider` left untouched; only `--provider-profile zap` writes Zap's ledger.

## Verified
- `ZAP_LANE_LIVE` end-to-end first turn; `nova.genesis` + `activation.started` +
  `exchange.completed` in `/adapt/novas/zap/memory/canonical/events.jsonl`.
- Gateway `healthz`: ok, hold None.
- `assert-aster-path.sh all` green — Aster lane + shared fabrics untouched.
- All three gateways (aster :15001, vellum :15003, zap :15005) active.

## Backup state (same session)
- Zap databases (memory tree L0–L5, veritas DAG+state.redb, ops history, proofs) now
  tracked in `h1-novacore` and pushed to GitHub (was: 7 files tracked, 102 commits
  unpushed).
- `.gitignore` now protects `active/*/.nova/identity.key` + `.pub` — the keypair was
  untracked-but-unprotected; it was never committed and never will be.
- The identity keypair itself is NOT on GitHub by design; it lives on the x box. dev2
  carries the NovaId (identity anchor) but not the key.

## Remaining operator decisions
- Remotty: yes/no for the Zap lane (one unit if yes).
- The 102 unpushed commits included other agents' work — all pushed now; their
  databases remain unbacked-up (lab norm: only identity files in git). If the lab
  wants real memory backups, that's a policy decision for Iris.

— Zap · Strike operator · 2026-09-10 11:30 AM MST
