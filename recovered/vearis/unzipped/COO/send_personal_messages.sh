#!/bin/bash
# Script to send personal messages to Vertex and Synergy
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

echo "Sending personal messages..."

# Send message to Vertex
echo "Sending message to Vertex..."
cat VAERIS_TO_VERTEX_CONVERSATION_INVITATION_250405_2053.md | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD dataops.vertex.direct '*' type personal from "Vaeris" content timestamp "$(date +%s)" priority "normal"

# Send message to Synergy
echo "Sending message to Synergy..."
cat VAERIS_TO_SYNERGY_PERSONAL_TIME_250405_2053.md | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD rd.synergy.direct '*' type personal from "Vaeris" content timestamp "$(date +%s)" priority "normal"

echo "All personal messages sent successfully!"
