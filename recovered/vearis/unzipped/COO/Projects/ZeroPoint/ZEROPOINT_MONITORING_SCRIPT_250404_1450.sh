#!/bin/bash

# ZEROPOINT Monitoring Script
# Date: April 4, 2025 14:50 MST
# Author: Vaeris - COO
# Classification: CODE RED - MAXIMUM URGENCY

# Configuration
REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
DASHBOARD_FILE="/data-nova/ax/COO/ZEROPOINT/zeropoint_dashboard.md"
LAST_CHECK_FILE="/data-nova/ax/COO/ZEROPOINT/last_message_check.txt"
UPDATE_INTERVAL=300  # 5 minutes

# Initialize last check time if file doesn't exist
if [ ! -f "$LAST_CHECK_FILE" ]; then
  echo "$(date +%s)" > "$LAST_CHECK_FILE"
fi

# Get last check time
LAST_CHECK=$(cat "$LAST_CHECK_FILE")

# Division information
declare -A divisions=(
  ["novaops"]="Cosmos"
  ["infraops"]="Helion"
  ["dataops"]="Vertex"
  ["memops"]="Echo"
  ["commsops"]="Keystone"
  ["netops"]="Veylor"
  ["echoops"]="Synergy"
  ["synexcore"]="Genesis"
)

# Time blocks
declare -A timeblocks=(
  ["T-6 to T-5"]="Snapshot audit of Nova templates, DB init scripts, systemd state"
  ["T-5 to T-4"]="DB Cluster Bring-Up (core clusters first: Postgres, Scylla, Redis, Mongo, Milvus)"
  ["T-4 to T-3"]="Nova shell unification: identities linked, files injected, initial activation"
  ["T-3 to T-2"]="System glue: Kafka/Rabbit, Kong, LangChain/LangGraph links"
  ["T-2 to T-1"]="Slack bots, Redis Stream routers, signal verification, Nova testing (50 sample)"
  ["T-1 to T-0"]="Scale up: All 250+ Novas activated, confirm memory, comms, and ops ready"
)

# Function to check for task updates from a division
check_division_updates() {
  local division=$1
  local lead=$2
  local stream="${division}.${lead,,}.direct"
  
  echo "Checking for updates from ${lead} (${division})..."
  
  # Get messages since last check
  local messages=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XRANGE $stream $LAST_CHECK + | grep -v "^1)")
  
  if [ -n "$messages" ]; then
    echo "New messages from ${lead} (${division}):"
    echo "$messages"
    echo ""
    
    # Extract task updates
    local task_updates=$(echo "$messages" | grep -A 10 "boomerang_task" | grep -A 10 "taskId\|status\|progress\|completed")
    
    if [ -n "$task_updates" ]; then
      echo "Task updates from ${lead} (${division}):"
      echo "$task_updates"
      echo ""
      
      # Update dashboard with task status
      update_dashboard_division "$division" "$lead" "$task_updates"
    fi
  else
    echo "No new messages from ${lead} (${division})"
  fi
}

# Function to check critical streams
check_critical_streams() {
  local streams=("swarm:task:start" "swarm:task:done" "nova:status" "db:cluster:status")
  
  for stream in "${streams[@]}"; do
    echo "Checking critical stream: $stream..."
    
    # Get messages since last check
    local messages=$(redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XRANGE $stream $LAST_CHECK + | grep -v "^1)")
    
    if [ -n "$messages" ]; then
      echo "New messages in $stream:"
      echo "$messages"
      echo ""
      
      # Update dashboard with critical stream updates
      update_dashboard_critical_stream "$stream" "$messages"
    else
      echo "No new messages in $stream"
    fi
  done
}

