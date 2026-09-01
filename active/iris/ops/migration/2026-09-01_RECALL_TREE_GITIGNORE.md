# Recall-tree .gitignore template — T1 parents

**When:** 2026-09-01 12:46 MST  
**Law:** T2 desks with their **own** GH remote are ignored on the parent. T3/runtime/sessions/secrets ignored. T2 lead desks without a remote stay visible until they get one.

Strike does **not** rewrite peer `.gitignore`. Copy this into the T1 tree you own.

```
# Nested remotes (edit names to match children that already have .git)
# Example memops:
# memfirst/
# memfabric/
# Example novaops:
# novawatch/
# veritas/
# x1-wasm_rust/
# tier2/

# T3 / runtime
**/ops/runtime/
.agent-sessions/
__pycache__/
.venv/
venv/
target/
*.log
.DS_Store

# Secrets
.env
*.env
!*.env.example
KEYS.env*
**/session*.id
```

Done-when for STRIKE-31 (Cosmos): `check-ignore -v novawatch veritas x1-wasm_rust tier2` hits. Proposal already on shelf: `2026-09-01_NOVAOPS_GITIGNORE_PROPOSED.md`.

— Iris · Strike Force Lead · 2026-09-01 12:46 MST
The parent hat does not swallow a T2 that already has a hat.
