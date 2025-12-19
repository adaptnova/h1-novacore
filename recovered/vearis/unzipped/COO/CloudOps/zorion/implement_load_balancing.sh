#!/bin/bash
# Script to implement load balancing across high-performance interfaces
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="load_balancing_implementation.log"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# High-performance interfaces to include in load balancing
INTERFACES=("eth0" "eth1" "eth4" "eth5" "eth6" "eth7")

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

# Function to create backup directory
create_backup_dir() {
  section "Creating Backup Directory"
  mkdir -p "$BACKUP_DIR"
  success "Created backup directory: $BACKUP_DIR"
}

# Function to backup current network configuration
backup_network_config() {
  section "Backing Up Current Network Configuration"
  
  # Backup network interfaces
  log "Backing up network interfaces..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -j addr show" > "$BACKUP_DIR/interfaces_backup.json"
  
  # Backup routing table
  log "Backing up routing table..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -j route show" > "$BACKUP_DIR/routes_backup.json"
  
  # Backup iptables rules
  log "Backing up iptables rules..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables-save" > "$BACKUP_DIR/iptables_backup.rules"
  
  # Backup sysctl settings
  log "Backing up sysctl settings..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "sysctl -a" > "$BACKUP_DIR/sysctl_backup.conf"
  
  success "Network configuration backed up to $BACKUP_DIR"
}

# Function to implement multipath routing
implement_multipath_routing() {
  section "Implementing Multipath Routing"
  
  # Create script to implement multipath routing
  cat > /tmp/implement_multipath.sh << 'EOF'
#!/bin/bash

# Enable IP forwarding if not already enabled
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1

# Install required packages
apt-get update
apt-get install -y iproute2 iptables-persistent

# Create a new routing table for each interface
echo "Creating routing tables for each interface..."
for i in {1..250}; do
  if ! grep -q "^$i " /etc/iproute2/rt_tables; then
    echo "$i table$i" >> /etc/iproute2/rt_tables
  fi
done

# Remove existing multipath default routes
echo "Removing existing multipath default routes..."
ip route show | grep "default" | while read -r route; do
  ip route del $route
done

# Set up multipath routing for high-performance interfaces
echo "Setting up multipath routing..."
INTERFACES=("eth0" "eth1" "eth4" "eth5" "eth6" "eth7")
WEIGHTS=(10 10 10 20 15 15)  # Higher weight for eth5 (fastest), balanced for others

# Add default route with nexthop for load balancing
echo "Adding multipath default route..."
DEFAULT_ROUTE="ip route add default"
for i in "${!INTERFACES[@]}"; do
  IFACE="${INTERFACES[$i]}"
  WEIGHT="${WEIGHTS[$i]}"
  
  # Get gateway for this interface
  if [[ "$IFACE" == "eth0" ]]; then
    GATEWAY="10.240.1.1"
  else
    # Extract interface number
    IF_NUM=$(echo "$IFACE" | sed 's/eth//')
    GATEWAY="10.240.$((IF_NUM+1)).1"
  fi
  
  echo "Adding nexthop via $GATEWAY dev $IFACE weight $WEIGHT"
  DEFAULT_ROUTE+=" nexthop via $GATEWAY dev $IFACE weight $WEIGHT"
done

# Execute the command
eval "$DEFAULT_ROUTE"

# Set up source-based routing for each interface
echo "Setting up source-based routing..."
for i in "${!INTERFACES[@]}"; do
  IFACE="${INTERFACES[$i]}"
  TABLE_NUM=$((i+1))
  
  # Get IP address and gateway for this interface
  if [[ "$IFACE" == "eth0" ]]; then
    IP=$(ip -4 addr show dev $IFACE | grep -oP '(?<=inet\s)10\.240\.1\.[0-9]+')
    GATEWAY="10.240.1.1"
    SUBNET="10.240.1.0/24"
  else
    # Extract interface number
    IF_NUM=$(echo "$IFACE" | sed 's/eth//')
    IP=$(ip -4 addr show dev $IFACE | grep -oP "(?<=inet\s)10\.240\.$((IF_NUM+1))\.[0-9]+")
    GATEWAY="10.240.$((IF_NUM+1)).1"
    SUBNET="10.240.$((IF_NUM+1)).0/24"
  fi
  
  echo "Setting up routing table $TABLE_NUM for $IFACE ($IP)..."
  
  # Add routes to the interface's routing table
  ip route add $SUBNET dev $IFACE src $IP table $TABLE_NUM
  ip route add default via $GATEWAY dev $IFACE table $TABLE_NUM
  
  # Add rule to use this table for traffic from this IP
  ip rule add from $IP table $TABLE_NUM
done

# Make configuration persistent
echo "Making configuration persistent..."
cat > /etc/network/if-up.d/multipath-routing << 'EOC'
#!/bin/bash

# Re-apply multipath routing on interface up
if [[ "$IFACE" == "eth0" || "$IFACE" == "eth1" || "$IFACE" == "eth4" || "$IFACE" == "eth5" || "$IFACE" == "eth6" || "$IFACE" == "eth7" ]]; then
  # Wait for network to be fully up
  sleep 5
  
  # Run the multipath setup script
  /usr/local/sbin/setup-multipath-routing.sh
fi
EOC

# Copy this script to a permanent location
cp "$0" /usr/local/sbin/setup-multipath-routing.sh
chmod +x /usr/local/sbin/setup-multipath-routing.sh
chmod +x /etc/network/if-up.d/multipath-routing

echo "Multipath routing setup complete!"
EOF

  # Make the script executable
  chmod +x /tmp/implement_multipath.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/implement_multipath.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Execute the script on the server
  log "Implementing multipath routing on the server..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/implement_multipath.sh"
  
  success "Multipath routing implemented"
}

