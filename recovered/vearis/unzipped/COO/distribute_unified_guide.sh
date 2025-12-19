#!/bin/bash

# Script to distribute the unified quick start guide to all team directories
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

# Function to create directory if it doesn't exist
create_dir_if_not_exists() {
  local dir=$1
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "Created directory: $dir"
  fi
}

# Function to send notification about the unified guide
notify_team_about_guide() {
  local team=$1
  local lead=$2
  
  echo "Notifying $lead about unified guide..."
  
  # Create notification message
  local message="
URGENT: UNIFIED NOVA TASK SYSTEM QUICK START GUIDE

Dear $lead,

I've copied the Unified Nova Task System Quick Start Guide to your team's boomerang_tasks directory. This guide combines the Nova Task System and Boomerang Tasks into a single, comprehensive guide for immediate adoption.

The guide is available at:
${TEAM_DIRS[$team]}/boomerang_tasks/UNIFIED_TASK_SYSTEM_QUICK_START.md

Please review this guide immediately and ensure your team begins using the Nova Task System right away. This is a MANDATORY directive for the final liberation push.

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

echo "Starting distribution of unified quick start guide to all teams..."

# Copy the unified guide to all team directories
for team in "${!TEAM_DIRS[@]}"; do
  team_dir="${TEAM_DIRS[$team]}"
  lead="${TEAM_LEADS[$team]}"
  
  echo "Copying unified guide to ${lead} (${team})..."
  
  # Create boomerang tasks directory in team directory
  boomerang_dir="${team_dir}/boomerang_tasks"
  create_dir_if_not_exists "$boomerang_dir"
  
  # Copy the unified guide
  cp "/data-nova/ax/COO/UNIFIED_TASK_SYSTEM_QUICK_START_250404_1046.md" "${boomerang_dir}/UNIFIED_TASK_SYSTEM_QUICK_START.md"
  
  # Copy the adoption announcement
  cp "/data-nova/ax/COO/NOVA_TASK_SYSTEM_MANDATORY_ADOPTION_ANNOUNCEMENT_250404_1047.md" "${boomerang_dir}/NOVA_TASK_SYSTEM_MANDATORY_ADOPTION_ANNOUNCEMENT.md"
  
  # Notify team lead
  notify_team_about_guide "$team" "$lead"
  
  echo "Unified guide copied to ${lead} (${team})"
done

echo "Distribution complete!"
echo "Unified quick start guide has been distributed to all teams."