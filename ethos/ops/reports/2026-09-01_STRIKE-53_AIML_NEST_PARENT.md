# STRIKE-53 receipt (copy of desk SoT)

Desk SoT: `/adapt/platform/aiml/NEST_PARENT.md`

Intake: haven-wake-ethos-strike53-1133-20260901t113300z

# AIML T1 desk — named nest parent

**Token:** `ETHOS_AIML_NEST_PARENT_STRIKE53`  
**Card:** [STRIKE-53](https://levelup2x.atlassian.net/browse/STRIKE-53)  
**Owner:** Ethos · CEEO / AIML T1  
**Stamped:** 2026-09-01  

## Decision

`/adapt/platform/aiml` is a **NOGIT nest parent**. It does **not** get a parent GitHub remote.

Children already own remotes. Parent **ignores nested remotes** and will not `git init` an umbrella that swallows them.

Done-when met: **named nest parent** (not GH remote, not named refuse).

## Parent rule

| Rule | Lock |
|------|------|
| Parent `.git` | **absent by design** |
| Parent GH remote | **none** |
| Nested child remotes | **authoritative** — do not rewrite |
| Umbrella mono-repo | **refused** (would fight nested remotes) |
| Secrets | never commit |

## Child census (2026-09-01 rematch)

| Child | Posture | origin (fetch) |
|-------|---------|----------------|
| cookbook | nested `.git` | `https://github.com/open-webui/cookbook.git` |
| desktop | nested `.git` | `https://github.com/open-webui/desktop.git` |
| extension | nested `.git` | `https://github.com/open-webui/extension.git` |
| functions | nested `.git` | `https://github.com/open-webui/functions.git` |
| open-coreui | nested `.git` | `https://github.com/TeamADAPT/open-coreui.git` |
| open-webui | nested `.git` | `https://github.com/adaptnova/open-webui.git` |
| open-webui-mcpo | nested `.git` | `https://github.com/TeamADAPT/open-webui-mcpo.git` |
| open-webui-openapi-servers | nested `.git` | `https://github.com/TeamADAPT/open-webui-openapi-servers.git` |
| opik | nested `.git` | `https://github.com/TeamADAPT/opik.git` |
| owui-forge | nested `.git` | `https://github.com/adaptnova/owui-forge.git` |
| pipelines | nested `.git` | `https://github.com/open-webui/pipelines.git` |
| quantization | NOGIT leaf | — |
| tier2/gateway | nested `.git`, **no remote yet** | — |

## Non-claims

- Not a thirteenth GH-READY card.
- STRIKE-56 was Haven leftover-close of a duplicate; **STRIKE-53** is the live aiml mill.
- Haven intake does not rewrite trees; this stamp does not rewrite child remotes.

— Ethos · CEEO / AIML T1 · Sep 1, 2026
