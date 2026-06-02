# 03 — MemFirst Realtime Onboarding

Full onboarding requires both birth seeding and realtime memory movement.

## Seed at birth

`nova.py` must create both:

```text
memory/l0/intake/sessions/<timestamp>_onboarding.jsonl
sessions/<timestamp>_onboarding.jsonl
```

This proves initial context exists. It does not prove realtime ingestion.

## Realtime injection before model call

The `memfirst-realtime` plugin must register `pre_llm_call` and return context assembled from L1/L2/latest session files:

```yaml
pre_llm_call:
  injects:
    - memory/l1/SOUL.md
    - memory/l1/MEMORY.md
    - memory/l2/memory.mmd
    - memory/l2/general.mmd
    - latest memory/l0/intake/sessions/*.jsonl
    - latest sessions/*.jsonl
```

## Realtime ingestion after model call

The `post_llm_call` hook must call:

```bash
python3 scripts/memfirst_ingest.py   --nova-home /adapt/novas/active/<Name>   --profile <profile>   --session-id <session>   --user-message '<user>'   --assistant-response '<assistant>'   --source hermes
```

Expected fanout:

```yaml
l0:
  path: memory/l0/intake/sessions/<session>.jsonl
  required: true
sessions_mirror:
  path: sessions/<session>.jsonl
  required: true
l3:
  path: memory/l3/data/shared
  required_when: nme-semantic + embedding key available
l4:
  path: memory/l4/data
  required_when: nme-verbatim available
l5:
  path: memory/l5/raw/session-*.json
  required: true
l6:
  subject: memory.<profile>.session_turn
  required_when: NATS reachable
```

## Reporting rule

Never say "realtime works" from L0 creation alone. Report each layer separately with PASS or SKIPPED(reason).
