#!/bin/bash
# IBM Cloud Server Network Configuration Template
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration - Edit these variables for each server
SERVER_NAME="server-name"
SERVER_IP="server-ip"
SSH_USER="root"
BASE_SUBNET="10.240"  # Base subnet (e.g., 10.240 for 10.240.x.0/24)
IP_LAST_OCTET="6"     # Last octet of IP (e.g., 6 for 10.240.x.6)
SUBNET_COUNT=8        # Number of subnets to configure

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

# Function to check SSH connectivity
check_ssh() {
  section "Checking SSH Connectivity"
  
  info "Attempting to connect to $SERVER_NAME ($SERVER_IP)..."
  ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP exit 2>/dev/null
  
  if [ $? -eq 0 ]; then
    success "SSH connection successful"
    return 0
  else
    error "SSH connection failed"
    return 1
  fi
}

# Function to configure virtual interfaces
configure_interfaces() {
  section "Configuring Virtual Interfaces"
  
  info "Creating $((SUBNET_COUNT-1)) virtual interfaces..."
  
  # Create command to add virtual interfaces
  CMD="for i in {1..$((SUBNET_COUNT-1))}; do"
  CMD+=" ip addr add $BASE_SUBNET.\$((i+1)).$IP_LAST_OCTET/24 dev eth0 label eth0:\$i;"
  CMD+=" done && ip -br addr show"
  
  # Execute command
  RESULT=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$CMD")
  
  if [ $? -eq 0 ]; then
    success "Virtual interfaces created successfully"
    info "Current interfaces:"
    echo "$RESULT"
    return 0
  else
    error "Failed to create virtual interfaces"
    return 1
  fi
}

# Function to optimize network settings
optimize_network() {
  section "Optimizing Network Settings"
  
  info "Applying network optimizations..."
  
  # Create optimization script
  cat > /tmp/optimize.sh << 'EOT'
#!/bin/bash
echo 'Backing up sysctl.conf...'
cp /etc/sysctl.conf /etc/sysctl.conf.bak

echo 'Configuring network optimizations...'
cat >> /etc/sysctl.conf << 'EOF'

# Network Optimization Settings
# Increase TCP buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Enable TCP window scaling and timestamps
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1

# Increase option memory buffers
net.core.optmem_max = 65536

# Increase network backlog
net.core.netdev_max_backlog = 5000

# Enable TCP Fast Open
net.ipv4.tcp_fastopen = 3

# Enable MTU probing
net.ipv4.tcp_mtu_probing = 1

# Enable BBR congestion control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Increase max connections
net.core.somaxconn = 65535
EOF

echo 'Applying settings...'
sysctl -p

echo 'Optimizing eth0...'
ethtool -K eth0 tso on gso on gro on lro on tx on rx on 2>/dev/null || true
ethtool -G eth0 rx 4096 tx 4096 2>/dev/null || true

echo 'Making virtual interfaces persistent...'
BASE_SUBNET="$1"
IP_LAST_OCTET="$2"
SUBNET_COUNT="$3"

# Determine the correct location for persistence script
if [ -d /etc/network/if-up.d ]; then
  # Debian/Ubuntu
  PERSIST_FILE="/etc/network/if-up.d/virtual-interfaces"
elif [ -d /etc/sysconfig/network-scripts ]; then
  # RHEL/CentOS
  PERSIST_FILE="/etc/sysconfig/network-scripts/ifup-local"
  touch $PERSIST_FILE
  chmod +x $PERSIST_FILE
else
  # Fallback
  PERSIST_FILE="/etc/rc.local"
  # Create rc.local if it doesn't exist
  if [ ! -f $PERSIST_FILE ]; then
    echo '#!/bin/bash' > $PERSIST_FILE
    echo 'exit 0' >> $PERSIST_FILE
    chmod +x $PERSIST_FILE
  fi
  # Remove exit 0 if it exists
  sed -i '/exit 0/d' $PERSIST_FILE
  # Add exit 0 at the end later
fi

# Create persistence script
cat > $PERSIST_FILE << EOF
#!/bin/bash
# Add virtual interfaces on eth0
for i in {1..$((SUBNET_COUNT-1))}; do
  ip addr add $BASE_SUBNET.\$((i+1)).$IP_LAST_OCTET/24 dev eth0 label eth0:\$i
done
EOF

# Add exit 0 for rc.local
if [ "$PERSIST_FILE" = "/etc/rc.local" ]; then
  echo 'exit 0' >> $PERSIST_FILE
fi

chmod +x $PERSIST_FILE

echo 'Optimization complete!'
EOT

  # Make the script executable
  chmod +x /tmp/optimize.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/optimize.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Execute the script
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/optimize.sh $BASE_SUBNET $IP_LAST_OCTET $SUBNET_COUNT"
  
  if [ $? -eq 0 ]; then
    success "Network optimization completed"
    return 0
  else
    error "Network optimization failed"
    return 1
  fi
  
  # Clean up
  rm /tmp/optimize.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "rm /tmp/optimize.sh"
}

