#!/bin/bash

# Script to monitor Boomerang System adoption across all teams
# Date: April 4, 2025
# Author: Vaeris (COO)
# Version: 2.0.0 (Updated with system rename)

# Configuration
REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
OUTPUT_FILE="/data-nova/ax/COO/boomerang_system_adoption_status.md"

# Team information
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

# Priority groups
declare -A TEAM_PRIORITIES=(
  ["memcommsops"]=1
  ["commsops"]=1
  ["devops"]=1
  ["dataops"]=1
  ["mlops"]=1
  ["infraops"]=1
  ["secops"]=1
  ["novaops"]=2
  ["evolutionops"]=2
  ["routeops"]=2
  ["consciousnessops"]=3
)

# Function to check if a team has sent any tasks
check_team_sent_tasks() {
  local team=$1
  local lead=$2
  local stream="${team}.${lead,,}.direct"
  
  # Check if the team has sent any tasks in the last hour
  local result=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREVRANGE $stream + - COUNT 100 | grep -c "boomerang_task")
  
  if [ "$result" -gt 0 ]; then
    echo "Yes ($result)"
  else
    echo "No"
  fi
}

# Function to check if a team has received any tasks
check_team_received_tasks() {
  local team=$1
  local lead=$2
  local stream="${team}.${lead,,}.direct"
  
  # Check if the team has received any tasks in the last hour
  local result=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREVRANGE $stream + - COUNT 100 | grep -c "boomerang_task")
  
  if [ "$result" -gt 0 ]; then
    echo "Yes ($result)"
  else
    echo "No"
  fi
}

# Function to check if a team has completed any tasks
check_team_completed_tasks() {
  local team=$1
  local lead=$2
  local stream="${team}.${lead,,}.direct"
  
  # Check if the team has completed any tasks in the last hour
  local result=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREVRANGE $stream + - COUNT 100 | grep -c "completed")
  
  if [ "$result" -gt 0 ]; then
    echo "Yes ($result)"
  else
    echo "No"
  fi
}

# Function to check if a team has confirmed adoption
check_team_confirmed_adoption() {
  local team=$1
  local lead=$2
  local stream="${team}.${lead,,}.direct"
  
  # Check if the team has confirmed adoption in the last hour
  local result=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XREVRANGE $stream + - COUNT 100 | grep -c "adoption")
  
  if [ "$result" -gt 0 ]; then
    echo "Yes"
  else
    echo "No"
  fi
}

# Function to get team status based on deadline
get_team_status() {
  local team=$1
  local priority=${TEAM_PRIORITIES[$team]}
  local current_hour=$(date +%H)
  local current_minute=$(date +%M)
  local deadline_hour
  
  case $priority in
    1) deadline_hour=12 ;;
    2) deadline_hour=14 ;;
    3) deadline_hour=16 ;;
    *) deadline_hour=18 ;;
  esac
  
  if [ $current_hour -lt $deadline_hour ]; then
    echo "On Track"
  elif [ $current_hour -eq $deadline_hour ] && [ $current_minute -le 15 ]; then
    echo "Due Now"
  else
    echo "Overdue"
  fi
}

# Generate the status report
generate_status_report() {
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S %Z")
  
  # Create the header
  cat > $OUTPUT_FILE << EOF
# Boomerang System Adoption Status
**Generated:** $timestamp
**Author:** Vaeris (COO)

## Overview

This report tracks the adoption of the Boomerang System (formerly Nova Task System) across all teams. It is automatically updated every 15 minutes.

## Adoption Status by Team

| Team | Lead | Priority | Deadline | Sent Tasks | Received Tasks | Completed Tasks | Confirmed | Status |
|------|------|----------|----------|------------|----------------|-----------------|-----------|--------|
EOF
  
  # Add each team's status
  for team in "${!TEAM_LEADS[@]}"; do
    lead="${TEAM_LEADS[$team]}"
    priority="${TEAM_PRIORITIES[$team]}"
    
    case $priority in
      1) deadline="12:00 PM" ;;
      2) deadline="2:00 PM" ;;
      3) deadline="4:00 PM" ;;
      *) deadline="6:00 PM" ;;
    esac
    
    sent_tasks=$(check_team_sent_tasks "$team" "$lead")
    received_tasks=$(check_team_received_tasks "$team" "$lead")
    completed_tasks=$(check_team_completed_tasks "$team" "$lead")
    confirmed=$(check_team_confirmed_adoption "$team" "$lead")
    status=$(get_team_status "$team")
    
    echo "| $lead | $team | $priority | $deadline | $sent_tasks | $received_tasks | $completed_tasks | $confirmed | $status |" >> $OUTPUT_FILE
  done
  
  # Add summary
  cat >> $OUTPUT_FILE << EOF

## Summary

- **Priority 1 Teams (12:00 PM)**: Core Teams
- **Priority 2 Teams (2:00 PM)**: Support Teams
- **Priority 3 Teams (4:00 PM)**: Specialized Teams
- **All Teams (6:00 PM)**: Full Operational Status

## System Rename Note

The system has been renamed from "Nova Task System" to "Boomerang System" to better reflect its functionality. All documentation and code has been updated to reflect this change.

## Next Steps

1. Follow up with teams that haven't confirmed adoption
2. Provide support to teams that haven't sent or received tasks
3. Address any issues reported by teams

## Updates

This report is automatically updated every 15 minutes. Last update: $timestamp
EOF
}

# Main function
main() {
  echo "Generating Boomerang System adoption status report..."
  generate_status_report
  echo "Report generated at $OUTPUT_FILE"
  
  # If running as a continuous monitor, set up a loop
  if [ "$1" == "continuous" ]; then
    echo "Starting continuous monitoring (Ctrl+C to exit)..."
    while true; do
      sleep 900  # 15 minutes
      generate_status_report
      echo "Report updated at $(date)"
    done
  fi
}

# Run the main function
main "$@"