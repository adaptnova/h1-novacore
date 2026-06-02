# Runtime Onboarding Verifier Status

**Date:** 2026-06-02 11:49:42 MST  
**Author:** Riven - MemOps T1 Lead  
**Domain:** NovaOps / MemOps  
**Project:** Full Nova onboarding  
**Verifier:** `/adapt/novas/active/a_nova_template/docs/full_onboarding/verify_runtime_onboarding.py`

## Summary

The full onboarding gate now has an executable runtime verifier.

It does not only inspect files. It creates or targets a Nova, exercises realtime hooks, probes MemFirst fanout, records E2E trace artifacts, verifies playback reconstruction, and inventories Temporal.io touch points.

## What the verifier does

```yaml
runtime_verifier:
  path: /adapt/novas/active/a_nova_template/docs/full_onboarding/verify_runtime_onboarding.py
  modes:
    temp_nova:
      command: python3 docs/full_onboarding/verify_runtime_onboarding.py --name RuntimeOnboardProbe
    existing_nova:
      command: |
        python3 docs/full_onboarding/verify_runtime_onboarding.py \
          --nova-home /adapt/novas/active/<NovaName> \
          --profile <profile>
  verifies:
    - temp Nova creation unless --nova-home is provided
    - pre_llm_call memory injection
    - post_llm_call turn ingestion
    - direct scripts/memfirst_ingest.py fanout
    - L0 raw session append
    - root sessions mirror append
    - L3/vector semantic add
    - L4 verbatim add
    - L5 raw source write
    - L6 NATS publish
    - NATS runtime publish
    - DragonflyDB namespace probe
    - Redpanda durable topic presence
    - NebulaDB CLI availability
    - Hermes DB/session mirror basics
    - E2E trace JSONL + L5 raw trace write
    - playback reconstruction
    - Temporal.io touch inventory
```

## Output contract

```yaml
runtime_probe_ok: true|false
production_gate_ok: true|false
```

Meaning:

```yaml
runtime_probe_ok:
  true: core hook/ingest/trace/playback verifier path executed successfully
  false: verifier could not prove the core runtime path

production_gate_ok:
  true: all production substrate checks passed
  false: one or more production substrate requirements are missing/incomplete
```

A run can have:

```yaml
runtime_probe_ok: true
production_gate_ok: false
```

That means the Nova/Hermes/MemFirst runtime path works, but the broader production substrate is incomplete.

## Latest verified run

```yaml
latest_verified_run:
  runtime_probe_ok: true
  production_gate_ok: false
  temp_nova_home: /data/vast/tmp/nova_runtime_onboard_base_4p7p0zny/RuntimeOnboardProbe
  trace_id: 1f3c80d3038d

  passed:
    l0: true
    sessions: true
    l3: true
    l4: true
    l5: true
    l6: true
    nats: true
    dragonflydb: true
    vector_db: true
    e2e_trace: true
    playback: true
    temporal_io_touch_inventory: true

  failed_or_incomplete:
    redpanda_topics: false

  skipped_or_not_available:
    nebuladb:
      skipped: true
      reason: NebulaDB CLI missing (nebula-console/ngql)
```

## Current production blocker

```yaml
current_blocker:
  redpanda_topics: missing
  expected_topics:
    - nova.session_turns
    - nova.memory_mutations
    - nova.lifecycle
    - nexus.messages
    - trace.e2e
```

The runtime path is not the blocker. Durable Redpanda topic provisioning is the current production-gate blocker.

## Temporal.io touch inventory

The verifier inventories Temporal without mutating workflows.

```yaml
temporal_io_touch_inventory:
  status: PASS
  temporal_cli: /home/x/.temporalio/bin/temporal
  cluster_health: true
  namespaces: true
  known_touch_paths_count: 6
  known_touch_paths:
    - /adapt/platform/timeops
    - /adapt/platform/pmops/orchops
    - /adapt/platform/dataops/dbops/integrations/temporal_langgraph_bridge.py
    - /adapt/novas/temporal_nova_core
    - /adapt/platform/novaops/toolops/mcp_servers/temporal-mcp
    - /adapt/projects/mem/tests/test_temporal_workflows.py
```

Temporal is therefore part of the onboarding visibility surface: it may own, replay, or orchestrate parts of the runtime, so onboarding verification must know what Temporal touches before declaring a Nova production-ready.

## Files updated in implementation

```yaml
created:
  - /adapt/novas/active/a_nova_template/docs/full_onboarding/verify_runtime_onboarding.py

updated:
  - /adapt/novas/active/a_nova_template/docs/full_onboarding/README.md
  - /adapt/novas/active/a_nova_template/docs/full_onboarding/05_infra_channels_databases_monitoring.md

commit:
  sha: 606905c
  message: Add runtime onboarding verifier
  pushed: true
```

## Next production step

```yaml
next_step:
  create_or_verify_redpanda_topics:
    - nova.session_turns
    - nova.memory_mutations
    - nova.lifecycle
    - nexus.messages
    - trace.e2e
  then_rerun:
    command: python3 /adapt/novas/active/a_nova_template/docs/full_onboarding/verify_runtime_onboarding.py --name RuntimeOnboardProbe
  expected_result:
    runtime_probe_ok: true
    production_gate_ok: true_or_blocked_only_by_nebuladb_if_nebuladb_is_not_installed
```
