#!/bin/bash
# Script to test load balancing with current configuration
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="load_balancing_test.log"
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
cat > /tmp/lb_test.sh << 'EOF'
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
  
  # Get the interface used for this connection
  local iface=$(get_interface $dest)
  
  echo "Test $test_num: Connection to $dest uses interface $iface"
  echo "$test_num,$dest,$iface" >> /tmp/lb_results.csv
}

# Initialize results file
echo "Test,Destination,Interface" > /tmp/lb_results.csv

# Run tests with different destinations
destinations=(
  "8.8.8.8"
  "1.1.1.1"
  "cloud.ibm.com"
  "s3.us-south.cloud-object-storage.appdomain.cloud"
  "s3.us-east.cloud-object-storage.appdomain.cloud"
)

# Run multiple tests for each destination
for i in $(seq 1 20); do
  for dest in "${destinations[@]}"; do
    run_test $dest $i
  done
done

# Analyze results
echo -e "\n=== Interface Usage Summary ==="
echo "Interface,Count,Percentage"
total=$(grep -v "Test,Destination" /tmp/lb_results.csv | wc -l)
for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  count=$(grep ",$iface$" /tmp/lb_results.csv | wc -l)
  percentage=$(echo "scale=2; $count * 100 / $total" | bc)
  echo "$iface,$count,$percentage%"
done

# Show distribution by destination
echo -e "\n=== Distribution by Destination ==="
for dest in "${destinations[@]}"; do
  echo -e "\nDestination: $dest"
  echo "Interface,Count,Percentage"
  dest_total=$(grep ",$dest," /tmp/lb_results.csv | wc -l)
  for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
    count=$(grep ",$dest,$iface$" /tmp/lb_results.csv | wc -l)
    percentage=$(echo "scale=2; $count * 100 / $dest_total" | bc)
    echo "$iface,$count,$percentage%"
  done
done
EOF

# Copy the script to the server
log "Copying test script to the server..."
scp -o StrictHostKeyChecking=no /tmp/lb_test.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/lb_test.sh"

# Run the test script
log "Running load balancing test..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "/tmp/lb_test.sh"

# Get the results
log "Getting test results..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat /tmp/lb_results.csv" > lb_results.csv

section "Test Results"
log "Load balancing test completed"
log "Results saved to lb_results.csv"

echo -e "\nLoad balancing test completed. Check $LOG_FILE for details."