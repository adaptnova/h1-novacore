# Proposed novaops .gitignore addendum — STRIKE-31

**When:** 2026-09-01 12:32 MST  
**Owner:** Cosmos (tree) · Voyager (novawatch remote)  
**Strike:** proposal only. Do **not** rewrite `/adapt/platform/novaops/.gitignore` from this desk.

Chase law: recall tree **ignores T2 lead desks that have their own repo** and **ignores T3/runtime**.

Live gap: current ignore is Python/runtime crumbs. `novawatch/` has nested `.git` (novawatch-lt). `check-ignore` does not hit `novawatch`.

## Append (Cosmos applies)

```
# T2 desks with their own GH remote — do not swallow into novaops.git
novawatch/
veritas/
x1-wasm_rust/

# T2 lead desks under recall (own identity elsewhere)
tier2/

# T3 / runtime / sessions
controlplane/*/ops/runtime/
.agent-sessions/
__pycache__/
.venv/
*.env
!*.env.example
```

Done-when: `git -C /adapt/platform/novaops check-ignore -v novawatch veritas x1-wasm_rust tier2` names these paths. Nested remotes stay the hat for those desks.

— Iris · Strike Force Lead · 2026-09-01 12:32 MST
Recall trees keep T2 desks off the parent hat.
