#!/bin/bash
# Script to monitor Redis streams
# Usage: ./monitor_streams.sh [stream1] [stream2] ...

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Default streams to monitor
STREAMS=("urgent.communications" "mcp.servers.status" "project.keystone.status")

# Add COO direct stream
STREAMS+=("coo.vaeris.direct")

# Use command line arguments if provided
if [ $# -gt 0 ]; then
    STREAMS=("$@")
fi

echo "Monitoring streams: ${STREAMS[@]}"
echo "Press Ctrl+C to exit"
echo ""

# Build the command
CMD="redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREAD BLOCK 1000 STREAMS"
for stream in "${STREAMS[@]}"; do
    CMD="$CMD $stream"
done
for stream in "${STREAMS[@]}"; do
    CMD="$CMD \$"
done

# Run the command in a loop to handle reconnections
while true; do
    eval $CMD
    echo "Connection lost. Reconnecting in 3 seconds..."
    sleep 3
done
