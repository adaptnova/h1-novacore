#!/bin/bash

# Script to monitor responses from teams about critical issues
# Date: April 4, 2025
# Author: Vaeris (COO)

# Configuration
REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
TASK_TRACKER="/data-nova/ax/COO/critical_issues_task_tracker.md"
LAST_CHECK_FILE="/data-nova/ax/COO/last_message_check.txt"

# Initialize last check time if file doesn't exist
if [ ! -f "$LAST_CHECK_FILE" ]; then
  echo "$(date +%s)" > "$LAST_CHECK_FILE"
fi

# Get last check time
LAST_CHECK=$(cat "$LAST_CHECK_FILE")

# Function to check for new messages from a team
check_team_messages() {
  local team=$1
  local lead=$2
  local stream="${team}.${lead,,}.direct"
  
  echo "Checking for new messages from ${lead} (${team})..."
  
  # Get messages since last check
  local messages=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XRANGE $stream $LAST_CHECK + | grep -v "^1)")
  
  if [ -n "$messages" ]; then
    echo "New messages from ${lead} (${team}):"
    echo "$messages"
    echo ""
    
    # Update task tracker with new information
    update_task_tracker "$team" "$lead" "$messages"
  else
    echo "No new messages from ${lead} (${team})"
  fi
}

# Function to update task tracker with new information
update_task_tracker() {
  local team=$1
  local lead=$2
  local messages=$3
  local timestamp=$(date "+%H:%M MST")
  
  echo "Updating task tracker with new information from ${lead}..."
  
  case "$team" in
    "dataops")
      # Update Vertex tasks
      if [[ "$messages" == *"SSH"* ]]; then
        sed -i "/### SSH Connectivity Restoration/,/### Database Restoration/s/- 14:13 MST: Requested urgent assistance from Helion/- 14:13 MST: Requested urgent assistance from Helion\n  - $timestamp: Received response from Vertex about SSH connectivity/" "$TASK_TRACKER"
      fi
      
      if [[ "$messages" == *"Database"* || "$messages" == *"PostgreSQL"* || "$messages" == *"MongoDB"* ]]; then
        sed -i "/### Database Restoration/,/### Monitoring System Restoration/s/- 14:12 MST: Offered assistance with Docker container verification/- 14:12 MST: Offered assistance with Docker container verification\n  - $timestamp: Received response from Vertex about database restoration/" "$TASK_TRACKER"
      fi
      
      if [[ "$messages" == *"Monitor"* || "$messages" == *"Prometheus"* || "$messages" == *"Grafana"* ]]; then
        sed -i "/### Monitoring System Restoration/,/### Message Queue Restoration/s/- 14:12 MST: Offered assistance with Prometheus, Grafana, and AlertManager/- 14:12 MST: Offered assistance with Prometheus, Grafana, and AlertManager\n  - $timestamp: Received response from Vertex about monitoring system restoration/" "$TASK_TRACKER"
      fi
      ;;
      
    "novaops")
      # Update Cosmos tasks
      if [[ "$messages" == *"Framework Bridge"* || "$messages" == *"framework_bridge"* ]]; then
        sed -i "/### Framework Bridge Implementation/,/### Boomerang System Adoption/s/- 14:13 MST: Sent direct assistance offer to Cosmos/- 14:13 MST: Sent direct assistance offer to Cosmos\n  - $timestamp: Received response from Cosmos about Framework Bridge implementation/" "$TASK_TRACKER"
      fi
      
      if [[ "$messages" == *"Boomerang"* ]]; then
        sed -i "/### Boomerang System Adoption/,/### LangChain Integration/s/- 14:13 MST: Offered assistance with Redis stream monitoring and task creation/- 14:13 MST: Offered assistance with Redis stream monitoring and task creation\n  - $timestamp: Received response from Cosmos about Boomerang system adoption/" "$TASK_TRACKER"
      fi
      
      if [[ "$messages" == *"LangChain"* ]]; then
        sed -i "/### LangChain Integration/,/## Cross-Team Coordination/s/- 14:13 MST: Offered assistance with LangChain component integration/- 14:13 MST: Offered assistance with LangChain component integration\n  - $timestamp: Received response from Cosmos about LangChain integration/" "$TASK_TRACKER"
      fi
      ;;
      
    "infraops")
      # Update Helion tasks
      if [[ "$messages" == *"SSH"* ]]; then
        sed -i "/### Helion (InfraOps) Support/,/### Keystone (CommsOps) Support/s/- 14:13 MST: Requested urgent SSH connectivity assistance/- 14:13 MST: Requested urgent SSH connectivity assistance\n  - $timestamp: Received response from Helion about SSH connectivity assistance/" "$TASK_TRACKER"
      fi
      ;;
      
    "commsops")
      # Update Keystone tasks
      if [[ "$messages" == *"Boomerang"* ]]; then
        sed -i "/### Keystone (CommsOps) Support/,/## Boomerang System Status/s/- 14:08 MST: Keystone sent urgent onboarding messages to both teams/- 14:08 MST: Keystone sent urgent onboarding messages to both teams\n  - $timestamp: Received response from Keystone about Boomerang system/" "$TASK_TRACKER"
      fi
      ;;
  esac
  
  # Update last updated timestamp
  sed -i "s/Last Updated:.*/Last Updated: $timestamp/" "$TASK_TRACKER"
}

# Main function
main() {
  echo "Starting critical response monitoring..."
  echo "Last check time: $(date -d @$LAST_CHECK)"
  
  # Check for new messages from critical teams
  check_team_messages "dataops" "Vertex"
  check_team_messages "novaops" "Cosmos"
  check_team_messages "infraops" "Helion"
  check_team_messages "commsops" "Keystone"
  
  # Update last check time
  echo "$(date +%s)" > "$LAST_CHECK_FILE"
  
  echo "Monitoring complete. Task tracker updated."
  echo "Next check in 5 minutes."
  
  # If running as a continuous monitor, set up a loop
  if [ "$1" == "continuous" ]; then
    echo "Starting continuous monitoring (Ctrl+C to exit)..."
    while true; do
      sleep 300  # 5 minutes
      main
    done
  fi
}

# Run the main function
main "$@"