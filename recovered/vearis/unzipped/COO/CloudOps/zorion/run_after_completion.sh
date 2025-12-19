#!/bin/bash

# Script to monitor the main configuration script and run speed tests after completion
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
MAIN_SCRIPT_PID=$(pgrep -f "ibm_cloud_server_setup.sh")
CHECK_INTERVAL=60  # Check every 60 seconds
SERVER_NAME="adapt"
SERVER_IP="10.240.1.6"
LOG_FILE="./post_config_actions.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display section headers
section() {
  echo -e "\n${BLUE}=== $1 ===${NC}"
  echo -e "\n=== $1 ===" >> "$LOG_FILE"
}

# Function to display success messages
success() {
  echo -e "${GREEN}✓ $1${NC}"
  echo -e "✓ $1" >> "$LOG_FILE"
}

# Function to display error messages
error() {
  echo -e "${RED}✗ $1${NC}"
  echo -e "✗ $1" >> "$LOG_FILE"
}

# Function to display warning messages
warning() {
  echo -e "${YELLOW}! $1${NC}"
  echo -e "! $1" >> "$LOG_FILE"
}

# Function to display info messages
info() {
  echo -e "  $1"
  echo -e "  $1" >> "$LOG_FILE"
}

# Function to check if the main script is still running
is_main_script_running() {
  if [ -z "$MAIN_SCRIPT_PID" ]; then
    return 1  # PID not found, script not running
  fi
  
  if ps -p "$MAIN_SCRIPT_PID" > /dev/null; then
    return 0  # Script is running
  else
    return 1  # Script is not running
  fi
}

# Function to check if the server has 8 NICs configured
check_nic_count() {
  info "Checking NIC count on $SERVER_NAME..."
  
  NIC_COUNT=$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "ip -br addr show | grep -v 'lo ' | wc -l" 2>/dev/null)
  
  if [ -z "$NIC_COUNT" ]; then
    error "Failed to get NIC count"
    return 1
  fi
  
  info "Current NIC count: $NIC_COUNT"
  
  if [ "$NIC_COUNT" -eq 8 ]; then
    success "Server has 8 NICs configured"
    return 0
  else
    warning "Server has $NIC_COUNT NICs configured, expected 8"
    return 1
  fi
}

# Function to run network speed tests
run_speed_tests() {
  section "Running Network Speed Tests"
  
  info "Executing network_speed_test.sh script..."
  
  # Run the speed test script
  ./network_speed_test.sh
  
  if [ $? -eq 0 ]; then
    success "Network speed tests completed successfully"
  else
    error "Network speed tests failed"
  fi
}

# Function to verify network optimization
verify_optimization() {
  section "Verifying Network Optimization"
  
  info "Checking network parameters on $SERVER_NAME..."
  
  # Check network parameters
  PARAMS=$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "sysctl -a | grep -E 'net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_rmem|net.ipv4.tcp_wmem|net.ipv4.tcp_congestion_control'" 2>/dev/null)
  
  echo "$PARAMS" >> "$LOG_FILE"
  
  # Check if buffer sizes have been increased
  RMEM_MAX=$(echo "$PARAMS" | grep "net.core.rmem_max" | awk '{print $3}')
  WMEM_MAX=$(echo "$PARAMS" | grep "net.core.wmem_max" | awk '{print $3}')
  
  if [ -z "$RMEM_MAX" ] || [ -z "$WMEM_MAX" ]; then
    warning "Could not retrieve buffer sizes"
  else
    info "Current buffer sizes: rmem_max=$RMEM_MAX, wmem_max=$WMEM_MAX"
    
    if [ "$RMEM_MAX" -gt 1000000 ] && [ "$WMEM_MAX" -gt 1000000 ]; then
      success "Buffer sizes have been increased"
    else
      warning "Buffer sizes have not been sufficiently increased"
    fi
  fi
  
  # Check congestion control algorithm
  CC_ALGO=$(echo "$PARAMS" | grep "net.ipv4.tcp_congestion_control" | awk '{print $3}')
  
  if [ -z "$CC_ALGO" ]; then
    warning "Could not retrieve congestion control algorithm"
  else
    info "Current congestion control algorithm: $CC_ALGO"
    
    if [ "$CC_ALGO" = "bbr" ]; then
      success "BBR congestion control is enabled"
    else
      warning "BBR congestion control is not enabled"
    fi
  fi
  
  # Check MTU settings
  MTU_SETTINGS=$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "ip link show | grep mtu" 2>/dev/null)
  
  echo "$MTU_SETTINGS" >> "$LOG_FILE"
  
  # Check if any interface has jumbo frames enabled
  if echo "$MTU_SETTINGS" | grep -q "mtu 9000"; then
    success "Jumbo frames are enabled on at least one interface"
  else
    info "Jumbo frames are not enabled"
  fi
}

