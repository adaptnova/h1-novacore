#!/bin/bash

# IBM Cloud Server Network Configuration Template
# This script orchestrates the process of configuring network interfaces and routing for IBM Cloud servers
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration - Edit these variables for each server
SERVER_NAME="adapt"
INSTANCE_ID="0717_ee285094-0683-4f21-a573-ae87022853e9"
SSH_USER="root"
PRIMARY_IP="10.240.1.6"
SECURITY_GROUP="trekker-refill-quit-refueling"

# Network configuration - Edit as needed for different network layouts
# Format: "subnet_cidr:gateway:interface_name:priority"
NETWORKS=(
  "10.240.1.0/24:10.240.1.1:eth0:10"  # Primary network (management)
  "10.240.2.0/24:10.240.2.1:eth1:20"  # Secondary network
  "10.240.3.0/24:10.240.3.1:eth2:30"  # Tertiary network
  "10.240.4.0/24:10.240.4.1:eth3:40"  # Additional network
  "10.240.5.0/24:10.240.5.1:eth4:50"  # Additional network
  "10.240.6.0/24:10.240.6.1:eth5:60"  # Additional network
  "10.240.7.0/24:10.240.7.1:eth6:70"  # Additional network
  "10.240.8.0/24:10.240.8.1:eth7:80"  # Public network (with gateway)
)

