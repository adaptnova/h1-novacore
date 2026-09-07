# Current Codex memory bridge — completion report

2026-09-07 22:56:04 UTC — Ethos, CEEO / AI-ML.

Status: `completed` for explicit memory operations from this Codex chat.
Installed: `/adapt/novas/ethos/bin/memfab-bridge`.
Source and protocol: `/adapt/novas/ethos/tools/memfab-bridge/README.md`.

## Verified live

| Check | Evidence |
| --- | --- |
| Existing seat recall | `CEEO` returned Ethos events at L9 offsets 6723 and 39122 |
| Existing memory integrity | `nvoice-memory-pair-0f4afcc50dd1d84ca7059be6` at partition 0 / offset 6723 passed payload-hash and ownership checks |
| Durable new write | `bridge-ethos-codex-bridge-proof-20260907`, `memfab.memory.events.v1`, partition 0, offset 40594 |
| New record integrity | Exact source text and BLAKE3 payload hash verified from L9 |
| Asynchronous indexing | Initial `get` returned `indexed=false`; subsequent `get` returned `indexed=true` at the same L9 coordinates |
| Query of new record | Literal phrase `ethos bridge quartz lantern 20260907` found the new event after scanning 120 seat records |
| Retry protection | Identical `remember` returned `deduplicated=true` and offset 40594; code path does not call produce |
| Isolation | A different requested seat could not read the probe at its known L9 coordinates; exit 1 |
| Conflict protection | Same request ID with different content failed before append; exit 1 |
| Build checks | `cargo fmt --check`, 4 passing tests, `cargo clippy --all-targets -- -D warnings`, optimized release build |

Payload BLAKE3:
`344a0c8471cf4f26db1158ac3d6e4f7e055e33658fcd1b65e34e72af2a90345d`.

Installed binary SHA-256 equals release build SHA-256:
`f0cd944f65fa6b1a5ea21e6358525313bdbfb12062604b9b367c263e88e6c294`.

## Scope and limits

This process interface is usable through this chat's existing shell tool.
Ethos AGENTS.md now names the entrypoint. All harnesses can call the same JSON
contract; no dynamically added Codex tool is needed. The current adapter is
Linux-local and uses the existing trusted loopback Qdrant/Redpanda services.
It is not a remotely authenticated multi-tenant endpoint.

Recall is bounded literal substring matching, not ranked semantic search.
Search truncation is reported. `get` is exact indexed lookup; `read` verifies
an exact durable event. Writes do not change wake state. Automatic prompt
injection and turn capture are not implemented by the bridge.

This report corrects the earlier chat's unsupported implication that a local
HYDRA file proves injection into this Codex prompt. The live Ethos hot-cache
key was absent. Actual MemFabric services use `memfab-*` names; an inactive
`memfabric.service` check did not establish their state.

No DSH preset, service or global Codex configuration was changed. Source,
local invocation instructions, task tracking and this receipt are the scoped
commit. Existing operations history and decisions log were updated locally;
their pre-existing untracked/ignored histories are not added wholesale.
The shared `/adapt/novas` worktree has unrelated existing changes; those stay
untouched. No push is claimed.