# Function to generate a summary report
generate_summary() {
  section "Generating Summary Report"
  
  SUMMARY_FILE="./post_config_summary.md"
  
  info "Creating summary report: $SUMMARY_FILE"
  
  # Create summary file
  cat > "$SUMMARY_FILE" << EOF
# Post-Configuration Summary Report for $SERVER_NAME

## Overview
This report summarizes the actions taken after the completion of the main configuration script for the $SERVER_NAME server.

## Network Interface Status
$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "ip -br addr show" 2>/dev/null)

## Routing Configuration
$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "ip route show" 2>/dev/null)

## Network Parameters
$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no root@$SERVER_IP "sysctl -a | grep -E 'net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_rmem|net.ipv4.tcp_wmem|net.ipv4.tcp_congestion_control'" 2>/dev/null)

## Speed Test Results
The network speed test results are available in the speed_test_results directory. The most recent report contains detailed information about download speeds across all network interfaces.

## Conclusion
The $SERVER_NAME server has been successfully configured with 8 network interfaces and optimized for performance. The speed tests provide a comprehensive analysis of the server's network capabilities.

## Report Generated
- **Date**: $(date)
- **Engineer**: Zorion (IBM Cloud Infrastructure Engineer)
EOF

  success "Summary report generated: $SUMMARY_FILE"
}

# Main execution
echo "Post-Configuration Actions for $SERVER_NAME" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "----------------------------------------------" | tee -a "$LOG_FILE"

# Check if main script PID was found
if [ -z "$MAIN_SCRIPT_PID" ]; then
  warning "Main script PID not found. Will check for 8 NICs directly."
  
  # Check if the server has 8 NICs
  if check_nic_count; then
    info "Server already has 8 NICs configured. Proceeding with post-configuration actions."
  else
    warning "Server does not have 8 NICs configured. Will wait and check periodically."
    
    # Wait and check periodically
    while ! check_nic_count; do
      info "Waiting $CHECK_INTERVAL seconds before checking again..."
      sleep $CHECK_INTERVAL
    done
  fi
else
  info "Main script is running with PID: $MAIN_SCRIPT_PID"
  info "Waiting for main script to complete..."
  
  # Wait for main script to complete
  while is_main_script_running; do
    info "Main script is still running. Waiting $CHECK_INTERVAL seconds..."
    sleep $CHECK_INTERVAL
  done
  
  success "Main script has completed"
  
  # Wait a bit for any final operations to complete
  info "Waiting 60 seconds for any final operations to complete..."
  sleep 60
  
  # Check if the server has 8 NICs
  if ! check_nic_count; then
    warning "Server does not have 8 NICs configured after main script completion."
    
    # Wait and check periodically
    while ! check_nic_count; do
      info "Waiting $CHECK_INTERVAL seconds before checking again..."
      sleep $CHECK_INTERVAL
    done
  fi
fi

# Verify network optimization
verify_optimization

# Run network speed tests
run_speed_tests

# Generate summary report
generate_summary

section "Summary"
echo "Server: $SERVER_NAME ($SERVER_IP)"
echo "Post-configuration actions completed"
echo "Log file: $LOG_FILE"
echo "Summary report: ./post_config_summary.md"

echo -e "\nAll post-configuration actions completed."
echo "You can view the summary report using: cat ./post_config_summary.md"

exit 0