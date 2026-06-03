# 05 — Infra Channels, Databases, Trace, and Playback

Full onboarding must provision or register the Nova in the runtime substrate, not just create files.

## Required substrate

```yaml
nats:
  purpose: realtime command/event bus
  subjects:
    direct: nova.<profile>.direct
    meet: nova.<profile>.meet
    ping: nova.<profile>.ping
    events: nova.<profile>.events
    memory_turns: memory.<profile>.session_turn
    nexus_direct: nexus.agent.<profile>.direct
    nexus_inbox: nexus.agent.<profile>.inbox
    nexus_wildcard: nexus.agent.<profile>.>
    session_events: nova.sessions.<profile>.events
  required_checks:
    - connection succeeds with configured env
    - direct subject accepts publish/request
    - NEXUS direct or inbox subject accepts full-message session-ingress envelope
    - full-message NEXUS push lands in Hermes session nexus_<profile>_<sender>
    - memory subject receives session-turn event
    - reply_to/correlation_id round trip works

nexus:
  purpose: routing, rooms, channel membership, cross-surface coordination
  required_registration:
    - nova identity/profile
    - direct channel
    - room/team channels
    - route owner / fallback target
    - xAI/Grok realtime voice provider plan or explicit Deepgram fallback
    - source surfaces: hermes_cli, nats_direct, voice, codex_mirror where applicable
  required_checks:
    - Nova can be resolved by profile/name
    - direct route exists
    - room membership exists if assigned to a team/project
    - route emits correlation_id for trace/playback
    - session-ingress route reports source_surface=nexus_inbox and delivery=api_session

dragonflydb:
  purpose: ephemeral runtime state, presence, locks, cache, counters
  namespaces:
    presence: nova:<profile>:presence
    heartbeat: nova:<profile>:heartbeat
    session_cache: nova:<profile>:session:<session_id>
    locks: nova:<profile>:lock:<name>
    rate_limits: nova:<profile>:ratelimit:<bucket>
  required_checks:
    - ping succeeds
    - write/read/delete namespace probe succeeds
    - heartbeat key can be set with TTL

redpanda:
  purpose: durable event log and downstream replay/consumers
  topics:
    - nova.session_turns
    - nova.memory_mutations
    - nova.lifecycle
    - nexus.messages
    - trace.e2e
  partitioning:
    key: <profile>|<session_id>|<trace_id>
  required_checks:
    - broker reachable
    - topics exist or can be created by provisioner
    - probe event publish/read works

nebuladb:
  purpose: graph DB for entities, relationships, routing, provenance, and ownership
  graph_spaces:
    novaops: Nova identities, teams, projects, channels, tools, permissions
    memfirst: memory entities, session entities, relationship edges, provenance
  vertex_types:
    - Nova
    - Chase
    - Project
    - Team
    - Channel
    - Session
    - MemoryArtifact
    - Tool
    - Service
  edge_types:
    - OWNS
    - MEMBER_OF
    - ROUTES_TO
    - PARTICIPATED_IN
    - GENERATED
    - REFERENCES
    - DEPENDS_ON
    - HAS_PERMISSION
  required_checks:
    - NebulaDB reachable
    - graph space exists
    - Nova vertex upsert succeeds
    - project/team/channel edges upsert succeed
    - query returns the Nova's route + memory provenance edge

vector_db:
  purpose: semantic recall/search
  primary_layer: L3 semantic index
  optional_external_backends:
    - Chroma
    - Qdrant
    - pgvector
  required_checks:
    - embedding key available from /adapt/secrets/m2.env
    - per-Nova/domain collection/index exists
    - identity seed embedded
    - realtime session-turn embedding inserted
    - probe query returns expected hit
    - no silent no-op/hash-only fallback

hermes_databases:
  purpose: local agent runtime state
  files:
    - state.db
    - sessions/*.jsonl
    - response_store.db if enabled
    - auth.json/auth.lock where applicable
  required_checks:
    - state DB can be opened if present
    - active session is mirrored to sessions JSONL
    - no stale lock blocks launch
```

## E2E trace + playback monitoring

Monitoring is not just health checks. It must prove an interaction can be traced end-to-end and replayed.

```yaml
trace_event_required_fields:
  - trace_id
  - correlation_id
  - session_id
  - turn_id
  - profile
  - source_surface
  - target_surface
  - route
  - model_provider
  - model_name
  - user_message_hash
  - assistant_response_hash
  - timestamps:
      - received_at
      - pre_llm_context_built_at
      - model_request_at
      - model_response_at
      - post_llm_ingest_at
      - fanout_complete_at
  - layer_results:
      - l0
      - sessions_mirror
      - l3
      - l4
      - l5
      - l6
      - nexus
      - nebuladb
      - vector_db
      - dragonflydb
      - redpanda

trace_sinks:
  local_jsonl: memory/l0/intake/logs/trace.e2e.jsonl
  nats: trace.<profile>.e2e
  redpanda: trace.e2e
  l5_raw: memory/l5/raw/trace-<trace_id>.json

playback_requirements:
  - load trace by trace_id
  - reconstruct ordered user/assistant/tool/layer events
  - verify each fanout target from recorded IDs/paths
  - replay a read-only route without mutating production state
  - compare expected vs actual memory/context retrieval
  - report first broken hop
```

## Acceptance gate

```yaml
infra_channels_databases_monitoring:
  nats: PASS|FAIL
  nexus: PASS|FAIL|SKIPPED(reason)
  dragonflydb: PASS|FAIL
  redpanda: PASS|FAIL
  nebuladb: PASS|FAIL|SKIPPED(reason)
  vector_db: PASS|FAIL|SKIPPED(reason)
  hermes_databases: PASS|FAIL
  e2e_trace: PASS|FAIL
  playback: PASS|FAIL
  temporal_io_touch_inventory: PASS|FAIL|SKIPPED(reason)
```

Temporal.io touch inventory is required because Temporal workers/workflows can silently own or replay parts of the runtime. The runtime verifier inventories, without mutating workflows:

```yaml
temporal_io_touch_inventory:
  checks:
    - temporal CLI availability
    - user/system service units
    - running temporal processes/workers
    - ports 7233/8233 and related listeners
    - cluster health
    - namespaces
    - known repo/config touch paths
  rule: inventory only; do not start/stop workflows during onboarding verification unless explicitly directed
```

A Nova is not production-onboarded until at least one complete user→Hermes→LLM→MemFirst→Nexus/trace path can be replayed from recorded trace data.
