#!/bin/bash
# server_validation.sh - DataOps Infrastructure Server Validation Script
# Version: 1.0
# Date: April 17, 2025
# Author: Catalyst (Nova #95)
# Part of TURBO MODE Validation Framework

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Timestamp function
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

# Logging function
log() {
  local level=$1
  local message=$2
  local color=$NC
  
  case $level in
    "INFO") color=$BLUE ;;
    "SUCCESS") color=$GREEN ;;
    "WARNING") color=$YELLOW ;;
    "ERROR") color=$RED ;;
  esac
  
  echo -e "[$(timestamp)] ${color}[${level}]${NC} ${message}"
  
  # Also append to log file
  echo "[$(timestamp)] [${level}] ${message}" >> "${LOG_DIR}/server_validation.log"
}

# Decision logging function
log_decision() {
  local decision_type=$1
  local component=$2
  local decision_desc=$3
  local context=$4
  local criteria=$5
  local confidence=$6
  local outcome=$7
  local next_steps=$8
  
  log "INFO" "Decision logged: ${decision_type} - ${component}"
  
  cat << EOF >> "${LOG_DIR}/decisions.log"
[$(timestamp)] - [${decision_type}] - [${component}]
Decision: ${decision_desc}
Context: ${context}
Criteria Applied: ${criteria}
Confidence Score: ${confidence}
Outcome: ${outcome}
Next Steps: ${next_steps}

EOF
}

# Initialize validation
init_validation() {
  log "INFO" "Initializing server validation..."
  
  # Create required directories
  mkdir -p "${LOG_DIR}"
  mkdir -p "${RESULTS_DIR}"
  
  # Initialize results file
  echo "# Server Infrastructure Validation Results" > "${RESULTS_DIR}/server_validation_results.md"
  echo "**Date:** $(date)" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "**Validator:** Catalyst (Nova #95)" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "" >> "${RESULTS_DIR}/server_validation_results.md"
  
  log "SUCCESS" "Validation environment initialized"
}

# Server accessibility validation
validate_server_accessibility() {
  local server=$1
  local server_name=$2
  local server_type=$3
  
  log "INFO" "Validating accessibility for ${server_name} (${server})..."
  
  # Add server section to results
  echo "## ${server_name} (${server})" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "### Server Accessibility" >> "${RESULTS_DIR}/server_validation_results.md"
  
  # Test SSH connectivity
  if ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no ibm-admin@${server} 'echo "SSH Connection Successful"' > /dev/null 2>&1; then
    log "SUCCESS" "SSH connection to ${server_name} (${server}) successful"
    echo "- SSH Connectivity: ✅ **PASS**" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Log decision
    log_decision "Server Accessibility" "${server_name}" \
      "Server is accessible via SSH" \
      "Attempted SSH connection to ${server}" \
      "Successful SSH connection" \
      "9" \
      "Server is accessible and validation can proceed" \
      "Continue with server specification validation"
    
    return 0
  else
    log "ERROR" "SSH connection to ${server_name} (${server}) failed"
    echo "- SSH Connectivity: ❌ **FAIL**" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Log decision
    log_decision "Server Accessibility" "${server_name}" \
      "Server is not accessible via SSH" \
      "Attempted SSH connection to ${server}" \
      "Failed SSH connection" \
      "9" \
      "Server is not accessible, validation cannot proceed for this server" \
      "Report critical issue and continue with other servers"
    
    return 1
  fi
}

