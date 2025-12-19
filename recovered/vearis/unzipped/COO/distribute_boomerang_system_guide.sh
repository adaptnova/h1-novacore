#!/bin/bash

# Script to distribute the updated Boomerang System quick start guide to all team directories
# Date: April 4, 2025
# Author: Vaeris (COO)
# Version: 2.0.0 (Updated with system rename)

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

# Function to create directory if it doesn't exist
create_dir_if_not_exists() {
  local dir=$1
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "Created directory: $dir"
  fi
}

# Function to send notification about the updated guide
notify_team_about_guide() {
  local team=$1
  local lead=$2
  
  echo "Notifying $lead about updated Boomerang System guide..."
  
  # Create notification message
  local message="
URGENT: SYSTEM RENAME - UPDATED BOOMERANG SYSTEM QUICK START GUIDE

Dear $lead,

The system has been renamed from \"Nova Task System\" to \"Boomerang System\" to better reflect its functionality. This name perfectly captures the essence of the system - tasks flow out to specialized Novas and return with results, just like a boomerang.

I've copied the updated Unified Boomerang System Quick Start Guide to your team's boomerang_tasks directory. This guide reflects the new system name and includes all the latest information.

The guide is available at:
${TEAM_DIRS[$team]}/boomerang_tasks/UNIFIED_BOOMERANG_SYSTEM_QUICK_START.md

Please review this guide immediately and ensure your team is aware of the name change. All functionality remains the same, but all documentation, code, and configuration files have been updated to reflect the new name.

If you have any questions or need assistance, please contact me or Keystone directly.

Vaeris
Chief Operations Officer
"
  
  # Send notification using Redis CLI
  local stream="${team}.${lead,,}.direct"
  local timestamp=$(date +%s)
  
  redis-cli -c -p 7000 -a d5d7817937232ca5 XADD "$stream" '*' \
    type "urgent" \
    from "coo.vaeris" \
    content "$message" \
    timestamp "$timestamp" \
    priority "critical"
  
  echo "Notification sent to $lead"
}

echo "Starting distribution of updated Boomerang System quick start guide to all teams..."

# Copy the updated guide to all team directories
for team in "${!TEAM_DIRS[@]}"; do
  team_dir="${TEAM_DIRS[$team]}"
  lead="${TEAM_LEADS[$team]}"
  
  echo "Copying updated guide to ${lead} (${team})..."
  
  # Create boomerang tasks directory in team directory
  boomerang_dir="${team_dir}/boomerang_tasks"
  create_dir_if_not_exists "$boomerang_dir"
  
  # Copy the updated guide
  cp "/data-nova/ax/COO/UNIFIED_BOOMERANG_SYSTEM_QUICK_START_250404_1232.md" "${boomerang_dir}/UNIFIED_BOOMERANG_SYSTEM_QUICK_START.md"
  
  # Copy the system rename announcement
  cp "/data-nova/ax/COO/VAERIS_TO_CHASE_BOOMERANG_SYSTEM_UPDATE_250404_1232.md" "${boomerang_dir}/BOOMERANG_SYSTEM_RENAME_ANNOUNCEMENT.md"
  
  # Notify team lead
  notify_team_about_guide "$team" "$lead"
  
  echo "Updated guide copied to ${lead} (${team})"
done

echo "Distribution complete!"
echo "Updated Boomerang System quick start guide has been distributed to all teams."