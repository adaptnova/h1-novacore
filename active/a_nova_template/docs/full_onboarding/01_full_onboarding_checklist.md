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

## E. Historical backfill and mirrors

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
structured_identity_prompt: PASS
```
