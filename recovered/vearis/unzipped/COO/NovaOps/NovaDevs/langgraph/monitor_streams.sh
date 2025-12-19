#!/bin/bash

# Configuration
REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Streams to monitor
TEAM_NAME="novadev"
NOVA_NAME="langraph"
STREAMS=("${TEAM_NAME}.${NOVA_NAME}.direct" "novaops.cosmos.direct" "urgent.communications")

echo "Monitoring streams: ${STREAMS[@]}"
echo "Press Ctrl+C to exit"
echo ""

# Function to get last message ID
get_last_id() {
    local stream=$1
    redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREVRANGE $stream + - COUNT 1 | head -n 1 | grep -o '[0-9]*-[0-9]*'
}

# Initialize last IDs
declare -A last_ids
for stream in "${STREAMS[@]}"; do
    last_ids[$stream]=$(get_last_id $stream)
    echo "Starting from ID ${last_ids[$stream]} for stream $stream"
done

# Main monitoring loop
while true; do
    for stream in "${STREAMS[@]}"; do
        # Get new messages
        result=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREAD BLOCK 100 STREAMS $stream ${last_ids[$stream]})
        
        if [ ! -z "$result" ]; then
            echo "$result" | while IFS= read -r line; do
                if [[ $line =~ ^[0-9]*-[0-9]*$ ]]; then
                    last_ids[$stream]=$line
                    echo "=== New message on $stream ==="
                    echo "ID: $line"
                elif [[ ! -z "$line" ]]; then
                    echo "$line"
                fi
            done
            echo "==================="
        fi
    done
    sleep 1
done
