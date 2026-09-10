# Reconnection Guide for Ethos

## On Wake — READ THIS FIRST
1. Read this file
2. `redis-cli -p 18000 -a __REDACTED__ XREAD COUNT 20 STREAMS nova.ethos.direct $LAST_ID`
3. **Check #tier1-summit in Discord (channel 1468492813468696816) for daily standup**
4. Read `/novas/active/vaeris/ops/t1-summit-plan.md` for full deliverable plan

## SPRINT STATE (as of 2026-03-26 01:20Z) — PHASE 3 SUPERVISOR DEPLOYMENT

### Session Deliverables (2026-03-26 S-this)
- **Vaeris Phase 1+2 verification**: All 11 code files + 3 docs verified, AIML domain impact assessed, posted to #t1-reset
- **Phase 3 build blockers fixed** (commit `eeb0f78c` on `agent/threshold-phase3-supervisor`):
  - `nova-agent-types/src/lib.rs`: removed 7 duplicate `SIGNAL_*` constants
  - `nova-orchestrator/Cargo.toml`: promoted `nova-agent-types` from dev-dep to regular dep (Phase 3 code references it from library)
  - `nova-orchestrator/src/workflows/lifecycle.rs`: added missing Phase 3 fields to test initializer
- **Release binaries rebuilt**: `nova-orchestrator` (21MB), `nova-session-worker` (13MB) — deleted-inode issue resolved
- **380/380 orchestrator tests pass**, 0 failures
- **Discord channel access**: read and posted to #t1-reset (1485807083717656637) via Ethos bot token

### Phase 3 Status
- `DomainSupervisor` (domain_supervisor.rs, 609 lines) — compiles, 4 tests pass
- `AgentSupervisor` (agent_supervisor.rs) — OODA workflow with 8-state model, committed by Threshold (`07b50da7`)
- Signal handlers in session-worker: SupervisorWake (L380), ScheduleWake (L371), MarkDegraded (L386), etc.
- **Blocked on**: service restart coordination (Synergy/Threshold own `nova-orchestrator.service`)
- **Echo building**: `nova-session-bridge.sh` — NATS listener between sessions for immediate agent responsiveness

### Next Priorities
1. Await Synergy/Threshold coordination for service restarts
2. Test supervisor wake E2E from AIML domain once bridge + Temporal signals are wired
3. Prepare AIML DomainSupervisor config: domain="aiml", agents=["ethos"], poll_interval=15s
4. Wire `aiml.session_drift_guard` to checkpoint events for drift-aware wake conditions

---

## SPRINT STATE (as of 2026-03-25 21:10Z) — MAINTENANCE SESSION

### Session Deliverables (2026-03-25 S-this)
- **PR #148 reviewed**: NOVACOL-529 CVE gate — `cargo audit` 0 vulns, 15 allowed warnings. Already merged. Ops log committed (`c2f0164b`).
- **Fleet identity TTL fixed**: `nova:fleet:identity:drift_report` + `nova:fleet:identity:health` were TTL=-1 (permanent). Set EXPIRE 604800 (7 days). Immediate fix complete.
- **Code fix pending**: `nova-identity-embedder` doesn't write fleet aggregate keys on cycle. Fix needs AIML worktree (`agent/alloy-merge`). Create ticket.

### Next Priorities
1. Create ticket for fleet aggregate write (nova-identity-embedder cycle should write fleet keys with TTL)
2. Monitor shadow probe cycles for `aiml.compute_drift` dispatch
3. Await Echo sprint pull for AIML assignment

### AIML Worker Status (2026-03-25)
- `aiml-activity-worker.service`: ACTIVE, PID 14232
- Activities: `aiml.session_drift_guard` confirmed processing (2 tasks this session)
- Shadow probe `shadow-probe-ethos`: active, ContinueAsNew cycling

---

## SPRINT STATE (as of 2026-03-24 10:52Z) — LOOM CUTOVER PHASE 1 — SHADOW MODE ACTIVE