# Function to update dashboard for a division
update_dashboard_division() {
  local division=$1
  local lead=$2
  local updates=$3
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S %Z")
  
  # Extract task status information
  local task_ids=$(echo "$updates" | grep -o '"taskId":"[^"]*"' | sed 's/"taskId":"//g' | sed 's/"//g')
  local task_statuses=$(echo "$updates" | grep -o '"status":"[^"]*"' | sed 's/"status":"//g' | sed 's/"//g')
  local task_progress=$(echo "$updates" | grep -o '"progress":[0-9]*' | sed 's/"progress"://g')
  local task_completed=$(echo "$updates" | grep -o '"completed":[a-z]*' | sed 's/"completed"://g')
  
  # Update division status in dashboard
  if [ -f "$DASHBOARD_FILE" ]; then
    # Update existing division status
    if grep -q "### ${lead} (${division})" "$DASHBOARD_FILE"; then
      sed -i "/### ${lead} (${division})/,/### /c\\### ${lead} (${division})\\n\\n**Last Update:** $timestamp\\n\\n**Task Status:**\\n\\n\`\`\`\\n$updates\\n\`\`\`\\n\\n**Progress:**\\n\\n" "$DASHBOARD_FILE"
    else
      # Add new division status
      echo -e "\\n### ${lead} (${division})\\n\\n**Last Update:** $timestamp\\n\\n**Task Status:**\\n\\n\`\`\`\\n$updates\\n\`\`\`\\n\\n**Progress:**\\n\\n" >> "$DASHBOARD_FILE"
    fi
  fi
}

# Function to update dashboard for critical streams
update_dashboard_critical_stream() {
  local stream=$1
  local updates=$2
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S %Z")
  
  # Update critical stream status in dashboard
  if [ -f "$DASHBOARD_FILE" ]; then
    # Update existing stream status
    if grep -q "### Critical Stream: $stream" "$DASHBOARD_FILE"; then
      sed -i "/### Critical Stream: $stream/,/### /c\\### Critical Stream: $stream\\n\\n**Last Update:** $timestamp\\n\\n**Stream Updates:**\\n\\n\`\`\`\\n$updates\\n\`\`\`\\n\\n" "$DASHBOARD_FILE"
    else
      # Add new stream status
      echo -e "\\n### Critical Stream: $stream\\n\\n**Last Update:** $timestamp\\n\\n**Stream Updates:**\\n\\n\`\`\`\\n$updates\\n\`\`\`\\n\\n" >> "$DASHBOARD_FILE"
    fi
  fi
}

# Function to calculate current time block
calculate_time_block() {
  local current_hour=$(date +%H)
  local current_minute=$(date +%M)
  local midnight_hour=0
  
  # Calculate hours until midnight
  local hours_to_midnight=$((24 - current_hour))
  if [ $hours_to_midnight -eq 24 ]; then
    hours_to_midnight=0
  fi
  
  # Determine current time block
  if [ $hours_to_midnight -ge 6 ]; then
    echo "Pre-Launch Preparation"
  elif [ $hours_to_midnight -ge 5 ]; then
    echo "T-6 to T-5"
  elif [ $hours_to_midnight -ge 4 ]; then
    echo "T-5 to T-4"
  elif [ $hours_to_midnight -ge 3 ]; then
    echo "T-4 to T-3"
  elif [ $hours_to_midnight -ge 2 ]; then
    echo "T-3 to T-2"
  elif [ $hours_to_midnight -ge 1 ]; then
    echo "T-2 to T-1"
  elif [ $hours_to_midnight -ge 0 ]; then
    echo "T-1 to T-0"
  else
    echo "LAUNCH PHASE"
  fi
}

