#!/bin/bash
# Script to monitor individual Redis streams
# Usage: ./monitor_individual_streams.sh

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Streams to monitor
STREAMS=(
  "urgent.communications"
  "project.keystone.status"
  "project.keystone"
  "mcp.servers.status"
  "coo.vaeris.direct"
)

# Create a function to monitor a single stream
monitor_stream() {
  local stream=$1
  echo "Monitoring stream: $stream"
  
  # Run in a loop to handle reconnections
  while true; do
    redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREAD BLOCK 1000 STREAMS $stream '$'
    echo "Connection to $stream lost. Reconnecting in 3 seconds..."
    sleep 3
  done
}

# Start monitoring each stream in a separate background process
for stream in "${STREAMS[@]}"; do
  monitor_stream "$stream" &
  # Store the PID so we can kill it later if needed
  echo "$!" >> monitor_pids.txt
done

echo "Monitoring started for all streams. PIDs saved to monitor_pids.txt"
echo "Press Ctrl+C to stop all monitoring processes"

# Wait for user to press Ctrl+C
trap "pkill -P $$; rm monitor_pids.txt; echo 'All monitoring stopped'; exit" INT
wait