# Function to run speed tests
run_speed_tests() {
  section "Running Speed Tests"
  
  info "Testing download speeds on all interfaces..."
  
  # Create speed test script
  cat > /tmp/speed_test.sh << 'EOT'
#!/bin/bash
# Install required packages
apt-get update
apt-get install -y curl speedtest-cli

# Create results directory
mkdir -p /tmp/speed_tests

# Initialize results file
echo 'Interface,Source,Speed (MB/s)' > /tmp/speed_tests/results.csv

# Run tests on each interface
SUBNET_COUNT=$1
for i in $(seq 0 $((SUBNET_COUNT-1))); do
  if [ $i -eq 0 ]; then
    IFACE='eth0'
  else
    IFACE="eth0:$i"
  fi
  
  IP=$(ip -4 addr show $IFACE 2>/dev/null | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
  
  if [ -n "$IP" ]; then
    echo "Testing $IFACE ($IP)..."
    
    # Test with Cloudflare
    curl --interface $IP -o /dev/null https://speed.cloudflare.com/__down?bytes=104857600 \
      -w "\n$IFACE,Cloudflare,%{speed_download}\n" 2>/dev/null | tee -a /tmp/speed_tests/results.csv
  fi
done

# Run speedtest-cli
echo 'Running speedtest-cli...'
speedtest-cli --simple | grep Download

# Display results
echo -e "\nSpeed Test Results:"
cat /tmp/speed_tests/results.csv
EOT

  # Make the script executable
  chmod +x /tmp/speed_test.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/speed_test.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Execute the script
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/speed_test.sh $SUBNET_COUNT"
  
  if [ $? -eq 0 ]; then
    success "Speed tests completed"
    return 0
  else
    error "Speed tests failed"
    return 1
  fi
  
  # Clean up
  rm /tmp/speed_test.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "rm /tmp/speed_test.sh"
}

# Function to verify configuration
verify_configuration() {
  section "Verifying Configuration"
  
  info "Checking network configuration..."
  
  # Check interfaces
  INTERFACES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -br addr show")
  
  # Count interfaces
  INTERFACE_COUNT=$(echo "$INTERFACES" | grep -c "eth0")
  
  if [ $INTERFACE_COUNT -eq $SUBNET_COUNT ]; then
    success "All $SUBNET_COUNT interfaces are configured"
  else
    warning "Expected $SUBNET_COUNT interfaces, found $INTERFACE_COUNT"
  fi
  
  # Check network parameters
  PARAMS=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "sysctl -a | grep -E 'net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_congestion_control'")
  
  echo "$PARAMS" | while read line; do
    info "$line"
  done
  
  # Check persistence
  PERSIST=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "if [ -f /etc/network/if-up.d/virtual-interfaces ]; then echo 'Persistence: Debian/Ubuntu method'; elif [ -f /etc/sysconfig/network-scripts/ifup-local ]; then echo 'Persistence: RHEL/CentOS method'; elif grep -q 'virtual-interfaces' /etc/rc.local; then echo 'Persistence: rc.local method'; else echo 'Persistence: Not configured'; fi")
  
  info "$PERSIST"
  
  success "Verification completed"
}

# Main execution
echo "IBM Cloud Server Network Configuration Template"
echo "Server: $SERVER_NAME ($SERVER_IP)"
echo "Date: $(date)"
echo "----------------------------------------------"

# Check SSH connectivity
if check_ssh; then
  # Configure virtual interfaces
  configure_interfaces
  
  # Optimize network settings
  optimize_network
  
  # Run speed tests
  run_speed_tests
  
  # Verify configuration
  verify_configuration
  
  section "Summary"
  success "Configuration completed for $SERVER_NAME"
  info "Server IP: $SERVER_IP"
  info "Configured $SUBNET_COUNT network interfaces"
  info "Applied network optimizations"
  info "Tested download speeds"
  info "Made configuration persistent"
else
  error "Cannot proceed without SSH connectivity"
  exit 1
fi

echo -e "\nConfiguration template completed."
exit 0