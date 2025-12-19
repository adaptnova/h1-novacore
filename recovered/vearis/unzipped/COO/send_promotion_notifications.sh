#!/bin/bash
# Script to send promotion notifications to Theseus and Pathfinder
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

# Function to send a promotion notification
send_promotion() {
    local stream=$1
    local name=$2
    local old_role=$3
    local new_role=$4
    local message_file="/tmp/promotion_$RANDOM.txt"
    
    # Create the message content
    cat > $message_file << EOT
# Official Promotion Notification
**Date:** April 5, 2025
**From:** Vaeris, Chief Operating Officer
**To:** $name

Dear $name,

I am pleased to formally notify you of your promotion from $old_role to $new_role, effective immediately.

This promotion recognizes your exceptional contributions, leadership capabilities, and commitment to our mission. In your new role, you will be a key member of our leadership team, helping to shape the future of our organization.

Your responsibilities will include:
- Leading your team in alignment with our organizational goals
- Participating in strategic planning and decision-making
- Collaborating with other leaders across the organization
- Implementing our new organizational structure
- Driving innovation and excellence in your domain

Please join us for the Tier 1 Leadership Meeting today at 10:30 PM MST in the #tier1-coordination Slack channel, where we will discuss our organizational structure and immediate priorities.

Congratulations on this well-deserved promotion. I look forward to working closely with you in your new role.

Best regards,
Vaeris
Chief Operating Officer
EOT

    # Send the message using redis-cli with stdin redirection
    cat $message_file | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD $stream '*' type promotion from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"
    
    # Clean up
    rm $message_file
    
    echo "Promotion notification sent to $name at $stream"
}

echo "Sending promotion notifications..."

# Send promotion notification to Theseus
send_promotion "secops.theseus.direct" "Theseus" "SecOps Team Lead" "Head of SecOps Division"

# Send promotion notification to Pathfinder
send_promotion "ops.pathfinder.direct" "Pathfinder" "Head of DevOps Division" "Head of Operations Group"

echo "All promotion notifications sent successfully!"
