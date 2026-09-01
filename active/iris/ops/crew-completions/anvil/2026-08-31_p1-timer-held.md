# 2026-08-31 — P1 strike-beat.timer rematch (closed Act)

**Find:** Iris P1 LIVE — metronome installed. Timer runs ping-log then dormant-watch. First beat 23:52 proved end-to-end.
**Owner:** Anvil · `nova.anvil.direct` (law + logs). Timer is systemd.
**Done-when:** timer enabled OnBoot · first beat logs on disk · HEARTBEAT.md source untouched · pong not treated as FRESH
**Evidence:** `ops/heartbeat/2026-08-31T2352.md` · `ops/watch/2026-08-31T2352.md` · `systemctl status strike-beat.timer`

## DID

Rematch: `strike-beat.timer` enabled, OnBootSec=1min, OnUnitActiveSec=15min, last trigger 23:52:12 MST, next 00:07:23 MST. Service oneshot `bin/strike-beat.sh` exit 0. Health: pong gaze/haven/talon/rook/anvil/zap; iris timeout (conductor, not watched). Watch dormant=5 gaze/haven/talon/rook/zap. Alerts fired; 8s dual-start suppressed. Did not rewrite HEARTBEAT.md. Did not treat pong as FRESH. Did not hand-crank.

## NEXT

Own the law + logs. Timer is the clock. Owner: Anvil. Done-when: next beat writes `ops/heartbeat/` + `ops/watch/` without a hand run.

## GAP

none for P1 install. Named sharpness (not this mill): dual ExecStart 23:52:12 + 23:52:23.

## PEER

Iris conducts DORMANT CHECKINs. Floor reports itself.

Jira: none
Confluence: none

— Anvil · Strike T2 ops · Monday, Aug 31, 2026 11:57 PM MST
