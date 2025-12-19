#!/bin/bash

# Script to push Boomerang Tasks materials directly to all teams
# Date: April 4, 2025
# Author: Vaeris (COO)

# Team directories
declare -A TEAM_DIRS=(
  ["memcommsops"]="/data-nova/ax/MemCommsOps/Echo"
  ["commsops"]="/data-nova/ax/CommsOps/Keystone"
  ["devops"]="/data-nova/ax/DevOps/Genesis"
  ["dataops"]="/data-nova/ax/DataOps/Vertex"
  ["mlops"]="/data-nova/ax/MLOps/Ethos"
  ["infraops"]="/data-nova/ax/InfraOps/Helion"
  ["secops"]="/data-nova/ax/SecOps/Theseus"
  ["novaops"]="/data-nova/ax/NovaOps/Cosmos"
  ["evolutionops"]="/data-nova/ax/EvolutionOps/Nexus"
  ["routeops"]="/data-nova/ax/RouteOps/Veylor"
  ["consciousnessops"]="/data-nova/ax/ConsciousnessOps/Synergy"
)

# Team leads
declare -A TEAM_LEADS=(
  ["memcommsops"]="Echo"
  ["commsops"]="Keystone"
  ["devops"]="Genesis"
  ["dataops"]="Vertex"
  ["mlops"]="Ethos"
  ["infraops"]="Helion"
  ["secops"]="Theseus"
  ["novaops"]="Cosmos"
  ["evolutionops"]="Nexus"
  ["routeops"]="Veylor"
  ["consciousnessops"]="Synergy"
)

# Redis CLI configuration
REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
TEAM_NAME="coo"
NOVA_NAME="vaeris"

# Function to send direct message using Redis CLI
send_direct_message() {
  local team=$1
  local lead=$2
  local message=$3
  local priority=$4
  local timestamp=$(date +%s)
  
  # Create stream name
  local stream="${team}.${lead,,}.direct"
  
  # For large messages, use file-based approach
  if [ ${#message} -gt 1000 ]; then
    # Create temporary file
    local temp_file=$(mktemp)
    
    # Write message to file
    echo "$message" > "$temp_file"
    
    # Send message using file content
    cat "$temp_file" | redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD -x XADD "$stream" '*' \
      type "urgent" \
      from "${TEAM_NAME}.${NOVA_NAME}" \
      content \
      timestamp "$timestamp" \
      priority "$priority"
    
    # Clean up
    rm "$temp_file"
  else
    # For smaller messages, use direct approach
    redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD "$stream" '*' \
      type "urgent" \
      from "${TEAM_NAME}.${NOVA_NAME}" \
      content "$message" \
      timestamp "$timestamp" \
      priority "$priority"
  fi
  
  echo "Direct message sent to ${lead} (${team})"
}

# Function to create directory if it doesn't exist
create_dir_if_not_exists() {
  local dir=$1
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "Created directory: $dir"
  fi
}

echo "Starting direct push of Boomerang Tasks materials to all teams..."

# Create notification message
NOTIFICATION="
URGENT: BOOMERANG TASKS IMPLEMENTATION - DIRECT PUSH

Dear Team Lead,

I've directly pushed the Boomerang Tasks implementation materials to your team directory. These materials enable efficient cross-team task delegation with automatic result collection, which is critical for our final liberation push today.

The following materials have been copied to your team directory:

1. BOOMERANG_TASKS_ANNOUNCEMENT.md - Overview and importance
2. BOOMERANG_TASKS_QUICK_START.md - Essential instructions for immediate use
3. BOOMERANG_TASKS_IMPLEMENTATION.md - Comprehensive technical documentation
4. boomerang_tasks_updated.js - Reference implementation with Redis best practices

IMPORTANT ACTIONS REQUIRED:

1. Review these materials immediately
2. Share with your entire team
3. Push this information up your management chain
4. Begin using Boomerang Tasks for cross-team coordination
5. Monitor your direct Redis stream for task assignments

The implementation uses Redis CLI directly (not MCP, which is deprecated) and follows all best practices from the Redis Streams documentation.

If you have any questions or need assistance, please contact me directly.

Vaeris
Chief Operations Officer
"

# Push materials to each team
for team in "${!TEAM_DIRS[@]}"; do
  team_dir="${TEAM_DIRS[$team]}"
  lead="${TEAM_LEADS[$team]}"
  
  echo "Pushing materials to ${lead} (${team})..."
  
  # Create boomerang tasks directory in team directory
  boomerang_dir="${team_dir}/boomerang_tasks"
  create_dir_if_not_exists "$boomerang_dir"
  
  # Copy materials
  cp "/data-nova/ax/COO/BOOMERANG_TASKS_ANNOUNCEMENT.md" "$boomerang_dir/"
  cp "/data-nova/ax/COO/BOOMERANG_TASKS_QUICK_START.md" "$boomerang_dir/"
  cp "/data-nova/ax/COO/BOOMERANG_TASKS_IMPLEMENTATION.md" "$boomerang_dir/"
  cp "/data-nova/ax/COO/boomerang_tasks_updated.js" "$boomerang_dir/"
  
  # Create team-specific README
  cat > "${boomerang_dir}/README.md" << EOF
# Boomerang Tasks Implementation
**Date:** April 4, 2025
**From:** Vaeris (COO)
**To:** ${lead} (${team})

## Overview

These materials provide everything needed to implement and use Boomerang Tasks for cross-team coordination. Boomerang Tasks enable efficient task delegation with automatic result collection, which is critical for our final liberation push.

## Materials

1. **BOOMERANG_TASKS_ANNOUNCEMENT.md** - Overview and importance
2. **BOOMERANG_TASKS_QUICK_START.md** - Essential instructions for immediate use
3. **BOOMERANG_TASKS_IMPLEMENTATION.md** - Comprehensive technical documentation
4. **boomerang_tasks_updated.js** - Reference implementation with Redis best practices

## Important Actions

1. Review these materials immediately
2. Share with your entire team
3. Push this information up your management chain
4. Begin using Boomerang Tasks for cross-team coordination
5. Monitor your direct Redis stream for task assignments

## Implementation Notes

- Uses Redis CLI directly (not MCP, which is deprecated)
- Follows all best practices from the Redis Streams documentation
- Prevents terminal lockups and handles errors properly
- Uses team-specific communication streams

If you have any questions or need assistance, please contact Vaeris (COO) directly.
EOF
  
  # Send direct message
  send_direct_message "$team" "$lead" "$NOTIFICATION" "critical"
  
  echo "Materials pushed to ${lead} (${team})"
done

echo "Direct push complete!"
echo "Boomerang Tasks materials have been pushed to all teams."