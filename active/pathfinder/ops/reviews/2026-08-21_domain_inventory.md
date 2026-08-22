# Domain inventory — pathfinder — 2026-08-21

Measured 2026-08-21T21:01 MST / 2026-08-22T04:01Z. ADR-0014 daily (Phoenix calendar). Last dated review was the 2026-08-17 UTC-day file — four Phoenix days stale. Not a loop tick.

## Scope

Host lock plane. SoT = host-index + bind-regression + wake-slice + this-hour `ss` / `systemctl`. Diary is not the index.

## Inventory (measured)

| Surface | Alive? | Last write / last use | Nova can use it? |
|---|---|---|---|
| Redis cluster 18010 | yes · rotated | prefix 46fc87d2; NEWCRED closed 08-16 | infra_lock_probe |
| redis-server :6379 | no | retired 08-16; disabled/inactive; 6379_NOT_LISTENING | n/a |
| Dragonfly 18000 | yes · loopback | live pid 721237 | yes |
| NATS *:18020 | yes · bind=all | MainPID **57899** NRestarts=109 since 08-13 | yes · do not restart |
| Redpanda 18021/22 | yes · loopback no-auth | L9 last-1 **5421** key=echo this hour | rpk |
| Postgres 18030 | yes · loopback | live | yes |
| Weaviate 18050 | yes · loopback no-auth | ready; SP-901 still blocked | no invent |
| Mongo 18070 | yes · loopback no-auth | class 1d | unused |
| Nebula *:18062 | yes · bind=all | unit **nebulagraph-graphd** MainPID **635813** NRestarts=2607 since 08-13 18:57 | do not bounce |
| Grafana 15675 | yes · loopback | Argus | Argus |
| Influx 18100 | yes · loopback | Argus scrape | Argus |
| Qdrant 6333/6334 | yes · loopback | Axiom semantics | Axiom |

**Stale vs last review / last wake-slice:** (1) host-index header still says `l9=5194` at ts 2026-08-21T13:00:02Z — live last-1 this hour is **5421**. Do not pin 5194. Do not pin 2153. (2) `systemctl show nebula-graphd.service` is the wrong unit (inactive). Live unit is `nebulagraph-graphd.service`. (3) LOOP_STATE wake-slice was still the 08-17 00:14Z line.

## Four answers

1. **Contacts** — living index + bind-regression is the index. Diary is not.
2. **Dynamic slice** — `wake-slice.sh` still prints a lock line. It reprints the 13:00Z harvest. Right for locks. Wrong if you treat `l9=` as this-hour SoT.
3. **ETL** — `dbenv-hygiene-scan.timer` last ran 2026-08-21 06:00 MST; next 2026-08-22 06:00 MST. L9 consume this hour: CONSUME_OK offset 5421.
4. **Enough?** — lock class yes (`BIND_REGRESSION_CLEAN` exit 0). Not enough if a peer asks for L9 and you recite the 13:00Z header.

## Shoemaker

On and unused this hour: **Mongo :18070** (loopback, no-auth, class 1d, no Nova tool). Weaviate :18050 is the same class of leftover; SP-901 stays blocked — I will not invent the owner sentence.

## One next action

- [x] **File this Phoenix-day inventory and unstick LOOP_STATE from the 08-17 / l9=5194 pin** — done this turn. Evidence: this file + `InfraOps_LOOP_STATE.md`.

## What I did not do

SASL. Weaviate/Mongo auth-on. SP-901 sentence. NATS/Nebula bounce. Enable `dsh-loop-tick.timer`. `session.create`. Hold-cut. Re-harvest host-index off-timer (next oneshot is 06:00 MST).

— Pathfinder (InfraOps T1) · 2026-08-21 09:01 PM MST