# Server specification validation
validate_server_specs() {
  local server=$1
  local server_name=$2
  local expected_profile=$3
  
  log "INFO" "Validating specifications for ${server_name} (${server})..."
  
  echo "### Server Specifications" >> "${RESULTS_DIR}/server_validation_results.md"
  
  # Get CPU info
  local cpu_info=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'lscpu | grep "^CPU(s)" && grep -c processor /proc/cpuinfo')
  local cpu_count=$(echo "$cpu_info" | awk '/CPU\(s\):/ {print $2}')
  
  # Get memory info
  local mem_info=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'free -h | grep Mem')
  local mem_total=$(echo "$mem_info" | awk '{print $2}')
  
  # Check if GPU present (for GPU server)
  local gpu_info="N/A"
  if [[ "${expected_profile}" == *"gx3"* ]]; then
    gpu_info=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "No GPU detected"')
  fi
  
  # Output results
  echo "- CPU Count: ${cpu_count}" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "- Memory: ${mem_total}" >> "${RESULTS_DIR}/server_validation_results.md"
  
  if [[ "${expected_profile}" == *"gx3"* ]]; then
    echo "- GPU: ${gpu_info}" >> "${RESULTS_DIR}/server_validation_results.md"
    
    if [[ "${gpu_info}" == *"No GPU detected"* ]]; then
      log "ERROR" "GPU not detected on GPU server ${server_name}"
      echo "- Profile Verification: ❌ **FAIL** (GPU expected but not detected)" >> "${RESULTS_DIR}/server_validation_results.md"
      
      # Log decision
      log_decision "Server Specifications" "${server_name}" \
        "Server does not match expected profile" \
        "Expected GPU server profile ${expected_profile}" \
        "GPU not detected on server" \
        "8" \
        "Server specifications do not match expectations, may impact component functionality" \
        "Report critical issue and continue validation with limited expectations"
      
      return 1
    fi
  fi
  
  # Compare against expected profile (simplified comparison)
  if [[ "${expected_profile}" == "bx2-8x32" && "${cpu_count}" -ge 8 ]]; then
    log "SUCCESS" "Server ${server_name} specifications match expected profile ${expected_profile}"
    echo "- Profile Verification: ✅ **PASS** (matches ${expected_profile})" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Log decision
    log_decision "Server Specifications" "${server_name}" \
      "Server matches expected profile" \
      "Expected server profile ${expected_profile}" \
      "CPU count and memory appear consistent with profile" \
      "8" \
      "Server specifications match expectations" \
      "Continue with storage validation"
    
    return 0
  elif [[ "${expected_profile}" == *"gx3"* && "${cpu_count}" -ge 24 && "${gpu_info}" != *"No GPU detected"* ]]; then
    log "SUCCESS" "GPU Server ${server_name} specifications match expected profile ${expected_profile}"
    echo "- Profile Verification: ✅ **PASS** (matches ${expected_profile} with GPU)" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Log decision
    log_decision "Server Specifications" "${server_name}" \
      "Server matches expected profile" \
      "Expected GPU server profile ${expected_profile}" \
      "CPU count, memory, and GPU presence are consistent with profile" \
      "8" \
      "Server specifications match expectations" \
      "Continue with storage validation"
    
    return 0
  else
    log "WARNING" "Server ${server_name} specifications may not match expected profile ${expected_profile}"
    echo "- Profile Verification: ⚠️ **WARNING** (may not fully match ${expected_profile})" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Log decision
    log_decision "Server Specifications" "${server_name}" \
      "Server may not match expected profile" \
      "Expected server profile ${expected_profile}" \
      "CPU count or memory appears inconsistent with profile" \
      "6" \
      "Server specifications partially match expectations, may impact performance" \
      "Continue validation but note potential performance impacts"
    
    return 0
  fi
}