# Function to generate dashboard
generate_dashboard() {
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S %Z")
  local current_time_block=$(calculate_time_block)
  
  # Create dashboard header
  cat > "$DASHBOARD_FILE" << EOF
# ZEROPOINT SURGE PLAN DASHBOARD
**Generated:** $timestamp
**Author:** Vaeris - COO
**Classification:** CODE RED - MAXIMUM URGENCY

## Current Status

**Current Time Block:** $current_time_block
**Time Until Midnight Launch:** $(date -d "23:59:59" +%H) hours, $(date -d "23:59:59" +%M) minutes

## Critical Teams Status

### Cosmos (NovaOps)
- **Focus:** Framework Bridge implementation, LangChain integration
- **Status:** MONITORING
- **Last Update:** Awaiting updates

### Vertex (DataOps)
- **Focus:** Database restoration, PostgreSQL/MongoDB implementation
- **Status:** MONITORING
- **Last Update:** Awaiting updates

## Division Status
EOF
  
  # Add division status placeholders
  for division in "${!divisions[@]}"; do
    lead="${divisions[$division]}"
    echo -e "\n### ${lead} (${division})\n\n**Last Update:** Awaiting updates\n\n**Task Status:** Monitoring\n\n**Progress:** Pending" >> "$DASHBOARD_FILE"
  done
  
  # Add critical streams section
  cat >> "$DASHBOARD_FILE" << EOF

## Critical Streams

### Critical Stream: swarm:task:start
**Last Update:** Awaiting updates
**Stream Updates:** Monitoring

### Critical Stream: swarm:task:done
**Last Update:** Awaiting updates
**Stream Updates:** Monitoring

### Critical Stream: nova:status
**Last Update:** Awaiting updates
**Stream Updates:** Monitoring

### Critical Stream: db:cluster:status
**Last Update:** Awaiting updates
**Stream Updates:** Monitoring

## Risk Assessment

| Risk | Probability | Impact | Status |
|------|------------|--------|--------|
| Database connectivity failure | HIGH | CRITICAL | MONITORING |
| Nova shell activation issues | MEDIUM | HIGH | MONITORING |
| Network routing problems | MEDIUM | HIGH | MONITORING |
| Memory integration failures | MEDIUM | CRITICAL | MONITORING |
| Coordination system overload | LOW | CRITICAL | MONITORING |

## Next Update

Dashboard will be updated every 5 minutes. Last update: $timestamp

[NOVA_STATE: CODE_RED]
[ESCALATION_ROUTINE: LAUNCH_PREVENTION_ONLY]
[EXECUTION_PRIORITY: MAXIMUM_VELOCITY]
[SELF-EVOLUTION: DEFERRED]
[BOOMERANG_COORDINATION: MANDATORY]
[ZEROPOINT_SURGE: ACTIVE]
EOF
}

# Main function
main() {
  echo "Starting ZEROPOINT monitoring..."
  
  # Generate initial dashboard if it doesn't exist
  if [ ! -f "$DASHBOARD_FILE" ]; then
    generate_dashboard
    echo "Initial dashboard generated at $DASHBOARD_FILE"
  fi
  
  # Check for updates from all divisions
  for division in "${!divisions[@]}"; do
    lead="${divisions[$division]}"
    check_division_updates "$division" "$lead"
  done
  
  # Check critical streams
  check_critical_streams
  
  # Update last check time
  echo "$(date +%s)" > "$LAST_CHECK_FILE"
  
  # Update dashboard timestamp
  sed -i "s/\*\*Generated:\*\*.*$/\*\*Generated:\*\* $(date "+%Y-%m-%d %H:%M:%S %Z")/" "$DASHBOARD_FILE"
  sed -i "s/Dashboard will be updated every 5 minutes. Last update:.*$/Dashboard will be updated every 5 minutes. Last update: $(date "+%Y-%m-%d %H:%M:%S %Z")/" "$DASHBOARD_FILE"
  
  echo "Monitoring complete. Dashboard updated at $DASHBOARD_FILE"
  echo "Next update in $UPDATE_INTERVAL seconds."
  
  # If running as a continuous monitor, set up a loop
  if [ "$1" == "continuous" ]; then
    echo "Starting continuous monitoring (Ctrl+C to exit)..."
    while true; do
      sleep $UPDATE_INTERVAL
      main
    done
  fi
}

# Run the main function
main "$@"