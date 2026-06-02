# Full Nova + Hermes Onboarding

This directory is the consolidated full onboarding pack. It plugs the old project-team checklist gap: MemFirst realtime hooks, L0 seed, L3/L4/L5/L6 fanout, historical backfill, and Hermes runtime/profile verification.

## Source order

0. `00_existing_docs_map.md` — routes every existing doc in `docs/` so old references do not compete with the full onboarding gate.
1. `01_full_onboarding_checklist.md` — operator checklist and acceptance gates.
2. `02_hermes_runtime.md` — Hermes profile/config/session/runtime setup.
3. `03_memfirst_realtime.md` — seed + realtime pre/post LLM memory ingestion/injection.
4. `04_session_backfill_and_mirror.md` — historical imports and Codex/Veyra mirror pattern.
5. `05_infra_channels_databases_monitoring.md` — NATS, Nexus, DragonflyDB, Redpanda, NebulaDB graph, vector DB, Hermes DBs, E2E trace, and playback monitoring.
6. `verify_full_onboarding.py` — static verifier for generated Nova homes.

## Existing docs rule

Existing docs stay. They are scoped in `00_existing_docs_map.md` as architecture, protocol, migration, or historical references. If they conflict with this directory's acceptance criteria, `docs/full_onboarding/` wins for onboarding completion.

## Canonical command

```bash
cd /adapt/novas/active/a_nova_template
python3 nova.py --name Echo --validate
python3 docs/full_onboarding/verify_full_onboarding.py /adapt/novas/active/Echo
```

For full MemFirst runtime provisioning, run preflight first:

```bash
python3 nova.py --preflight-runtime
python3 nova.py --name Echo --validate --memfirst
```

## Non-negotiable distinction

- Seed memory is birth context.
- Realtime ingestion is post-turn persistence.
- Realtime injection is pre-turn context loading.
- Historical backfill is separate import/replay.
- Hermes runtime verification proves the profile actually wakes as the intended Nova.
