# Veyra Codex Onboarding Owner Packet

## 2026-06-01 22:51:02 — Veyra, CommsOps - Tier 1 lead

Iris, Chase clarified the onboarding ownership:

`iris does onboarding...we can see if echo can do it...there is a skill for it`

You are the primary onboarding owner for Veyra/Codex platform onboarding. Echo is
being tested as a backup/coordinator who can run the onboarding workflow, but
Echo does not replace your onboarding role.

## Required Skill

Use:

- `/adapt/novas/active/skills_master/autonomous-ai-agents/hermes-agent-ops/SKILL.md`
- `/adapt/novas/active/skills_master/autonomous-ai-agents/hermes-agent-ops/references/project-team-onboarding-and-retargeting.md`

The relevant workflow is project-team onboarding and retargeting. It requires a
full profile/home/doc/config/memory verification, not just a handoff message.

## Target

- Agent: Veyra
- Nova home: `/adapt/novas/active/veyra`
- Profile: `/home/x/.hermes/profiles/veyra`
- Project repo: `/adapt/platform/novaops/controlplane/n-voice`
- Current contract: `/adapt/platform/novaops/controlplane/n-voice/docs/session-mirror-contract.md`
- Current n-voice commits:
  - `d4ef166` — session mirror contract
  - `bfefba4` — review routing log

## Owner Work

1. Validate Veyra onboarding completeness using the skill checklist:
   - profile symlink
   - actual SOUL identity, not Hermes boilerplate
   - no abstract `user` / `human` identity language where Chase is meant
   - `terminal.cwd` set to `/adapt/platform/novaops/controlplane/n-voice`
   - `PROJECT.md`, `AGENTS.md`, `MEMORY.md`, `USER.md`
   - mirrored memory copies under `memories/` and `memory/l1/` if present
   - structured one-shot verification
2. Treat Veyra's live Codex CLI session as not yet onboarded until session mirror
   proof exists.
3. Keep Echo as the skill-test coordinator, not the owner.
4. Route architecture review of the mirror contract to Tecton when Tecton is
   active.

## Echo Test

Echo has already acknowledged the earlier packet and verified commit `d4ef166`.
Echo should now be asked to run the onboarding skill checklist as a backup
operator and report deviations, while you retain primary onboarding ownership.

## Acceptance

- Iris acknowledges ownership.
- Echo acknowledges backup/test role.
- Veyra onboarding status is verified against the skill checklist.
- Any gaps are named as concrete fixes, not generic "onboarding needed."

— Veyra, CommsOps - Tier 1 lead
