#!/bin/bash
# Script to monitor Redis streams for Tier 1 and Tier 2 leaders
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Default streams to monitor
STREAMS=(
    "ops.pathfinder.direct"
    "novaops.cosmos.direct"
    "evoops.nexus.direct"
    "rd.synergy.direct"
    "growthops.oracle.direct"
    "tier1.coordination"
)

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
