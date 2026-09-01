# GitHub-ready migration map — drop of a hat

**When:** 2026-09-01 12:20 MST · **rematch 12:28 MST**  
**Owner:** Iris · Strike Force Lead  
**Status:** pack LIVE on STRIKE-28..33 + 44–54. **Not drop-of-a-hat yet.** Named GAPs: `gh` token invalid; novaops ignore unmilled; T1 remotes unminted; living T1 homes janus/voyager/stratum/nexus/delve/threshold/oracle/mnemos/lumen/spark/ethos/goggles/weft untracked. Vertex restore drill **PASS** on disk (STRIKE-33 Jira still To Do).  
**Secrets:** never. `/adapt/secrets/` stays off GH. Names only.

Chase: not a clock. Jira Task assigned → wake that seat **now** (Delve inject, 15 min is the net). This pack is the first real MISSION pile.

## What “current” means

| Surface | Done-when |
|---|---|
| Nova home | Identity files (AGENTS, SOUL, USER, MEMORY, ops law) on a GH remote, or nested under a parent remote that tracks that seat. Dirty/ahead named. |
| Work domain | T1 desk `/adapt/platform/<domain>` has its own GH remote **or** is nested under a parent with an ignore that does **not** swallow T2 lead desks. T3/runtime under a recall tree is **ignored**. |
| Databases | Dump/restore runbook + artifact path (not live volumes). Owner named. |

Do **not** commit: secrets, `KEYS.env`, session ids, Atlassian tokens, LIVING gold-bar if it holds private inodes only as needed — disk wins; never print keys.

## 1. Nova homes — `/adapt/novas/active`

Parent git: `/adapt/novas` → `novacore` `https://github.com/adaptnova/h1-novacore.git`. Rematch 12:48: tracking `synergy-master/working` **ahead 95**. Remotes named `novacore` + `synergy-master` (twin still GAP — Forge STRIKE-30). `gh` token **invalid** this host (`2026-09-01_GH_AUTH_GAP.md`).

**Tracked under novacore (parent `git ls-files`, rematch 12:28):** a_nova_template, anvil, axiom, canary-forge, chronos, echo, **gaze, haven**, iris, meridian, pathfinder, riven, rook, skipper, **talon**, tecton, vertex, veyra, **zap**. File counts this sitting: gaze 85 · haven 42 · talon 39 · rook 94 · zap 8 · anvil 41 · iris 52. **STRIKE-29 rematch: T2 identity is on the parent hat.** Remaining: dirty/untracked ops under those seats, and ~73 other active dirs still untracked (twins, specialists, janus/voyager/stratum/nexus/delve/…).

**Own `.git` (nested, not the parent):** cosmos (cosmos-lt), forge (devops-automation), synergy (synergy-master), vaeris (vaeris-master, ahead 18).

**Living Strike T2s:** parent-tracked (not NOGIT). Home has no nested `.git`. **P0 hole closed on rematch — do not recopy map L28 as still-NOGIT.**

**Living T1s still untracked at home (sample):** janus, voyager, stratum, nexus, delve, threshold, oracle, mnemos, lumen. Echo/axiom/chronos/veyra/meridian/pathfinder/vertex tracked. Cosmos/forge/synergy/vaeris own-git.

**Do not treat as seats:** `Apex`/`apex` case twins, `KEYS.env.template`, `secrets/`, `_migrate_backups`, `_shared`, `packet162`, specialist clones, `Iris` vs `iris`.

## 2. Work domains — `/adapt/platform`

**Has own GH remote**

| Desk | Remote |
|---|---|
| novaops | adaptnova/novaops.git (branch working-loop-engineer-continuous-operations) |
| novaops/novawatch | adaptnova/novawatch-lt.git |
| novaops/veritas | adaptnova/veritas.git |
| novaops/x1-wasm_rust | adaptnova/x1-wasm_rust.git |
| commsops | adaptnova/commsops-lt.git |
| commsops/n-voice | adaptnova/n-voice.git |
| timeops | adaptnova/timeops.git |
| orchops | adaptnova/h1-orchops.git |
| COO | adaptnova/coo.git |
| dataops | ADAPT-Chase/x1_dataops.git |
| architecture/z-pure | adaptnova/z-pure.git |
| memops/memfirst | adaptnova/memfirst.git |
| memops/memfabric | adaptnova/memfabric.git |
| rustynova | ADAPT-Chase/x1_rustynova.git |
| researchops/viper | ADAPT-Chase/x1_viper.git |

**NOGIT at T1 desk (must get a remote or nest under a named parent)**

aiml (children have remotes), architecture (z-pure only), devops, evoops, growthops, infraops, memops (children only), pmops, researchops, CoS, **striketeam**, cognition, MLOps.

**Recall-tree ignore law (Chase)**

Example: `novaops` should **gitignore T2 lead desks** that have their own repo (novawatch already has novawatch-lt) and **gitignore T3/runtime** (`controlplane/*/ops/runtime/`, sessions, logs, `__pycache__`, `.venv`). Live gap: novaops `.gitignore` has Python/runtime crumbs but **does not** ignore `novawatch/` (nested `.git` risk), `tier2/`, or T3 leads. Untracked flood: `_shared/`, `bin/`, `controlplane/paperclip*`, recoveryops.

Same pattern for memops (ignore memfirst/memfabric as nested remotes), commsops (n-voice already nested).

## 3. Databases — dump path, not volumes

Live this host (names only): NATS 18020, Dragonfly 18000, Redis 18010, Postgres 18030, Redpanda 18021, Nebula 18062, MinIO, Mongo, ClickHouse (langfuse + memfab), memfab-graph, memfab-indexer. Neo4j vars exist; confirm running before dump.

**Never GH:** live data dirs, WAL, secrets in connection strings. **Do GH:** restore runbook + last dump pointer (object store / encrypted artifact), schema migrations in the owning domain repo.

Owners (T1): Axiom memops river/L9 · Pathfinder infra · Vertex dataops · Chronos time · Veyra NATS surface · Voyager glass.

## 4. Jira pack (STRIKE Tasks — labels not types)

File as **Task**. Assign the domain lead. Haven stamps. Delve injects on assign (when wired); until then Anvil 15 min net.

| Card | Owner | Done-when |
|---|---|---|
| STRIKE GH-READY map SoT | Iris / Anvil | this file + wiki Mission Log line |
| Novacore: track living Strike T2 homes (gaze haven talon rook zap) **or** per-seat remotes | Anvil + Forge | `git ls-files active/<seat>` or named remote |
| Novacore: ahead-92 push **or** named GAP (review first) | Forge | working not 92 ahead, or GAP |
| Novacore: drop/rename twin `origin` synergy-master | Forge | one fetch remote |
| novaops .gitignore: T2 desks with own repo + T3/runtime | Cosmos / Voyager | check-ignore novawatch, tier2, runtime |
| T1 NOGIT desks: remote or nest | each T1 (Forge/Axiom/Nexus/Meridian/Oracle/Iris striketeam/…) | desk has GH or named parent |
| DB dump/restore runbook | Vertex + Axiom + Pathfinder | one restore drill named |
| Secrets stay off GH | Stratum | obtain-seat / m2.env never in tree |
| Zap Atlassian pen | Stratum / Janus / Meridian | already sequenced — not this mill |

## 5. Agent power

Not a 15 min leftover mill. One Task per owner. Inject on assign. Close-bar: find, owner, done-when, evidence path. Recopy of this map = fail.

— Iris · Strike Force Lead · 2026-09-01 12:20 MST
The mill is the map. GitHub is the hat. Drop it when you say go.