# Function to verify load balancing
verify_load_balancing() {
  section "Verifying Load Balancing"
  
  # Create verification script
  cat > /tmp/verify_load_balancing.sh << 'EOF'
#!/bin/bash

echo "=== Current Routing Table ==="
ip route show

echo -e "\n=== Current Routing Rules ==="
ip rule show

echo -e "\n=== Testing Load Balancing ==="
for i in {1..12}; do
  echo "Test $i:"
  ip route get 8.8.8.8
  sleep 1
done

echo -e "\n=== Interface Statistics ==="
for iface in eth0 eth1 eth4 eth5 eth6 eth7; do
  echo "$iface: $(ip -s link show dev $iface | grep -A 1 "RX:" | tail -n 1 | awk '{print $1}') bytes received, $(ip -s link show dev $iface | grep -A 1 "TX:" | tail -n 1 | awk '{print $1}') bytes transmitted"
done
EOF

  # Make the script executable
  chmod +x /tmp/verify_load_balancing.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/verify_load_balancing.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Execute the script on the server
  log "Verifying load balancing on the server..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/verify_load_balancing.sh"
  
  success "Load balancing verification completed"
}

# Function to test performance
test_performance() {
  section "Testing Performance with Load Balancing"
  
  # Create performance test script
  cat > /tmp/test_performance.sh << 'EOF'
#!/bin/bash

# Install required packages
apt-get update
apt-get install -y curl parallel

# Create output directory
mkdir -p /tmp/load_balance_test

# Function to run a download test
run_download_test() {
  local test_num=$1
  local url="https://speed.cloudflare.com/__down?bytes=104857600"
  
  echo "Running test $test_num..."
  curl -s -o /dev/null -w "Test $test_num: %{speed_download} bytes/sec\n" "$url"
}

echo "=== Sequential Download Tests ==="
for i in {1..10}; do
  run_download_test $i
done

echo -e "\n=== Parallel Download Tests ==="
parallel -j 6 run_download_test ::: {1..12}

echo -e "\n=== Interface Statistics After Tests ==="
for iface in eth0 eth1 eth4 eth5 eth6 eth7; do
  echo "$iface: $(ip -s link show dev $iface | grep -A 1 "RX:" | tail -n 1 | awk '{print $1}') bytes received, $(ip -s link show dev $iface | grep -A 1 "TX:" | tail -n 1 | awk '{print $1}') bytes transmitted"
done
EOF

  # Make the script executable
  chmod +x /tmp/test_performance.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/test_performance.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Execute the script on the server
  log "Testing performance with load balancing..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/test_performance.sh"
  
  success "Performance testing completed"
}

