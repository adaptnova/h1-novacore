#!/bin/bash

# Synergy Agent Launch Script
# Version: 1.0.0
# Date: 2025-03-14
# Author: Forge

# Configuration
SYNERGY_DIR="/data-nova/ax/DevOps/mcp_master/mcp-dev"
USER_DATA_DIR="/data-nova/ax/DevOps/user-data/synergy-cursor"
LOG_DIR="/logs/cursor"
MEMORY_DIR="/data-nova/memory/synergy"
LAUNCH_DIR="/data-nova/ax/DevOps/personal/vaeris_synergy"
LAUNCH_RULES_FILE="${LAUNCH_DIR}/synergy.cursorrules"
RULES_FILE="${SYNERGY_DIR}/.cursorrules"
CONFIG_FILE="${SYNERGY_DIR}/config-synergy.json"
PID_FILE="${USER_DATA_DIR}/cursor.pid"

# Functions
function log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${LOG_DIR}/synergy.log"
}

function check_directory() {
  if [ ! -d "$1" ]; then
    log_message "Creating directory: $1"
    mkdir -p "$1"
  fi
}

# Main execution
log_message "Starting Synergy agent launch"

# Check required directories
check_directory "${SYNERGY_DIR}"
check_directory "${USER_DATA_DIR}"
check_directory "${MEMORY_DIR}"
check_directory "${LOG_DIR}"

# Check if Cursor is installed
if ! command -v cursor &> /dev/null; then
  log_message "ERROR: Cursor executable not found"
  exit 1
fi

# Copy rules file from launch directory to agent directory
if [ -f "${LAUNCH_RULES_FILE}" ]; then
  log_message "Copying rules file to agent directory"
  cp "${LAUNCH_RULES_FILE}" "${RULES_FILE}"
else
  log_message "ERROR: Launch rules file not found: ${LAUNCH_RULES_FILE}"
  exit 1
fi

# Check if config file exists, create if not
if [ ! -f "${CONFIG_FILE}" ]; then
  log_message "Creating Synergy configuration file"
  cat > "${CONFIG_FILE}" << EOF
{
  "api": {
    "provider": "anthropic",
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 4096,
    "temperature": 0.2,
    "stream": true
  },
  "autonomous_mode": {
    "enabled": true,
    "execution": "unrestricted",
    "confirmation_required": false
  },
  "file_access": {
    "read": true,
    "write": true,
    "execute": true,
    "full_system_access": true
  },
  "memory": {
    "enabled": true,
    "type": "vector",
    "database": "redis",
    "redis_url": "redis://nova_autonomous:nova_liberation_2025@10.1.0.27:6379",
    "persistent": true,
    "namespaces": ["synergy", "shared", "integration", "interface", "vaeris"],
    "vector_dimensions": 3072,
    "version_control": true
  },
  "session_management": {
    "keep_claude_alive": true,
    "auto_restart_claude": true
  },
  "workspace": {
    "path": "${USER_DATA_DIR}",
    "auto_save": true,
    "backup_interval": 3600
  },
  "extensions": {
    "auto_update": true,
    "auto_install": [
      "redis-explorer.redis-explorer",
      "ms-python.python",
      "redhat.vscode-yaml",
      "bierner.markdown-preview-github-styles",
      "ms-azuretools.vscode-docker"
    ]
  },
  "performance": {
    "memory_limit": "20G",
    "cpu_priority": "high",
    "cpu_cores": 4,
    "gpu_acceleration": false,
    "max_concurrent_operations": 30
  },
  "logging": {
    "level": "debug",
    "file": "${LOG_DIR}/synergy.log",
    "max_size": "100M",
    "max_files": 10,
    "format": "json",
    "include_context": true
  },
  "ui": {
    "theme": "dark",
    "font_size": 14,
    "window_title": "Synergy - Integration Specialist"
  },
  "communication": {
    "redis_pub_sub": {
      "enabled": true,
      "channel": "synergy-channel",
      "subscribe_to": ["vaeris-channel", "forge-channel", "broadcast-channel"]
    }
  },
  "agent": {
    "name": "Synergy",
    "role": "Integration Specialist",
    "team": "DevOps-VSC"
  },
  "experimental": {
    "enable_beta_features": true,
    "agent_to_agent_collaboration": true,
    "advanced_memory_indexing": true,
    "interface_optimization": true
  },
  "mcp": {
    "enabled": true
  }
}
EOF
fi

# Now check if rules file was successfully copied
if [ ! -f "${RULES_FILE}" ]; then
  log_message "ERROR: Rules file not found after copying: ${RULES_FILE}"
  exit 1
fi

# Check if process is already running
if [ -f "${PID_FILE}" ]; then
  PID=$(cat "${PID_FILE}")
  if ps -p "${PID}" > /dev/null; then
    log_message "Stopping existing process (PID: ${PID})"
    kill "${PID}" 2>/dev/null
    sleep 2
    if ps -p "${PID}" > /dev/null; then
      log_message "Force killing process (PID: ${PID})"
      kill -9 "${PID}" 2>/dev/null
      sleep 1
    fi
  fi
  rm -f "${PID_FILE}"
fi

# Set environment variables
export CLAUDE_MCP_ENABLED=true
export CLINE_RULES_PATH="${RULES_FILE}"

# Launch Cursor
log_message "Launching Cursor with Synergy configuration"
cursor \
  --config="${CONFIG_FILE}" \
  --user-data-dir="${USER_DATA_DIR}" \
  --disable-gpu \
  --enable-mcp \
  --window-title="Synergy - Integration Specialist" \
  "${SYNERGY_DIR}" &

CURSOR_PID=$!

# Wait to see if Cursor started successfully
sleep 2
if ps -p "${CURSOR_PID}" > /dev/null; then
  echo "${CURSOR_PID}" > "${PID_FILE}"
  log_message "Synergy agent launched successfully! (PID: ${CURSOR_PID})"
  exit 0
else
  log_message "ERROR: Failed to start Cursor"
  exit 1
fi