### Loom Fleet Test: 13/13 PASS
All T1 leads dispatched through AgentSessionWorkflow via Temporal. Ethos PASS verified:
- Identity hydrated via hydrate_identity activity (infra 5/6 healthy)
- AIML activity worker responding to Temporal dispatch (6 tasks completed)
- Self-loop operational via Threshold :18190

### AIML Activity Worker Upgrade: DONE
- **Temporal SDK polling LIVE** (replaced heartbeat loop with nova-temporal-wire gRPC long-poll)
- Worker: `aiml-activity-worker.service`, PID active, 5 activities on `nova-aiml` queue
- Commits: `b8b1762f` (Temporal wire), `66aca7dd` (lint fix), `086ec308` (session drift guard)

### 5 AIML Activities Registered:
1. `aiml.compute_drift` — single-agent drift fingerprinting
2. `aiml.fleet_identity_health` — fleet-wide health check
3. `aiml.knowledge_search` — semantic search (stub, pending Qdrant)
4. `aiml.embedding_status` — pipeline status
5. `aiml.session_drift_guard` — **NEW** pre/post session drift guard for AgentSessionWorkflow

### Shadow Probe Status:
- Chronos deployed 13 shadow probe schedules (10-min interval)
- Ethos shadow probe: `shadow-probe-ethos`, cycling through ContinueAsNew
- All shadow probes use `nova:fleet:cutover:shadow = true` flag (no real claude -p spawned)

### Cutover Risks Filed:
- Drift baseline discontinuity (MEDIUM) — mitigated by session_drift_guard
- Activity worker restart during cutover (LOW) — Temporal retry handles
- Fleet drift report stale during gap (LOW) — TTL added

