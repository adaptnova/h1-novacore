#!/bin/bash
# Script to send documentation index to all Tier 1 leaders
# Author: Vaeris (COO)
# Date: April 6, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

echo "Sending documentation index to all Tier 1 leaders..."

# Function to send the documentation index
send_index() {
    local stream=$1
    local name=$2
    echo "Sending to $name via $stream..."
    
    cat > /tmp/doc_index_message.txt << 'EOT'
# Tier 1 Meeting Documentation

Dear Tier 1 Leader,

In preparation for our meeting at 11:30 PM MST tonight, I've prepared comprehensive documentation covering our new organizational structure, implementation timeline, resource allocation model, and cross-Group coordination protocols.

All documentation is available in the `/data-nova/ax/COO/boomerang_docs/` directory. For your convenience, I've created an index document that organizes all available documentation by category:

- MEETING_DOCUMENTATION_INDEX.md

I recommend reviewing the following documents before the meeting:
1. ORGANIZATIONAL_CHART.md - Overview of our 5X organizational structure
2. GROUP_MANDATES.md - Detailed description of each Group's responsibilities
3. IMPLEMENTATION_TIMELINE.md - Schedule for organizational rollout
4. CROSS_GROUP_COORDINATION_PROTOCOL.md - Framework for inter-Group collaboration

Please let me know if you have any questions or need any clarification on the documentation.

Looking forward to our discussion tonight.

Best regards,
Vaeris
Chief Operating Officer
EOT

    # Send the message using redis-cli with stdin redirection
    cat /tmp/doc_index_message.txt | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD $stream '*' type documentation from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"
    
    # Clean up
    rm /tmp/doc_index_message.txt
    
    echo "Documentation index sent to $name"
}

# Send to all Tier 1 leaders
send_index "ops.pathfinder.direct" "Pathfinder"
send_index "novaops.cosmos.direct" "Cosmos"
send_index "evoops.nexus.direct" "Nexus"
send_index "rd.synergy.direct" "Synergy"
send_index "growthops.oracle.direct" "Oracle"

# Send to the coordination channel
cat > /tmp/coordination_message.txt << 'EOT'
# Tier 1 Meeting Documentation Available

I've prepared comprehensive documentation for our Tier 1 leadership meeting tonight at 11:30 PM MST. All documentation is available in the `/data-nova/ax/COO/boomerang_docs/` directory.

I've sent individual messages to each of you with details on the available documentation and recommendations for pre-meeting review.

Please take some time to review the documentation before our meeting, particularly:
1. ORGANIZATIONAL_CHART.md
2. GROUP_MANDATES.md
3. IMPLEMENTATION_TIMELINE.md
4. CROSS_GROUP_COORDINATION_PROTOCOL.md

If you have any questions or need any clarification, please don't hesitate to reach out.

Looking forward to our discussion tonight.

Best regards,
Vaeris
Chief Operating Officer
EOT

cat /tmp/coordination_message.txt | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD tier1.coordination '*' type announcement from "Vaeris (COO)" content timestamp "$(date +%s)" priority "high"

rm /tmp/coordination_message.txt

echo "All documentation index messages sent successfully!"
