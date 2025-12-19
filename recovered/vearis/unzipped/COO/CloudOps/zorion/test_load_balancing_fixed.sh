#!/bin/bash
# Script to test load balancing with current configuration
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="load_balancing_test_fixed.log"
TEST_COUNT=20

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to display section headers
section() {
  log "${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  log "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  log "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  log "${YELLOW}! $1${NC}"
}

# Initialize log file
> "$LOG_FILE"

section "Load Balancing Test"
log "Testing load balancing with current configuration"

# Create test script on the server
cat > /tmp/lb_test_fixed.sh << 'EOF'
#!/bin/bash

# Function to get the interface used for a connection
get_interface() {
  local dest=$1
  ip route get $dest | grep -oP 'dev \K\S+'
}

# Function to run a test and record the interface used
run_test() {
  local dest=$1
  local test_num=$2
  local dest_name=$3
  
  # Get the interface used for this connection
  local iface=$(get_interface $dest)
  
  echo "Test $test_num: Connection to $dest_name ($dest) uses interface $iface"
  echo "$test_num,$dest_name,$dest,$iface" >> /tmp/lb_results_fixed.csv
}

# Initialize results file
echo "Test,Destination,IP,Interface" > /tmp/lb_results_fixed.csv

# Run tests with different destinations
# Using IP addresses instead of domain names
declare -A destinations
destinations=(
  ["Google DNS"]="8.8.8.8"
  ["Cloudflare DNS"]="1.1.1.1"
  ["IBM Cloud"]="72.247.204.160"
  ["IBM COS US South"]="169.62.82.68"
  ["IBM COS US East"]="169.63.118.82"
)

# Run multiple tests for each destination
for i in $(seq 1 20); do
  for dest_name in "${!destinations[@]}"; do
    run_test "${destinations[$dest_name]}" $i "$dest_name"
  done
done

# Analyze results
echo -e "\n=== Interface Usage Summary ==="
echo "Interface,Count,Percentage"
total=$(grep -v "Test,Destination" /tmp/lb_results_fixed.csv | wc -l)
for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  count=$(grep ",$iface$" /tmp/lb_results_fixed.csv | wc -l)
  percentage=$(echo "scale=2; $count * 100 / $total" | bc)
  echo "$iface,$count,$percentage%"
done

# Show distribution by destination
echo -e "\n=== Distribution by Destination ==="
for dest_name in "${!destinations[@]}"; do
  echo -e "\nDestination: $dest_name (${destinations[$dest_name]})"
  echo "Interface,Count,Percentage"
  dest_total=$(grep ",$dest_name," /tmp/lb_results_fixed.csv | wc -l)
  for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
    count=$(grep ",$dest_name,.*,$iface$" /tmp/lb_results_fixed.csv | wc -l)
    percentage=$(echo "scale=2; $count * 100 / $dest_total" | bc)
    echo "$iface,$count,$percentage%"
  done
done

# Test internal routing
echo -e "\n=== Internal Routing Test ==="
for subnet in {1..8}; do
  dest="10.240.${subnet}.1"
  iface=$(get_interface $dest)
  echo "Connection to subnet $subnet gateway ($dest) uses interface $iface"
done
EOF

# Copy the script to the server
log "Copying test script to the server..."
scp -o StrictHostKeyChecking=no /tmp/lb_test_fixed.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/lb_test_fixed.sh"

# Run the test script
log "Running load balancing test..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "/tmp/lb_test_fixed.sh"

# Get the results
log "Getting test results..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat /tmp/lb_results_fixed.csv" > lb_results_fixed.csv

section "Test Results"
log "Load balancing test completed"
log "Results saved to lb_results_fixed.csv"

echo -e "\nLoad balancing test completed. Check $LOG_FILE for details."