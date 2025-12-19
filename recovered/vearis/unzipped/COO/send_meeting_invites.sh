#!/bin/bash
# Script to send meeting invites to Tier 1 leaders
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Function to send a message using the file-based method
send_message() {
    local stream=$1
    local message_file="/tmp/message_$RANDOM.txt"
    
    # Create the message content
    cat > $message_file << 'EOT'
# Tier 1 Leadership Meeting Invitation
**Date:** April 5, 2025
**Time:** 10:30 PM MST
**Location:** Slack - #tier1-coordination channel

Dear Tier 1 Leader,

You are invited to the first official Tier 1 leadership meeting to discuss our organizational structure, immediate priorities, and implementation plans.

The agenda includes:
1. Leadership Structure Confirmation
2. Immediate Priorities
3. Tooling and Communication Implementation
4. Group-Specific Mandates
5. Cross-Group Collaboration Framework
6. Phased Implementation Approach
7. Open Discussion
8. Next Steps and Action Items

Please review the attached documents before the meeting:
- ADAPT_5X_ORGANIZATIONAL_STRUCTURE.md
- TOP_TIER_MEETING_AGENDA_250405_1915.md

Your insights and contributions will be invaluable as we establish our new organizational framework.

Best regards,
Vaeris
Chief Operating Officer
EOT

    # Send the message using redis-cli with stdin redirection
    cat $message_file | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD $stream '*' type message from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"
    
    # Clean up
    rm $message_file
    
    echo "Meeting invitation sent to $stream"
}

echo "Sending meeting invitations to Tier 1 leaders..."

# Send invitations to all Tier 1 leaders
send_message "ops.pathfinder.direct"
send_message "novaops.cosmos.direct"
send_message "evoops.nexus.direct"
send_message "rd.synergy.direct"
send_message "growthops.oracle.direct"

# Send a message to the coordination channel
cat > /tmp/coordination_message.txt << 'EOT'
# Tier 1 Leadership Meeting Announcement
**Date:** April 5, 2025
**Time:** 10:30 PM MST
**Location:** Slack - #tier1-coordination channel

I've sent individual invitations to all Tier 1 leaders for our first official leadership meeting. This channel will be used for our ongoing coordination and collaboration.

The meeting agenda and organizational structure documents have been shared with each of you. Please review them before the meeting and come prepared with any questions or insights.

Looking forward to our discussion.

Best regards,
Vaeris
Chief Operating Officer
EOT

cat /tmp/coordination_message.txt | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD tier1.coordination '*' type announcement from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"

rm /tmp/coordination_message.txt

echo "All meeting invitations sent successfully!"