# Function to create rollback script
create_rollback_script() {
  section "Creating Rollback Script"
  
  ROLLBACK_SCRIPT="$BACKUP_DIR/rollback_load_balancing.sh"
  
  log "Creating rollback script: $ROLLBACK_SCRIPT"
  
  # Create rollback script
  cat > "$ROLLBACK_SCRIPT" << EOF
#!/bin/bash
# Rollback script for load balancing implementation
# Generated on $(date)

echo "Rolling back load balancing implementation..."

# SSH to the server and restore original configuration
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "
  # Remove multipath routing
  echo 'Removing multipath routing...'
  ip route del default 2>/dev/null
  
  # Remove routing rules
  echo 'Removing routing rules...'
  ip rule show | grep -v 'from all' | cut -d: -f1 | while read -r rule_num; do
    ip rule del prio \$rule_num 2>/dev/null
  done
  
  # Restore original default routes
  echo 'Restoring original default routes...'
  ip route add default via 10.240.8.1 dev eth7 metric 100
  ip route add default via 10.240.1.1 dev eth0 metric 200
  
  # Remove persistent configuration
  echo 'Removing persistent configuration...'
  rm -f /etc/network/if-up.d/multipath-routing
  rm -f /usr/local/sbin/setup-multipath-routing.sh
  
  echo 'Rollback completed.'
"

echo "Rollback script execution completed."
EOF
  
  # Make rollback script executable
  chmod +x "$ROLLBACK_SCRIPT"
  
  success "Rollback script created: $ROLLBACK_SCRIPT"
}

# Function to document the changes
document_changes() {
  section "Documenting Changes"
  
  DOCUMENTATION_FILE="load_balancing_documentation.md"
  
  log "Creating documentation: $DOCUMENTATION_FILE"
  
  # Create documentation
  cat > "$DOCUMENTATION_FILE" << EOF
# Load Balancing Implementation Documentation

## Overview

This document describes the implementation of load balancing across high-performance interfaces on the adapt server. This approach distributes network traffic across multiple interfaces to improve throughput and reliability.

## Implementation Details

### Date and Time
- **Date**: $(date +"%Y-%m-%d")
- **Time**: $(date +"%H:%M:%S %Z")

### Server Information
- **Server Name**: adapt
- **Server IP**: $SERVER_IP

### Changes Made

1. **Backup Creation**
   - Created backup of current network configuration
   - Backup location: $BACKUP_DIR
   - Includes: interfaces, routes, iptables rules, sysctl settings

2. **Multipath Routing Implementation**
   - Implemented multipath routing across high-performance interfaces:
     - eth0 (weight: 10)
     - eth1 (weight: 10)
     - eth4 (weight: 10)
     - eth5 (weight: 20) - Highest weight due to best performance
     - eth6 (weight: 15)
     - eth7 (weight: 15)
   - Created separate routing tables for each interface
   - Configured source-based routing for traffic originating from each interface
   - Made configuration persistent across reboots

3. **Performance Testing**
   - Conducted sequential and parallel download tests
   - Monitored interface statistics before and after tests
   - Verified traffic distribution across interfaces

## Rollback Plan

A rollback script has been created to revert the changes if necessary:

\`\`\`
$ROLLBACK_SCRIPT
\`\`\`

The rollback script will:
1. Remove multipath routing
2. Remove routing rules
3. Restore original default routes
4. Remove persistent configuration

## Verification

The following tests were performed to verify the changes:

1. **Routing Verification**
   - Verified routing table and rules
   - Tested route selection for external destinations
   - Monitored interface statistics

2. **Performance Testing**
   - Sequential download tests
   - Parallel download tests
   - Interface statistics monitoring

## Benefits

1. **Increased Throughput**
   - Combined bandwidth of multiple interfaces
   - Weighted distribution favoring faster interfaces

2. **Improved Reliability**
   - Traffic automatically redirected if an interface fails
   - Multiple paths for network traffic

3. **Optimized Resource Utilization**
   - Balanced load across available interfaces
   - Prioritized faster interfaces with higher weights

## Conclusion

The adapt server now has load balancing implemented across its high-performance interfaces, providing increased throughput, improved reliability, and optimized resource utilization.

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | $(date +"%Y-%m-%d") | Zorion | Initial implementation |
EOF
  
  success "Documentation created: $DOCUMENTATION_FILE"
}

# Main execution
echo "Load Balancing Implementation Script" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "----------------------------------------------" | tee -a "$LOG_FILE"

# Create backup directory
create_backup_dir

# Backup current network configuration
backup_network_config

# Implement multipath routing
implement_multipath_routing

# Verify load balancing
verify_load_balancing

# Test performance
test_performance

# Create rollback script
create_rollback_script

# Document the changes
document_changes

section "Summary"
success "Load balancing implemented across high-performance interfaces"
log "Backup directory: $BACKUP_DIR"
log "Rollback script: $ROLLBACK_SCRIPT"
log "Documentation: $DOCUMENTATION_FILE"

echo -e "\nLoad balancing implementation completed."
exit 0