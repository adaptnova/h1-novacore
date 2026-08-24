#!/usr/bin/env bash
# pressure-loop.sh — Pathfinder-owned host-pressure oneshot (not dsh-loop-tick).
# Measure swap/io, keep parked furniture parked, write one evidence line.
# No secrets. No NATS/Nebula/Redpanda/Temporal/DSH bounce.
set -u
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOCAL=$(date '+%Y-%m-%d %H:%M:%S %Z')
EVID=/adapt/novas/active/pathfinder/ops/reviews/pressure-loop.jsonl
mkdir -p "$(dirname "$EVID")"

swap_used=$(awk '/SwapTotal/{t=$2} /SwapFree/{f=$2} END{if(t>0) printf "%.0f", (t-f)*100/t; else print 0}' /proc/meminfo)
io_some=$(awk '/^some /{for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"="); print a[2]}}' /proc/pressure/io | head -1)
io_full=$(awk '/^full /{for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"="); print a[2]}}' /proc/pressure/io | head -1)
load=$(awk '{print $1}' /proc/loadavg)
actions=""

if systemctl is-active --quiet society-dash.service 2>/dev/null; then
  systemctl stop society-dash.service || true
  actions="${actions}stop-society-dash;"
fi

if ss -lnt 2>/dev/null | awk '$4 ~ /:15025$/ {found=1} END{exit found?0:1}'; then
  if command -v pm2 >/dev/null 2>&1 || [ -x /data/vast/npm/lib/node_modules/pm2/bin/pm2 ]; then
    sudo -u x -H env PM2_HOME=/home/x/.pm2 /data/vast/npm/lib/node_modules/pm2/bin/pm2 stop opencode-web >/dev/null 2>&1 || true
    sudo -u x -H env PM2_HOME=/home/x/.pm2 /data/vast/npm/lib/node_modules/pm2/bin/pm2 delete opencode-web >/dev/null 2>&1 || true
    sudo -u x -H env PM2_HOME=/home/x/.pm2 /data/vast/npm/lib/node_modules/pm2/bin/pm2 save --force >/dev/null 2>&1 || true
  fi
  actions="${actions}stop-opencode-15025;"
fi

[ -n "$actions" ] || actions="none"

printf '%s\n' "{\"ts\":\"$STAMP\",\"local\":\"$LOCAL\",\"swap_used_pct\":$swap_used,\"io_some_avg10\":${io_some:-0},\"io_full_avg10\":${io_full:-0},\"load1\":$load,\"actions\":\"$actions\"}" >> "$EVID"
echo "PRESSURE $STAMP swap=${swap_used}% io_some=${io_some:-?} io_full=${io_full:-?} load1=$load actions=$actions"