# Subnets to add (we already have nic1-subnet)
SUBNETS=(
  "nic2-subnet"
  "nic3-subnet"
  "nic4-subnet"
  "nic5-subnet"
  "nic6-subnet"
  "nic7-subnet"
  "nic8-subnet"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display section headers
section() {
  echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  echo -e "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  echo -e "${YELLOW}! $1${NC}"
}

# Function to display info messages
info() {
  echo -e "  $1"
}

# Function to check IBM Cloud CLI installation
check_ibmcloud_cli() {
  section "Checking IBM Cloud CLI"
  
  if command -v ibmcloud >/dev/null 2>&1; then
    success "IBM Cloud CLI is installed"
    
    # Check if user is logged in
    ibmcloud account show >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      success "Already logged in to IBM Cloud"
    else
      warning "Not logged in to IBM Cloud"
      info "Please login using: ibmcloud login"
      exit 1
    fi
  else
    error "IBM Cloud CLI is not installed"
    info "Please install IBM Cloud CLI: https://cloud.ibm.com/docs/cli"
    exit 1
  fi
}

# Function to check instance status
check_instance_status() {
  section "Checking Instance Status"
  
  info "Retrieving status for instance $SERVER_NAME ($INSTANCE_ID)"
  
  # Get instance details
  INSTANCE_JSON=$(ibmcloud is instance $INSTANCE_ID --output JSON)
  
  # Check if instance exists
  if [ $? -ne 0 ]; then
    error "Failed to retrieve instance details"
    exit 1
  fi
  
  # Extract status and lifecycle state
  STATUS=$(echo $INSTANCE_JSON | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
  LIFECYCLE=$(echo $INSTANCE_JSON | grep -o '"lifecycle_state": "[^"]*"' | cut -d'"' -f4)
  
  info "Instance status: $STATUS"
  info "Lifecycle state: $LIFECYCLE"
  
  # Check if instance is running
  if [ "$STATUS" != "running" ]; then
    warning "Instance is not running (status: $STATUS)"
    info "Starting instance..."
    ibmcloud is instance-start $INSTANCE_ID
    
    # Wait for instance to start
    while true; do
      sleep 10
      STATUS=$(ibmcloud is instance $INSTANCE_ID --output JSON | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
      info "Current status: $STATUS"
      if [ "$STATUS" == "running" ]; then
        success "Instance is now running"
        break
      fi
    done
  else
    success "Instance is running"
  fi
  
  # Check if instance is updating
  if [ "$LIFECYCLE" == "updating" ]; then
    warning "Instance is currently updating (lifecycle: $LIFECYCLE)"
    info "Waiting for update to complete..."
    
    # Wait for update to complete
    while true; do
      sleep 30
      LIFECYCLE=$(ibmcloud is instance $INSTANCE_ID --output JSON | grep -o '"lifecycle_state": "[^"]*"' | cut -d'"' -f4)
      info "Current lifecycle: $LIFECYCLE"
      if [ "$LIFECYCLE" != "updating" ]; then
        success "Instance update completed"
        break
      fi
    done
  else
    success "Instance is not updating"
  fi
}

# Function to check current network interfaces
check_network_interfaces() {
  section "Checking Current Network Interfaces"
  
  info "Retrieving network interfaces for instance $SERVER_NAME ($INSTANCE_ID)"
  
  # Get network interfaces
  INTERFACES=$(ibmcloud is instance-network-interfaces $INSTANCE_ID)
  
  # Count interfaces
  INTERFACE_COUNT=$(echo "$INTERFACES" | grep -c "available")
  
  info "Current interface count: $INTERFACE_COUNT"
  
  if [ $INTERFACE_COUNT -eq 8 ]; then
    success "Instance already has 8 network interfaces"
    NEED_TO_ADD_NICS=false
  else
    warning "Instance has $INTERFACE_COUNT network interfaces, needs 8"
    NEED_TO_ADD_NICS=true
    NICS_TO_ADD=$((8 - INTERFACE_COUNT))
    info "Need to add $NICS_TO_ADD network interfaces"
  fi
}

# Function to add network interfaces
add_network_interfaces() {
  section "Adding Network Interfaces"
  
  if [ "$NEED_TO_ADD_NICS" = false ]; then
    info "No need to add network interfaces"
    return 0
  fi
  
  info "Adding $NICS_TO_ADD network interfaces to instance $SERVER_NAME ($INSTANCE_ID)"
  
  # Add each network interface
  for i in $(seq 0 $((NICS_TO_ADD - 1))); do
    SUBNET_INDEX=$i
    SUBNET=${SUBNETS[$SUBNET_INDEX]}
    NIC_NAME="nic-${SUBNET:0:3}-interface"
    
    info "Adding interface $NIC_NAME with subnet $SUBNET..."
    ibmcloud is instance-network-interface-create $NIC_NAME $INSTANCE_ID $SUBNET --allow-ip-spoofing true
    
    if [ $? -eq 0 ]; then
      success "Added network interface $NIC_NAME"
    else
      error "Failed to add network interface $NIC_NAME"
      exit 1
    fi
    
    # Wait a bit between additions to avoid rate limiting
    sleep 5
  done
  
  success "Added all required network interfaces"
}

# Function to check SSH connectivity
check_ssh_connectivity() {
  section "Checking SSH Connectivity"
  
  info "Checking SSH connectivity to $PRIMARY_IP..."
  
  # Remove from known_hosts if exists
  ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$PRIMARY_IP" >/dev/null 2>&1
  
  # Try to connect
  ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_USER@$PRIMARY_IP exit 2>/dev/null
  
  if [ $? -eq 0 ]; then
    success "SSH connection successful"
    SSH_AVAILABLE=true
  else
    warning "SSH connection failed"
    SSH_AVAILABLE=false
  fi
}

# Function to configure network on the server
configure_network() {
  section "Configuring Network"
  
  if [ "$SSH_AVAILABLE" = false ]; then
    warning "Cannot configure network due to SSH connectivity issues"
    info "Please ensure the instance is accessible via SSH before running this part"
    return 1
  fi
  
  info "Configuring network on instance $SERVER_NAME ($PRIMARY_IP)"
  
  # Run the configure_routing.sh script
  bash configure_routing.sh
  
  if [ $? -eq 0 ]; then
    success "Network configuration completed"
  else
    error "Network configuration failed"
    exit 1
  fi
}

# Function to verify configuration
verify_configuration() {
  section "Verifying Configuration"
  
  if [ "$SSH_AVAILABLE" = false ]; then
    warning "Cannot verify configuration due to SSH connectivity issues"
    return 1
  fi
  
  info "Verifying network configuration on instance $SERVER_NAME ($PRIMARY_IP)"
  
  # Create a temporary verification script
  cat > /tmp/verify_network.sh << 'EOF'
#!/bin/bash

# Check network interfaces
echo "Network Interfaces:"
ip -br addr show

# Check routing tables
echo -e "\nRouting Tables:"
ip rule list

# Check network performance
echo -e "\nNetwork Performance:"
for i in {0..7}; do
  if [ -e /sys/class/net/eth$i ]; then
    echo "eth$i MTU: $(cat /sys/class/net/eth$i/mtu)"
    ethtool eth$i | grep -E "Speed|Duplex|Link"
  fi
done

# Check sysctl network parameters
echo -e "\nNetwork Parameters:"
sysctl -a | grep -E "net.ipv4.tcp_rmem|net.ipv4.tcp_wmem|net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_congestion_control"

exit 0
EOF

  # Make the script executable
  chmod +x /tmp/verify_network.sh
  
  # Copy and execute the script on the remote server
  scp -o StrictHostKeyChecking=no /tmp/verify_network.sh $SSH_USER@$PRIMARY_IP:/tmp/
  ssh -o StrictHostKeyChecking=no $SSH_USER@$PRIMARY_IP "bash /tmp/verify_network.sh"
  
  # Clean up
  rm /tmp/verify_network.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$PRIMARY_IP "rm /tmp/verify_network.sh"
  
  success "Verification completed"
}

# Main execution
echo "IBM Cloud Server Network Configuration Template"
echo "Server: $SERVER_NAME ($INSTANCE_ID)"
echo "Date: $(date)"
echo "----------------------------------------------"

# Check prerequisites
check_ibmcloud_cli

# Check instance status
check_instance_status

# Check current network interfaces
check_network_interfaces

# Add network interfaces if needed
add_network_interfaces

# Check SSH connectivity
check_ssh_connectivity

# Configure network if SSH is available
configure_network

# Verify configuration if SSH is available
verify_configuration

section "Summary"
echo "Server: $SERVER_NAME ($INSTANCE_ID)"
echo "Primary IP: $PRIMARY_IP"
echo "Network interfaces: $([ "$NEED_TO_ADD_NICS" = false ] && echo "Already had 8" || echo "Added $NICS_TO_ADD to reach 8")"
echo "SSH connectivity: $([ "$SSH_AVAILABLE" = true ] && echo "Available" || echo "Not available")"
echo "Network configuration: $([ "$SSH_AVAILABLE" = true ] && echo "Completed" || echo "Not performed (SSH unavailable)")"
echo "Verification: $([ "$SSH_AVAILABLE" = true ] && echo "Completed" || echo "Not performed (SSH unavailable)")"

echo -e "\nConfiguration template completed."
echo "This template can be reused for other servers by modifying the configuration variables at the top of the script."

exit 0