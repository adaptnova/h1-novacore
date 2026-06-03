# 01 — Full Onboarding Checklist

Use this for every Nova birth, retarget, or project-team onboarding. The old project-team checklist is not enough by itself.

## A. Identity + home

- [ ] Nova home exists: `/adapt/novas/active/<Name>`.
- [ ] Hermes profile path exists: `/home/x/.hermes/profiles/<profile>`.
- [ ] Profile is a symlink to Nova home, unless explicitly operating in external-profile mode.
- [ ] `SOUL.md`, `MEMORY.md`, `USER.md`, `PROJECT.md`, `AGENTS.md` exist when project-scoped.
- [ ] Mirrored identity exists and matches intent:
  - [ ] `memories/SOUL.md` / `memories/MEMORY.md` / `memories/USER.md` where present.
  - [ ] `memory/l1/SOUL.md` / `memory/l1/MEMORY.md` / `memory/l1/USER.md`.
- [ ] Identity docs say Chase/he/him, not abstract "user" or distancing "human" language.

## B. Hermes runtime

- [ ] `config.yaml` parses as YAML.
- [ ] `terminal.cwd` points to the assigned project repo, not `.` for project-team agents.
- [ ] `plugins.enabled` includes `memfirst-realtime`.
- [ ] Plugin files exist:
  - [ ] `plugins/memfirst-realtime/plugin.yaml`
  - [ ] `plugins/memfirst-realtime/__init__.py`
- [ ] `scripts/memfirst_ingest.py` exists and is executable/readable by Hermes.
- [ ] Hermes can launch one-shot and answer a structured identity prompt.

## C. MemFirst seed

- [ ] `memory/l0/intake/sessions/*_onboarding.jsonl` exists.
- [ ] `sessions/*_onboarding.jsonl` exists.
- [ ] Both JSONL files parse.
- [ ] Seed contains system/user/assistant onboarding records.

## D. Realtime injection and ingestion

- [ ] `pre_llm_call` hook injects compact context from:
  - [ ] `memory/l1/SOUL.md`
  - [ ] `memory/l1/MEMORY.md`
  - [ ] `memory/l2/memory.mmd`
  - [ ] `memory/l2/general.mmd`
  - [ ] latest `memory/l0/intake/sessions/*.jsonl` or `sessions/*.jsonl`
- [ ] `post_llm_call` hook calls `scripts/memfirst_ingest.py` for completed user/assistant turns.
- [ ] Per-turn L0 append works: `memory/l0/intake/sessions/<session>.jsonl`.
- [ ] Root session mirror works: `sessions/<session>.jsonl`.
- [ ] L3 semantic add works or reports explicit skip reason.
- [ ] L4 verbatim add works or reports explicit skip reason.
- [ ] L5 raw session source write works.
- [ ] L6 NATS publish works or reports explicit skip reason.

## E. Infrastructure, graph/vector, trace/playback

- [ ] NATS direct/event/memory subjects exist and accept probe publish/request.
- [ ] Nexus route/channel registration exists for direct and assigned team/project rooms.
- [ ] Voice/A2A/NEXUS contract is verified:
  - [ ] `nova.<profile>.direct` accepts public direct A2A payloads.
  - [ ] `nova.<profile>.meet` accepts public room payloads.
  - [ ] `nexus.agent.<profile>.direct` or `.inbox` accepts full-message session-ingress payloads.
  - [ ] Full NEXUS push lands in Hermes session `nexus_<profile>_<sender>`.
  - [ ] Successful route metadata reports `source_surface=nexus_inbox`, `delivery_policy=session_only`, and `delivery=api_session`.
  - [ ] xAI/Grok voice plan is available or Deepgram fallback is explicitly recorded.
- [ ] DragonflyDB namespace probe works for presence, heartbeat, cache, locks, counters.
- [ ] Redpanda durable topics exist and probe publish/read works.
- [ ] NebulaDB graph space exists and Nova/project/channel/memory provenance vertices + edges upsert/query.
- [ ] Vector DB/L3 semantic probe embeds and retrieves identity + realtime turn.
- [ ] Hermes runtime DBs/JSONL mirrors are present and no stale lock blocks launch.
- [ ] E2E trace records the full user→Hermes→LLM→MemFirst→Nexus/fanout path.
- [ ] Playback can reconstruct the trace and identify the first broken hop without mutating production state.

## F. Historical backfill and mirrors

- [ ] Historical Codex/Hermes/session exports are copied into `history/` or `memory/l0/intake/sessions/` as appropriate.
- [ ] Durable facts are distilled into `MEMORY.md`; raw transcript is preserved, not pasted blindly into durable memory.
- [ ] If preserving a live Codex/Veyra-style session, use session mirror metadata and do not claim process transfer.
- [ ] Backfilled sessions are marked as historical, not current live turns.

## F. Acceptance

A Nova is fully onboarded only when all of these are true:

```yaml
identity: PASS
hermes_profile: PASS
hermes_runtime: PASS
seed_l0_sessions: PASS
realtime_pre_llm_injection: PASS
realtime_post_llm_ingestion:
  l0: PASS
  sessions_mirror: PASS
  l3: PASS|SKIPPED(reason)
  l4: PASS|SKIPPED(reason)
  l5: PASS
  l6: PASS|SKIPPED(reason)
historical_backfill: DONE|NOT_REQUIRED|SEPARATE_PENDING
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
voice_a2a_nexus:
  public_direct_subject: PASS
  public_meet_subject: PASS
  nexus_direct_or_inbox_subject: PASS
  session_event_subject: PASS
  full_push_session_delivery: PASS
  reply_to_round_trip: PASS|NOT_REQUIRED
  xai_voice_plan_or_fallback: PASS
structured_identity_prompt: PASS
```
