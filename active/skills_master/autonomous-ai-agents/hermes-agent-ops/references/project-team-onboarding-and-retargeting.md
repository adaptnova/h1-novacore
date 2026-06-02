# Project-team onboarding and retargeting for Hermes novas

Use this when an operator wants multiple novas brought up around a single repo/team structure rather than just opening an existing CLI.

## What to do

1. Ensure each nova has a full home under `/adapt/novas/active/<profile>` and a matching profile symlink at `/home/x/.hermes/profiles/<profile> -> /adapt/novas/active/<profile>`.
2. Set `terminal.cwd` in each profile `config.yaml` to the canonical project repo, not `.`.
3. Add explicit onboarding files in the nova home:
   - `PROJECT.md`
   - `AGENTS.md`
   - `SOUL.md`
   - `MEMORY.md`
   - `USER.md`

   **Identity language rule:** Never use "user", "human", or "they/them" when referring to the operator. Always use "Chase" and "he/him." Check every identity file (SOUL.md, MEMORY.md, USER.md) for abstract distancing words and replace with Chase. The operator is not an abstract user — he is Chase, CEO of Adapt AI + iRemember. Files that say "your human gave you access" or "tell the user" are WRONG — they should say "Chase gave you access" and "tell Chase."

4. **CRITICAL: Sync SOUL.md to the profile directory.**
6. When repurposing an existing nova, refresh not only top-level `SOUL.md` / `MEMORY.md` / `USER.md` but also the mirrored copies under:
   - `memories/`
   - `memory/l1/`
   Old mirrored files can keep the agent anchored to a previous project even after top-level files are updated.
7. Set `terminal.cwd` in the profile `config.yaml` to the canonical project repo. Note: this only controls the working directory of terminal() tool calls within the session — it does NOT set the initial process cwd. For the initial session cwd, pass `--working-directory` on gnome-terminal launch or set it in the persistent CLI invocation.
8. Verify with a direct Hermes prompt that asks for exact structured fields, e.g. name, role, repo, and first required action. Free-form verification can drift.
9. For full onboarding, apply the MemFirst + Hermes overlay from `/adapt/novas/active/a_nova_template/docs/full_onboarding/`:
   - L0 onboarding seed in both `memory/l0/intake/sessions/` and root `sessions/`
   - `plugins/memfirst-realtime` enabled in Hermes config
   - `pre_llm_call` realtime memory injection
   - `post_llm_call` realtime turn ingestion via `scripts/memfirst_ingest.py`
   - L3/L4/L5/L6 fanout or explicit skip reasons
   - historical backfill/session mirror handling when applicable

## Verification pattern

Good verification prompt:

```text
Reply exactly in this format: NAME=<name>; ROLE=<role>; REPO=<primary repo>; FIRST=<first required action>.
```

Why: exact formatting makes it obvious whether the nova adopted the new repo and onboarding instructions.

## Pitfalls

1. **Profile SOUL.md mismatch (CRITICAL).** Hermes loads SOUL.md from the profile directory (`/home/x/.hermes/profiles/<name>/SOUL.md`), NOT from the nova home. If the profile's SOUL.md is default boilerplate and the nova home's is the custom identity, the agent WILL wake up as generic Hermes Agent. Always replace the profile SOUL.md with the nova home version.

2. **Profile is a real directory, not a symlink.** When the profile exists independently (not a symlink to the nova home), edits to nova home files do NOT propagate. You must sync key files (SOUL.md, MEMORY.md, USER.md) to both locations. This is common when the profile was bootstrapped with `hermes` before the nova home was created.

3. **Old mirrored files.** If an existing nova still reports an old project after you updated the obvious files, check `memories/SOUL.md`, `memories/MEMORY.md`, `memory/l1/SOUL.md`, and `memory/l1/MEMORY.md` before assuming the config edit failed.

4. **terminal.cwd misconception.** Setting `terminal.cwd` in config.yaml only controls the working directory of terminal() tool calls within the session. It does NOT set the initial process cwd. For the session cwd, use `--working-directory` on the gnome-terminal launch command.