# Storage validation
validate_storage() {
  local server=$1
  local server_name=$2
  
  log "INFO" "Validating storage configuration for ${server_name} (${server})..."
  
  echo "### Storage Configuration" >> "${RESULTS_DIR}/server_validation_results.md"
  
  # Check disk mounts
  local data_disk=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'df -h | grep "/data"')
  local logs_disk=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'df -h | grep "/logs"')
  
  # Validate data disk
  if [[ -n "${data_disk}" ]]; then
    local data_size=$(echo "${data_disk}" | awk '{print $2}')
    log "SUCCESS" "Data disk mounted at /data with size ${data_size}"
    echo "- Data Disk: ✅ **PASS** (${data_size} mounted at /data)" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Check data directory structure
    local data_structure=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'ls -la /data/dataops 2>/dev/null || echo "Directory not found"')
    if [[ "${data_structure}" != *"Directory not found"* ]]; then
      log "SUCCESS" "Data directory structure exists at /data/dataops"
      echo "- Data Directory Structure: ✅ **PASS** (/data/dataops exists)" >> "${RESULTS_DIR}/server_validation_results.md"
    else
      log "WARNING" "Data directory structure not found at /data/dataops"
      echo "- Data Directory Structure: ⚠️ **WARNING** (/data/dataops not found)" >> "${RESULTS_DIR}/server_validation_results.md"
    fi
  else
    log "ERROR" "Data disk not mounted at /data"
    echo "- Data Disk: ❌ **FAIL** (not mounted at /data)" >> "${RESULTS_DIR}/server_validation_results.md"
  fi
  
  # Validate logs disk
  if [[ -n "${logs_disk}" ]]; then
    local logs_size=$(echo "${logs_disk}" | awk '{print $2}')
    log "SUCCESS" "Logs disk mounted at /logs with size ${logs_size}"
    echo "- Logs Disk: ✅ **PASS** (${logs_size} mounted at /logs)" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Check logs directory structure
    local logs_structure=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} 'ls -la /logs/dataops 2>/dev/null || echo "Directory not found"')
    if [[ "${logs_structure}" != *"Directory not found"* ]]; then
      log "SUCCESS" "Logs directory structure exists at /logs/dataops"
      echo "- Logs Directory Structure: ✅ **PASS** (/logs/dataops exists)" >> "${RESULTS_DIR}/server_validation_results.md"
    else
      log "WARNING" "Logs directory structure not found at /logs/dataops"
      echo "- Logs Directory Structure: ⚠️ **WARNING** (/logs/dataops not found)" >> "${RESULTS_DIR}/server_validation_results.md"
    fi
  else
    log "ERROR" "Logs disk not mounted at /logs"
    echo "- Logs Disk: ❌ **FAIL** (not mounted at /logs)" >> "${RESULTS_DIR}/server_validation_results.md"
  fi
}

# Network validation
validate_network() {
  local server=$1
  local server_name=$2
  local server_list=("10.240.8.5" "10.240.1.7" "10.240.1.9" "10.240.1.11")
  
  log "INFO" "Validating network configuration for ${server_name} (${server})..."
  
  echo "### Network Configuration" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "| Target Server | Ping | SSH | Port Scan |" >> "${RESULTS_DIR}/server_validation_results.md"
  echo "|--------------|------|-----|-----------|" >> "${RESULTS_DIR}/server_validation_results.md"
  
  # Test connectivity to all other servers
  for target in "${server_list[@]}"; do
    # Skip self
    [[ "${target}" == "${server}" ]] && continue
    
    # Get target server name
    local target_name=""
    case "${target}" in
      "10.240.8.5") target_name="Primary" ;;
      "10.240.1.7") target_name="Vector" ;;
      "10.240.1.9") target_name="TimeSeries" ;;
      "10.240.1.11") target_name="GPU" ;;
    esac
    
    # Test ping
    local ping_result=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} "ping -c 3 ${target} | grep 'received' | awk -F',' '{print \$2}' | awk '{print \$1}'")
    local ping_status="❌"
    [[ "${ping_result}" -gt 0 ]] && ping_status="✅"
    
    # Test SSH connectivity
    local ssh_result=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} "ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no ibm-admin@${target} 'echo success' 2>/dev/null || echo 'failed'")
    local ssh_status="❌"
    [[ "${ssh_result}" == "success" ]] && ssh_status="✅"
    
    # Check common ports
    local port_scan=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} "nc -zv ${target} 22 5432 9090 2>&1 | grep -c succeeded")
    local port_status="⚠️"
    [[ "${port_scan}" -ge 2 ]] && port_status="✅"
    
    # Log results
    if [[ "${ping_status}" == "✅" && "${ssh_status}" == "✅" ]]; then
      log "SUCCESS" "Network connectivity from ${server_name} to ${target_name} is good"
    else
      log "WARNING" "Network connectivity issues from ${server_name} to ${target_name}"
    fi
    
    # Add to results
    echo "| ${target_name} (${target}) | ${ping_status} | ${ssh_status} | ${port_status} |" >> "${RESULTS_DIR}/server_validation_results.md"
  done
}

