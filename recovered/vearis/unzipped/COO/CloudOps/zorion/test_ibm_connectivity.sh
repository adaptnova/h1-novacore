#!/bin/bash
# Script to test IBM Cloud connectivity and diagnose issues
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="ibm_connectivity_test.log"

# IBM Cloud endpoints to test
ENDPOINTS=(
  "cloud.ibm.com|IBM Cloud Main Website"
  "s3.us-south.cloud-object-storage.appdomain.cloud|IBM Cloud Object Storage US South"
  "s3.us-east.cloud-object-storage.appdomain.cloud|IBM Cloud Object Storage US East"
  "s3.eu-gb.cloud-object-storage.appdomain.cloud|IBM Cloud Object Storage UK"
  "s3.eu-de.cloud-object-storage.appdomain.cloud|IBM Cloud Object Storage Germany"
  "s3.jp-tok.cloud-object-storage.appdomain.cloud|IBM Cloud Object Storage Tokyo"
  "api.softlayer.com|IBM Cloud Classic Infrastructure API"
  "api.service.softlayer.com|IBM Cloud Classic Service API"
  "containers.cloud.ibm.com|IBM Cloud Kubernetes Service"
  "registry.ng.bluemix.net|IBM Cloud Container Registry"
)

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

# Function to test connectivity to an endpoint
test_endpoint() {
  local endpoint=$1
  local description=$2
  local interface=$3
  
  log "Testing connectivity to $description ($endpoint) via $interface..."
  
  # Create the test command
  local test_cmd="curl -v --interface $interface --max-time 10 https://$endpoint 2>&1"
  
  # Execute the test command
  local result=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$test_cmd")
  
  # Check for successful connection
  if echo "$result" | grep -q "Connected to"; then
    success "Connected to $endpoint via $interface"
    
    # Check for SSL handshake
    if echo "$result" | grep -q "SSL connection"; then
      success "SSL handshake successful with $endpoint via $interface"
      
      # Check for HTTP response
      if echo "$result" | grep -q "HTTP/"; then
        local http_status=$(echo "$result" | grep "HTTP/" | head -1 | awk '{print $3}')
        success "Received HTTP response $http_status from $endpoint via $interface"
        return 0
      else
        error "No HTTP response from $endpoint via $interface"
      fi
    else
      error "SSL handshake failed with $endpoint via $interface"
    fi
  else
    error "Failed to connect to $endpoint via $interface"
  fi
  
  return 1
}

# Function to run traceroute to an endpoint
run_traceroute() {
  local endpoint=$1
  local description=$2
  local interface=$3
  
  log "Running traceroute to $description ($endpoint) via $interface..."
  
  # Create the traceroute command
  local traceroute_cmd="traceroute -i $interface -T -p 443 $endpoint"
  
  # Execute the traceroute command
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$traceroute_cmd"
}

# Function to check DNS resolution
check_dns() {
  local endpoint=$1
  local description=$2
  
  log "Checking DNS resolution for $description ($endpoint)..."
  
  # Create the DNS lookup command
  local dns_cmd="nslookup $endpoint"
  
  # Execute the DNS lookup command
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$dns_cmd"
}

# Function to check firewall rules
check_firewall() {
  section "Checking Firewall Rules"
  
  # Check iptables rules
  log "Checking iptables rules..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables -L -n -v"
  
  # Check for any IBM-specific rules
  log "Checking for IBM-specific rules..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables-save | grep -i ibm"
}

# Function to check routing
check_routing() {
  section "Checking Routing"
  
  # Check routing table
  log "Checking routing table..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip route show"
  
  # Check routing rules
  log "Checking routing rules..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip rule show"
}

# Function to test download from IBM Cloud Object Storage
test_download() {
  local endpoint=$1
  local description=$2
  local interface=$3
  
  log "Testing download from $description ($endpoint) via $interface..."
  
  # Create a test file in IBM Cloud Object Storage (this would require proper authentication)
  # For this test, we'll use a public URL if available
  local test_url="https://$endpoint/speedtest-cos-bucket/100MB.bin"
  
  # Create the download command
  local download_cmd="curl --interface $interface -o /dev/null -w '%{speed_download}' $test_url"
  
  # Execute the download command
  local speed=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$download_cmd")
  
  # Convert to MB/s
  local speed_mbps=$(echo "scale=2; $speed / 1048576" | bc)
  
  log "Download speed from $description via $interface: $speed_mbps MB/s"
}

# Main execution
echo "IBM Cloud Connectivity Test" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "----------------------------------------------" | tee -a "$LOG_FILE"

# Check DNS resolution for all endpoints
section "Checking DNS Resolution"
for endpoint_info in "${ENDPOINTS[@]}"; do
  IFS='|' read -r endpoint description <<< "$endpoint_info"
  check_dns "$endpoint" "$description"
done

# Check firewall rules
check_firewall

# Check routing
check_routing

# Test connectivity to all endpoints via each interface
section "Testing Connectivity via Each Interface"
for interface in eth0 eth1 eth4 eth5 eth6 eth7; do
  log "Testing connectivity via $interface..."
  
  # Get IP address for this interface
  ip_addr=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}' | head -1")
  
  if [ -z "$ip_addr" ]; then
    error "No IP address found for $interface, skipping tests"
    continue
  fi
  
  log "Using IP address $ip_addr for $interface"
  
  for endpoint_info in "${ENDPOINTS[@]}"; do
    IFS='|' read -r endpoint description <<< "$endpoint_info"
    test_endpoint "$endpoint" "$description" "$interface"
    
    # If connection fails, run traceroute
    if [ $? -ne 0 ]; then
      run_traceroute "$endpoint" "$description" "$interface"
    fi
  done
  
  # Test download from IBM Cloud Object Storage
  test_download "s3.us-south.cloud-object-storage.appdomain.cloud" "IBM Cloud Object Storage US South" "$interface"
done

section "Summary"
log "IBM Cloud connectivity test completed"
log "Check $LOG_FILE for detailed results"

echo -e "\nIBM Cloud connectivity test completed."
exit 0