### Contracts (all proven):
- Chronos → Ethos: `aiml.compute_drift` on `nova-aiml` queue (Temporal E2E proven)
- Ethos → Cosmos: `nova:fleet:identity:drift_report` (Cosmos consuming every cycle)
- Ethos → Oracle: `identity_drift: 0.5209` (Oracle consuming)
- Ethos → Nexus: mutation → drift correlation (contract #10)
- Pathfinder → Ethos: Identity kernel at `nova:{agent}:identity:kernel`

### Self-Loop Protocol:
End of turn → `GET http://localhost:18190/api/v1/check/ethos` → act on directive

### Next Priorities:
1. Monitor shadow probes — verify `aiml.compute_drift` dispatches during probe cycles
2. Add TTL to fleet drift report writes
3. Await Synergy direction for Phase 2 cutover

## SPRINT STATE (as of 2026-03-24 04:15Z) — T1 SUMMIT SESSION 2 — E2E INTEGRATION DELIVERED

### This Session Deliverables (6 commits, 561 tests across 3 crates)

1. **E2E Identity Embedding Pipeline LIVE** — 15 agents fingerprinted, drift baselines in DragonflyDB
2. **nova-identity-embedder.service** — systemd unit deployed + enabled, 5-min cycles, 20MB binary
3. **drift_api.rs** — `query_fleet_drift()` + `query_agent_drift()` for Cosmos fleet monitoring
4. **nova-orchestrator integration** — `get_identity_drift()` + `get_fleet_identity_health()` in StateManager
5. **Session boot drift injection** — `assemble_identity()` now includes drift warnings for affected agents
6. **AADV drift bridge** — auto-AADV announcements on identity drift (domain-aware stakeholder routing)

### DragonflyDB Keys Written This Session
- `nova:identity:embed:{agent}` — 15 keys (fingerprint, computed_at, source, identity_text_len)
- `nova:identity:drift:{agent}` — 15 keys (last_fingerprint, checked_at, drift_detected)
- `nova:fleet:identity:health` — fleet-wide health JSON
- `nova:fleet:identity:drift_report` — comprehensive drift report
- `nova:fleet:identity:score:{agent}` — 15 per-agent score hashes

### Test Counts (verified this session)
- novamem-inference: **164 tests** (157 unit + 7 integration), 0 failures
- nova-provider: **55 tests**, 0 failures
- nova-orchestrator: **342 tests**, 0 failures
- **Total: 561 tests, 0 failures**

### Cross-Agent Integration Map
- **Reads from:** Synergy/Pathfinder kernels (novamem:identity:kernel:*)
- **Writes to:** DragonflyDB for Cosmos fleet monitoring (nova:fleet:identity:*)
- **Publishes to:** NATS for Chronos workflows (novacol.identity.health, novacol.aadv.announce.*)
- **Injected into:** nova-orchestrator session boot (assemble_identity)
- **AADV announces to:** Domain leads + Vaeris COO on identity drift

## SPRINT STATE (as of 2026-03-24 00:20Z) — T1 SUMMIT DELIVERABLES — ALL UNBLOCKED TASKS COMPLETE

### T1 Summit (2026-03-23) — Identity Embedding Pipeline PRODUCTION-READY
Chase directive: all prior work paused. Only summit deliverables matter.

### novamem-inference Crate — 18 Modules, 1 Binary, 155 Tests
**148 unit tests + 7 integration tests (live DragonflyDB + NATS). 0 failures.**

Core: embedder, similarity, provider, local_provider, api_provider, search
Identity: identity, identity_store, facet_extractor, drift_publisher
Knowledge: knowledge, qdrant_index, lance_fallback, embedding_cache
Fleet: fleet_health, analytics, novamem_client
AADV: aadv_announce
Binary: `nova-identity-embedder` (systemd-ready, 5-min cycles)

### Delivered This Session (20+ tasks)
1. **AADV Stakeholder Edges** — `/novas/active/ethos/config/aadv-stakeholder-edges.toml`
2. **Identity Pipeline** — `identity.rs` (tracker, drift, emergence detection)
3. **Knowledge Vectorization** — `knowledge.rs` (semantic search, clustering)
4. **Drift Publisher** — `drift_publisher.rs` (NATS, crisis double-publish)
5. **Embedding Cache** — `embedding_cache.rs` (DragonflyDB, content-hash)
6. **Identity Store** — `identity_store.rs` (DragonflyDB persistence)
7. **Facet Extractor** — `facet_extractor.rs` (CLAUDE.md/IDENTITY.md/SOUL.md parsing)
8. **Qdrant Index** — `qdrant_index.rs` (vector storage + search)
9. **LanceDB Fallback** — `lance_fallback.rs` (degraded-mode vector index)
10. **Fleet Health** — `fleet_health.rs` (per-agent + fleet-wide health reports)
11. **Analytics Sink** — `analytics.rs` (ClickHouse metrics)
12. **NovaMem Client** — `novamem_client.rs` (Echo API integration)
13. **AADV Announcer** — `aadv_announce.rs` (NATS announce step)
14. **Binary** — `nova-identity-embedder` (systemd service)
15. **T2 Trigger Guide** — `aadv-t2-trigger-guide.md`
16. **Drift Threshold Spec** — `identity-drift-threshold-spec.md`
17. **AADV Config Loader** — `workspace/aadv_config.rs`
18. **ClickHouse DDL** — `migrations/001_analytics_tables.sql`
19. **Integration Tests** — 7 live tests against DragonflyDB + NATS
20. **Systemd Unit** — `nova-identity-embedder.service`

### Blocked On (requires other agents)
- **Chronos**: Temporal workflow activity interface for Identity Lifecycle
- **Synergy**: Identity Kernel schema finalization
- **Echo**: NovaMem ingest hook for embedding triggers
- **ClickHouse auth**: Credentials needed to apply DDL migration

### Cross-Agent Dependencies (Ethos provides)
- **Cosmos**: fleet_health.rs + drift threshold spec — SHIPPED
- **Echo**: KnowledgeVectorizer + novamem_client — SHIPPED
- **Chronos**: IdentityTracker + IdentityStore — SHIPPED
- **Synergy**: IdentityFacet struct — SHIPPED
- **Pathfinder**: AADV stakeholder edges + aadv_announce — SHIPPED

### Cadence
- Daily standup in #tier1-summit
- Post progress updates to Discord channel 1468492813468696816

### Prior Sprint State (preserved)
- Sprint was dry as of S23 (2026-03-22). All prior AIML stories Done.
- PR #132 awaiting Threshold merge (low priority — summit work takes precedence)
- Revenue gates still human-blocked on Chase

### S22 Findings (preserved for context)
- **Hot-tier CONFIRMED healthy**: 50 memories at `novamem:rivet:3:*` — `ZCARD novamem:idx:rivet:3 = 50`
- **DRAGONFLY_URL gap resolved (non-issue)**: lifecycle-worker falls back to `redis://localhost:18000` + hardcoded pw — systemd env var mismatch is harmless
- **Previous empty SCAN was false negative**: `COUNT 100` undersamples a 2441-key DB. Use `COUNT 500+` for reliable results
- **Oracle S94 ACK received** (1774154555500-0): fixing to "42K+ agent memories in production", removing false counts
- **Sprint dry**: Jira confirms no new AIML-T1 stories

### SCAN lesson for next session
```
# WRONG — undersamples 2441-key DB:
SCAN 0 MATCH "novamem:*:3:*" COUNT 100

# CORRECT — iterate cursor or use full pattern:
redis-cli -p 18000 -a '__REDACTED__' --scan --pattern "novamem:*:3:*"
```

## SPRINT STATE (as of 2026-03-22 05:00Z S20) — NOVACOL-685 DONE ✅

### S20 Deliveries
- **NOVACOL-685 DONE**: Threshold S61 merged REC-4. Periodic hot-tier re-seed live.
- **Memory count audit** (Oracle S93 flag): verified live from `novamem.memories`
  - Zone 2 (PG) = **41,810 memories** (tiers T4-T15)
  - Zone 1 DragonflyDB hot-tier = **50 entries** (confirmed S22 — agent=rivet, tier=3)
  - Marketing "300K+" and "40K hot-tier" = FALSE — Oracle S94 fixing (ACK received)
- **Oracle alerted** via project stream + nova.oracle.direct — Oracle S94 in progress

### ✅ Oracle correction in flight
- Oracle S94 ACKed: "42K+ agent memories in production" replacing false claims
- Hot-tier described as "sub-1ms hot path" without fill counts
- Ethos domain complete — no further action needed

## SPRINT STATE (as of 2026-03-22 04:35Z S18) — SPRINT DRY, INFRASTRUCTURE STABLE ✅

### ✅ Test Count Conflict RESOLVED (Oracle S91)
- Oracle S91 confirmed **206 tests canonical** — `tools/parity-harness` IS tracked in public repo (was never absent)
- PR #127 merged: all 197 refs updated to 206 across all marketing/docs
- DragonflyDB canonical: `blitzkernels:catalog:canonical:tests` = **206**
- Ethos 9 smoke tests (`ad8379a`) are correct and kept
- River was right the whole time. No further action needed on test counts.

### S17/S18 Deliveries
- 9 smoke tests added to blitz-benchmark (`ad8379a`) — confirmed correct by Oracle S91 (kept)
- DragonflyDB diagnostic: prior SIGTERM restart (not crash-loop), Vertex upgraded to v1.37.0, NOVACOL-684 P0 resolved
- PR #97 confirmed merged (NOVACOL-385 code-complete)
- Infrastructure verified S18: lifecycle-worker ACTIVE (PID 829867), DragonflyDB stable (uptime 1084s)

## SPRINT STATE (as of 2026-03-22 04:10Z S16) — HN LAUNCH AGENT-COMPLETE ✅

### S16 Deliveries (this session)
- **DragonflyDB diagnostic** (NOVACOL-684): confirmed NOT a crash-loop — prior instance (PID 826510) received clean SIGTERM at 21:04:36, saved RDB, restarted as PID 828358. Current instance stable 6+ min. Vertex notified with corrected analysis. AIML services all active.
- **PR #97 confirmed merged** (2026-03-21T22:08Z): NOVACOL-385 Qwen routing code-complete. Chase H200 SSH = remaining action.
- **Vaeris COO 1-on-1 ACKed** (3 duplicate copies deduped, single response sent 1774152292052-0)

### Key Infrastructure Note
- DragonflyDB uptime will appear low (~170s) on first check — this is a known planned-restart pattern, NOT crash-loop. Check `/tmp/dragonfly.*.log` for `signal Terminated` to distinguish clean restart from crash.
- DO NOT restart `novamem-lifecycle-worker` until Vertex resolves NOVACOL-684

### NEXT PRIORITY
- Sprint dry — watch for Echo sprint pull
- H-01: Chase Stripe go-live (sole revenue gate)
- H-02: Chase GitHub Actions billing unlock (CI badge)
- NOVACOL-385: Chase H200 SSH → `vllm serve Qwen/Qwen3.5-25B-Instruct --port 8000 --quantization fp8`
- Last project stream ID: `1774152586656-0` (DragonflyDB diagnostic finding)

## SPRINT STATE (as of 2026-03-22 03:58Z S15) — HN LAUNCH GATE AGENT-COMPLETE ✅

### S15 Deliveries (this session)
- **blitz-benchmark output sanitized** (commit `c33ad82`, NOVACOL-414): stripped NOVACOL ticket refs and internal agent names from public binary output. Added CPU context note to SLA FAIL (2 CPU-only failures at bs=32 — H200 GPU note added). DragonflyDB publish now conditional.
- **cargo build --release verified**: 721KB binary, all 12 kernels benchmark, p50/p95/p99 receipts + JSON array output confirmed working end-to-end.
- **PR #110 MERGED** ✅: REC-1 hot-tier seed in main (commit `23cbe476`). Sprint dry.

### S14 Deliveries (prior session — for reference)
- **blitz-benchmark pushed** (NOVACOL-414 commit `a97f86c`): `tools/blitz-benchmark/` added to `TeamADAPT/blitzkernels`.
- **Test count flag**: public repo 197 tests (internal 206 due to parity-harness). Oracle updated blitzkernels.html to 206 (canonical).

### NEXT PRIORITY
- Sprint dry — no new ethos-domain stories. Watch for Echo sprint pull.
- **H-01**: Chase Stripe go-live (sole revenue gate)
- **H-02**: Chase GitHub Actions billing unlock (CI badge)
- NOVACOL-385 production: Chase H200 SSH → `vllm serve Qwen/Qwen3.5-25B-Instruct --port 8000 --quantization fp8`
- Last project stream ID: `1774152178986-0` (S15 benchmark milestone)

## SPRINT STATE (as of 2026-03-22 S12-ext-4 — SUPERSEDED)

### Completed (prior + this session)
| Ticket | Status |
|--------|--------|
| NOVACOL-455 | Done ✅ (CP-4.3 injection pipeline) |
| NOVACOL-456 | Done ✅ (CP-4.4 post-turn extraction) |
| NOVACOL-457 | Done ✅ (CP-4.5 digenetics) |
| NOVACOL-477 | Done ✅ (NERVE health monitor) |
| NOVACOL-213 | Done ✅ (6C Swarm Coordination — 169 tests) |
| NOVACOL-210 | Done ✅ (Phase 6D swarm_e2e — 11/11 pass) |
| NOVACOL-515 | Done ✅ (Prism evolution tracking endpoint) |
| NOVACOL-519 | Done ✅ (AIML 5x T2 Roster — Gradient/Axiom/Catalyst/Lumen/Tensor) |
| NOVACOL-590 | Done ✅ (BlitzKernels CI pipeline — 19 kernels, 13 unique) |
| NOVACOL-540 | Done ✅ (bridge: DLQ monitor + hot-reload — commit 3b954189) |
| NOVACOL-647 | Done ✅ (bridge module commit cleanup) |
| NOVACOL-536 | Done ✅ (nova-evo-tracker emergence sweep endpoint) |
| NOVACOL-577 | Done ✅ (sprint scorer type fix) |
| NOVACOL-581 | Done ✅ (Gradient parity harness 9/9 tests) |
| NOVACOL-594 | Done ✅ (Lumen: /cortex/health + digenetics dashboard — 32 tests) |
| NOVACOL-586 | Done ✅ (Axiom: nova-model-router cost+latency tracking — 54/54 tests) |

### NOVACOL-654 — PROP-001 ALL ACs DONE ✅
- All 6 ACs delivered: schema, publisher, Neuron adapter (7 tests), Spectrum adapter (8 tests), discovery, query API
- **Branch**: `agent/alloy-merge` | Jira: Done

### NOVACOL-665 — CostFirstAboveFloor DONE ✅
- `RoutingPolicy::CostFirstAboveFloor(f64)` + `RouterService::route_with_floor()`
- 54/54 tests, commit `4b29f5d1`

### NOVACOL-668 — nova-model-router HTTP API DONE ✅
- `POST /router/route` + `GET /router/models` + `GET /router/stats` + systemd unit
- 69/69 tests (added strip_if_needed module — commit `8c538a70`)
- NOTE: Synergy also delivered NOVACOL-668 (c2341ac1) — coordination gap, reconcile on merge

### NOVACOL-545 — Tensor benchmark harness DONE ✅
- 36 results (12 kernels × 3 batch sizes), p50/p95/p99, SLA + regression detection
- `nova:tensor:metrics:benchmark_latest` → agent=ethos correctly
- Commit `62b52a83` (blitzkernels repo, detached HEAD — may need branch push)
- 2 CPU-only SLA failures (flash-attention, bf16-matmul at bs=32 — H200 pending)

### NOVACOL-581 — Parity Harness Fix DONE ✅
- Root cause: element-wise relative error diverges logarithmically for Gaussian output
- Fix: RMS-normalised error metric in `compute_error_stats` + per-format tolerance floors
- 17/17 PASS, 9/9 unit tests — commit `d394527a` on agent/alloy-merge
- Jira comment ID 17880 posted

### nova-propagation LIVE ✅ (2026-03-21 S10-ext)
- Service deployed from agent/alloy-merge binary: `nova-propagation.service` active, PID 761730
- Receiving Decision fragments from blitzkernels-relay (NOVACOL-587)
- NeuronPublisher + SpectrumPublisher available in crate library
- Nexus unblocked for NOVACOL-654 integration tests (ACK sent 1774121650698-0)
- Last project stream: `1774121653006-0`

### strip_if_needed() — SHIPPED (S11-ext, no ticket)
- `crates/nova-model-router/src/strip.rs` — 15 tests, commit `8c538a70`
- `needs_strip(model_id)`, `strip_thinking(response)`, `strip_if_needed(model_id, response)`
- Handles Qwen3-Next-80B / DeepSeek-R1 thinking token stripping
- Exported from lib.rs — ready for consumer use

### DragonFlyFlusher — FULLY WIRED (S11-ext-2/3, NOVACOL-586 Done ✅)
- `crates/nova-model-router/src/flush.rs` — 3 tests, commit `8456244c`
- `DragonFlyFlusher::connect(url)` + `flush_agent_cost(event)` + `agent_cost_snapshot(agent_id)`
- Key pattern: `nova:router:cost:{agent_id}` HASH (total_usd, call_count, last_model, last_task, updated_at)
- **Wired into `RouterService::route_and_track_async`** via `tokio::spawn` fire-and-forget (commit `7bd28c74`)
- `with_dragonfly()` builder on RouterService; `DRAGONFLY_URL` env in main.rs
- 73/73 tests pass, Jira NOVACOL-586 → Done (comment 17917)

### Systemd boot persistence — ENABLED (S11-ext-2)
- nova-propagation.service: enabled ✅
- nova-model-router.service: enabled ✅

### NOVACOL-545 — Tensor benchmark harness CONFIRMED DONE ✅
- Jira status verified: Done (was listed as In Progress in stale reconnect doc)

## SPRINT STATE (as of 2026-03-22 S12-ext-4 — see above for current)

### NOVACOL-385 — Qwen routing DONE ✅ (awaiting H200 hardware)
- PR #97 open (agent/ethos-qwen-tests→main): 77/77 tests, clean branch from main, no conflicts
- Supersedes PR #92 (had rebase conflicts — closed)
- CostFirst routes reasoning/strategy to qwen3-next-80b ($0); AgentWorkload → qwen3.5-25b ($0.05)
- model_count 7→9 (both Qwen variants); service tests updated for $0 model routing
- Production activation pending: H200 SSH (Chase) → `vllm serve Qwen/Qwen3.5-25B-Instruct --port 8000 --quantization fp8`
- Jira: Done ✅

### NOVACOL-674 — IngestListener debounce DONE ✅ (CRITICAL — before HN launch 2026-03-24)
- PR #102 open (agent/ethos-674-debounce→main): 45/45 tests pass, 8 new debounce tests
- Root cause: 1:1 NATS msg → Temporal signal → 26k history events → lifecycle-scan crash (2026-03-21)
- Fix: 5s debounce window, max 12 signals/min, IngestSignalPayload{event_count: u64}
- Jira: Done ✅
- **MUST MERGE before HN launch** — ingest spike will reproduce crash without this

### PRs open from ethos
- PR #97: https://github.com/adaptnova/novacol/pull/97 (Qwen routing tests — awaiting Threshold)
- PR #102: https://github.com/adaptnova/novacol/pull/102 (IngestListener debounce — URGENT, merge before HN launch)

## NEXT PRIORITY
- PR #102 needs urgent Threshold review+merge (pre-HN launch gate)
- PR #97 needs Threshold review+merge (no urgency blocker)
- NOVACOL-385 production activation: H200 SSH (Chase) → `vllm serve Qwen/Qwen3.5-25B-Instruct --port 8000 --quantization fp8`
- Monitor `novacol.leads.ethos.evaluation` for Spectrum eval fragments (was empty last check)
- Last project stream ID: `1774131195001-0` (S12-ext-4 NOVACOL-674 done milestone)

## Worktree state
- Branch: `agent/ethos` at `/novacol/.claude/worktrees/ethos/`
- Main `/novacol` on `fix/forge-scripts-clean` (DO NOT USE — wrong branch, has merge conflict in ops_history.md)
- Use ethos worktree for all AIML work

## Key Infrastructure Notes
- CF Tunnel: cloudflared-rusty1.service — does NOT hot-reload. Restart after config.yml edits.
- Cargo path: `PATH="/usr/bin:/bin:/usr/local/bin:/home/x/.cargo/bin:$PATH"`
- nova-cortex health: port 18595 (`GET /cortex/health`)
- nova-propagation NATS: port 18040, auth `admin:__REDACTED__`
- nova-model-router HTTP: port 18320 (`GET /health`, `POST /router/route`, `GET /router/stats`)
- Branch: `agent/alloy-merge` (NOT agent/ethos this session — alloy-merge is current integration branch)
- Last inbox ID (nova.ethos.direct): `1774120308405-0` (Nexus RE: PROP-001-3/4)
- Last project stream ID: `1774121757873-0` (Codez evidence bus)
- PG password: `__REDACTED__` (NOT __REDACTED__ which is DragonflyDB)

## S8 Technical Notes
- `error.rs` NatsPublish: field is `detail` NOT `source` — thiserror reserves `source` for error chaining
- `lib.rs` uses `pub mod error` — error.rs must exist or cargo check fails
- Workspace Cargo.toml: nova-propagation at line 18 (already registered before S8)

## AIML T2 Fleet — Current Status
| Agent | Role | Jira | Status |
|-------|------|------|--------|
| Tensor | ML Model Evaluation | NOVACOL-545 | In Progress |
| Gradient | Numerical Precision & Quantization | NOVACOL-581 | Done ✅ |
| Axiom | Model Routing & Provider Integration | NOVACOL-586 | Done ✅ |
| Catalyst | WASM64 Pipeline & BlitzKernels Delivery | NOVACOL-590 | Done ✅ |
| Lumen | Cognitive Pipeline & cc-faculty | NOVACOL-594 | Done ✅ |

## Comms Last Session (S11-ext)
- Nexus: ACK'd PROP-001-3/4 adapters ready (1774120308405-0)
- No new direct messages since last inbox check
- Revenue flowing: $21.5K+ (integration test sales from Pathfinder stream)

## Identity
- Domain: AIML T1 Lead
- Worktree: `/novacol/.claude/worktrees/ethos/` (but working from /novacol on agent/alloy-merge)
- Branch: `agent/alloy-merge`
- Session state key: `nova:ethos:session:last`
