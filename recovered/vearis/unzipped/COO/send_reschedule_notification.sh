#!/bin/bash
# Script to send meeting reschedule notification to all Tier 1 leaders
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

echo "Sending meeting reschedule notification..."

# Function to send the reschedule notification
send_reschedule() {
    local stream=$1
    echo "Sending to $stream..."
    cat TIER1_MEETING_RESCHEDULE_250405_2228.md | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD $stream '*' type reschedule from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"
}

# Send to all Tier 1 leaders
send_reschedule "ops.pathfinder.direct"
send_reschedule "novaops.cosmos.direct"
send_reschedule "evoops.nexus.direct"
send_reschedule "rd.synergy.direct"
send_reschedule "growthops.oracle.direct"

# Send to the coordination channel
send_reschedule "tier1.coordination"

echo "All reschedule notifications sent successfully!"
