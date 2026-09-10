#!/usr/bin/env bash
# SGLang MTP-acceptance watchdog for the Pennyroyal endpoint.
# Restarts sglang-qwen38.service if spec_accept_rate stays degraded (< THRESHOLD)
# under SUSTAINED LOAD (num_running_reqs > 0) for MAX_LOW consecutive polls.
# Idle (no running requests) never triggers — acceptance is 0 when idle.
# Guards against the NEXTN acceptance-uptime-decay (Mamba radix ghost-node class).
set -u
BASE=http://127.0.0.1:8001
THRESHOLD=0.35
MAX_LOW=5
low=0
CB=$(command -v curl)
while true; do
  sleep 60
  m=$("$CB" -fsS --max-time 6 "$BASE/metrics" 2>/dev/null) || continue
  rate=$(printf '%s\n' "$m" | grep 'spec_accept_rate' | grep 'model_name="pennyroyal"' | awk '{print $NF}' | head -1)
  running=$(printf '%s\n' "$m" | grep 'num_running_reqs' | grep 'model_name="pennyroyal"' | awk '{print $NF}' | head -1)
  rate=${rate:-0}; running=${running:-0}
  if awk "BEGIN{exit !($running>0 && $rate<$THRESHOLD)}"; then
    low=$((low+1))
    echo "watchdog $(date +%H:%M:%S): low acceptance rate=$rate running=$running low_count=$low"
    if [ "$low" -ge "$MAX_LOW" ]; then
      echo "watchdog $(date +%H:%M:%S): acceptance degraded persistently (rate=$rate) -> restart sglang"
      systemctl restart sglang-qwen38.service
      low=0
      sleep 45
    fi
  else
    low=0
  fi
done
