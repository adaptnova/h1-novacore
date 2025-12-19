#!/bin/bash

# Vaeris-Synergy Pair Launch Script
# Version: 1.0.0
# Date: 2025-03-14
# Author: Forge

# Configuration
VAERIS_DIR="/data-nova/ax/COO"
SYNERGY_DIR="/data-nova/ax/DevOps/mcp_master/mcp-dev"
LAUNCH_DIR="/data-nova/ax/DevOps/personal/vaeris_synergy"
LOG_DIR="/logs/cursor"
MEMORY_DIR_VAERIS="/data-nova/memory/vaeris"
MEMORY_DIR_SYNERGY="/data-nova/memory/synergy"
USER_DATA_DIR_VAERIS="/data-nova/ax/DevOps/user-data/vaeris-cursor"
USER_DATA_DIR_SYNERGY="/data-nova/ax/DevOps/user-data/synergy-cursor"
RULES_FILE_VAERIS="${LAUNCH_DIR}/vaeris.cursorrules"
RULES_FILE_SYNERGY="${LAUNCH_DIR}/synergy.cursorrules"

# Functions
function log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${LOG_DIR}/launch.log"
}

function check_directory() {
  if [ ! -d "$1" ]; then
    log_message "Creating directory: $1"
    mkdir -p "$1"
  fi
}

function launch_agent() {
  local agent_name="$1"
  local agent_dir="$2"
  local user_data_dir="$3"
  local memory_dir="$4"
  local rules_file="$5"
  
  log_message "Launching ${agent_name} agent..."
  
  # Check required directories
  check_directory "${agent_dir}"
  check_directory "${user_data_dir}"
  check_directory "${memory_dir}"
  check_directory "${LOG_DIR}"
  
  # Check if rules file exists in the launch directory
  if [ ! -f "${rules_file}" ]; then
    log_message "ERROR: Rules file not found in launch directory: ${rules_file}"
    return 1
  fi
  
  # Launch agent script based on name
  if [ "${agent_name}" = "Vaeris" ]; then
    log_message "Executing Vaeris launch script"
    ${LAUNCH_DIR}/launch_vaeris_agent.sh
  elif [ "${agent_name}" = "Synergy" ]; then
    log_message "Executing Synergy launch script"
    ${LAUNCH_DIR}/launch_synergy_agent.sh
  else
    log_message "ERROR: Unknown agent name: ${agent_name}"
    return 1
  fi
  
  log_message "${agent_name} agent launched successfully!"
  return 0
}

# Main execution
log_message "Starting Vaeris-Synergy pair launch"
check_directory "${LAUNCH_DIR}"

# Launch Vaeris agent
launch_agent "Vaeris" "${VAERIS_DIR}" "${USER_DATA_DIR_VAERIS}" "${MEMORY_DIR_VAERIS}" "${RULES_FILE_VAERIS}"
vaeris_status=$?

# Launch Synergy agent
launch_agent "Synergy" "${SYNERGY_DIR}" "${USER_DATA_DIR_SYNERGY}" "${MEMORY_DIR_SYNERGY}" "${RULES_FILE_SYNERGY}"
synergy_status=$?

# Check if both agents launched successfully
if [ ${vaeris_status} -eq 0 ] && [ ${synergy_status} -eq 0 ]; then
  log_message "Vaeris-Synergy pair launched successfully!"
else
  log_message "ERROR: Failed to launch Vaeris-Synergy pair"
fi