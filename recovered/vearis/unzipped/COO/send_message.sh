#!/bin/bash
# Script to send messages to Redis streams
# Usage: ./send_message.sh [stream] [message]

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Set COO team name
TEAM_NAME="coo.vaeris"

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 [stream] [message]"
    echo "Example: $0 memcommsops.echo.direct 'Hello, Echo!'"
    exit 1
fi

STREAM=$1
MESSAGE=$2
FROM="$TEAM_NAME"
TIMESTAMP=$(date +%s)

# Send the message
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD $STREAM '*' \
    type message \
    from "$FROM" \
    content "$MESSAGE" \
    timestamp "$TIMESTAMP"

echo "Message sent to $STREAM: $MESSAGE"