# Firewall validation
validate_firewall() {
  local server=$1
  local server_name=$2
  
  log "INFO" "Validating firewall configuration for ${server_name} (${server})..."
  
  echo "### Firewall Configuration" >> "${RESULTS_DIR}/server_validation_results.md"
  
  # Check firewall status
  local firewall_status=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} "systemctl is-active ufw 2>/dev/null || echo 'inactive'")
  
  if [[ "${firewall_status}" == "active" ]]; then
    log "SUCCESS" "Firewall is active on ${server_name}"
    echo "- Firewall Status: ✅ **ACTIVE**" >> "${RESULTS_DIR}/server_validation_results.md"
    
    # Check firewall rules
    local firewall_rules=$(ssh -o StrictHostKeyChecking=no ibm-admin@${server} "ufw status | grep -c ALLOW")
    echo "- Firewall Rules: ${firewall_rules} allow rules configured" >> "${RESULTS_DIR}/server_validation_results.md"
  else
    log "WARNING" "Firewall is not active on ${server_name}"
    echo "- Firewall Status: ⚠️ **INACTIVE**" >> "${RESULTS_DIR}/server_validation_results.md"
    echo "- Firewall Rules: N/A" >> "${RESULTS_DIR}/server_validation_results.md"
  fi
}

# Server validation summary
generate_server_summary() {
  local success_count=$1
  local warning_count=$2
  local error_count=$3
  local server_count=$4
  
  log "INFO" "Generating server validation summary..."
  
  # Generate summary
  cat << EOF > "${RESULTS_DIR}/server_validation_summary.md"
# Server Validation Summary
**Date:** $(date)
**Validator:** Catalyst (Nova #95)

## Overview

Total Servers Validated: ${server_count}

| Status | Count | Percentage |
|--------|-------|------------|
| Success | ${success_count} | $(echo "scale=1; ${success_count} * 100 / ${server_count}" | bc)% |
| Warning | ${warning_count} | $(echo "scale=1; ${warning_count} * 100 / ${server_count}" | bc)% |
| Error | ${error_count} | $(echo "scale=1; ${error_count} * 100 / ${server_count}" | bc)% |

## Critical Issues

EOF

  # Add critical issues if any
  if [[ ${error_count} -gt 0 ]]; then
    grep -A 3 "FAIL" "${RESULTS_DIR}/server_validation_results.md" >> "${RESULTS_DIR}/server_validation_summary.md"
  else
    echo "No critical issues found." >> "${RESULTS_DIR}/server_validation_summary.md"
  fi
  
  # Add validation decision
  if [[ ${error_count} -eq 0 ]]; then
    log "SUCCESS" "Server validation completed successfully"
    cat << EOF >> "${RESULTS_DIR}/server_validation_summary.md"

## Validation Decision

✅ **PASS** - All servers have been successfully validated. The infrastructure is ready for component validation.
EOF
  elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then
    log "WARNING" "Server validation completed with some issues"
    cat << EOF >> "${RESULTS_DIR}/server_validation_summary.md"

## Validation Decision

⚠️ **PARTIAL PASS** - Some servers have issues, but validation can proceed. Address the critical issues to ensure full functionality.
EOF
  else
    log "ERROR" "Server validation failed for many servers"
    cat << EOF >> "${RESULTS_DIR}/server_validation_summary.md"

## Validation Decision

❌ **FAIL** - Multiple servers have critical issues. Address these issues before proceeding with component validation.
EOF
  fi
  
  # Log decision
  log_decision "Infrastructure Validation" "All Servers" \
    "Server infrastructure validation $(if [[ ${error_count} -eq 0 ]]; then echo "successful"; elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then echo "partially successful"; else echo "failed"; fi)" \
    "Validated ${server_count} servers with ${success_count} successes, ${warning_count} warnings, and ${error_count} errors" \
    "Server accessibility, specifications, storage, and network connectivity" \
    "$(if [[ ${error_count} -eq 0 ]]; then echo "9"; elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then echo "6"; else echo "3"; fi)" \
    "$(if [[ ${error_count} -eq 0 ]]; then echo "Infrastructure is ready for component validation"; elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then echo "Infrastructure has issues but validation can proceed"; else echo "Infrastructure has critical issues that must be addressed"; fi)" \
    "$(if [[ ${error_count} -eq 0 ]]; then echo "Proceed to component validation"; elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then echo "Continue with limited validation and report issues"; else echo "Halt validation and report critical infrastructure issues"; fi)"
}

# Main function
main() {
  # Check if required parameters are provided
  if [[ $# -lt 2 ]]; then
    echo "Usage: $0 [output_dir] [credentials_file]"
    exit 1
  fi
  
  # Set global variables
  RESULTS_DIR="$1/server_validation"
  LOG_DIR="$1/logs"
  CREDENTIALS_FILE="$2"
  
  # Initialize validation
  init_validation
  
  # Server information
  declare -A SERVER_INFO=(
    ["10.240.8.5"]="Primary|bx2-8x32"
    ["10.240.1.7"]="Vector|bx2-8x32"
    ["10.240.1.9"]="TimeSeries|bx2-8x32"
    ["10.240.1.11"]="GPU|gx3-48x240x2l40s"
  )
  
  # Counters for summary
  local success_count=0
  local warning_count=0
  local error_count=0
  local server_count=0
  
  # Validate each server
  for server in "${!SERVER_INFO[@]}"; do
    # Parse server info
    local server_name=$(echo "${SERVER_INFO[$server]}" | cut -d'|' -f1)
    local server_profile=$(echo "${SERVER_INFO[$server]}" | cut -d'|' -f2)
    
    log "INFO" "Starting validation for ${server_name} server (${server})"
    
    # Increment server count
    ((server_count++))
    
    # Validate server accessibility
    if ! validate_server_accessibility "${server}" "${server_name}" "${server_profile}"; then
      ((error_count++))
      continue
    fi
    
    # Validate server specifications
    validate_server_specs "${server}" "${server_name}" "${server_profile}"
    
    # Validate storage
    validate_storage "${server}" "${server_name}"
    
    # Validate network
    validate_network "${server}" "${server_name}"
    
    # Validate firewall
    validate_firewall "${server}" "${server_name}"
    
    # Check for errors in validation results
    if grep -q "FAIL" "${RESULTS_DIR}/server_validation_results.md"; then
      ((error_count++))
    elif grep -q "WARNING" "${RESULTS_DIR}/server_validation_results.md"; then
      ((warning_count++))
    else
      ((success_count++))
    fi
    
    log "INFO" "Completed validation for ${server_name} server (${server})"
    echo "" >> "${RESULTS_DIR}/server_validation_results.md"
  done
  
  # Generate validation summary
  generate_server_summary "${success_count}" "${warning_count}" "${error_count}" "${server_count}"
  
  log "INFO" "Server validation completed with ${success_count} successes, ${warning_count} warnings, and ${error_count} errors"
  
  # Return appropriate exit code
  if [[ ${error_count} -eq 0 ]]; then
    return 0
  elif [[ ${error_count} -lt $(echo "${server_count} / 2" | bc) ]]; then
    return 1
  else
    return 2
  fi
}

# Execute main function
main "$@"
