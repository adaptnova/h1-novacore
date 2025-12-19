#!/bin/bash
# Template Script for Fixing Server Configuration to Match Ethos
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 28, 2025

# Usage: ./fix_server_template.sh <server_ip> [username]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
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

# Check if server IP is provided
if [ $# -lt 1 ]; then
  error "Usage: $0 <server_ip> [username]"
  exit 1
fi

SERVER_IP="$1"
SSH_USER="${2:-root}"

section "FIXING SERVER CONFIGURATION ON $SERVER_IP"
log "Using SSH user: $SSH_USER"

# Step 1: Uninstall iptables
section "Step 1: Uninstalling iptables"
log "Creating script to uninstall iptables..."

cat > /tmp/uninstall_iptables.sh << 'EOF'
#!/bin/bash

# Flush all iptables rules first
echo "Flushing all iptables rules..."
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Disable iptables services
echo "Disabling iptables services..."
systemctl stop iptables 2>/dev/null || true
systemctl disable iptables 2>/dev/null || true
systemctl mask iptables 2>/dev/null || true

# Remove iptables boot scripts
echo "Removing iptables boot scripts..."
if [ -f /etc/network/if-pre-up.d/iptables ]; then
  rm -f /etc/network/if-pre-up.d/iptables
  echo "Removed /etc/network/if-pre-up.d/iptables"
fi

if [ -f /etc/network/if-pre-up.d/iptables.disabled ]; then
  rm -f /etc/network/if-pre-up.d/iptables.disabled
  echo "Removed /etc/network/if-pre-up.d/iptables.disabled"
fi

# Remove iptables rules files
echo "Removing iptables rules files..."
if [ -d /etc/iptables ]; then
  rm -rf /etc/iptables
  echo "Removed /etc/iptables directory"
fi

# Uninstall iptables packages
echo "Uninstalling iptables packages..."
apt-get -y purge iptables iptables-persistent || true
apt-get -y autoremove || true
yum -y remove iptables iptables-services || true

# Remove any remaining iptables files
echo "Removing any remaining iptables files..."
find /etc -name "*iptables*" -exec rm -rf {} \; 2>/dev/null || true
find /usr/lib -name "*iptables*" -exec rm -rf {} \; 2>/dev/null || true

echo "IPTABLES HAS BEEN COMPLETELY UNINSTALLED AND REMOVED FROM THE SYSTEM."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/uninstall_iptables.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/uninstall_iptables.sh"

# Run the script
log "Running the script to uninstall iptables..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/uninstall_iptables.sh"

success "iptables has been uninstalled."

# Step 2: Fix routing and network configuration
section "Step 2: Fixing routing and network configuration"
log "Creating script to fix routing and network configuration..."

cat > /tmp/fix_routing.sh << 'EOF'
#!/bin/bash

# Backup current routing configuration
echo "Backing up current routing configuration..."
ip route show > /tmp/routes_backup_$(date +%Y%m%d%H%M%S).txt

# Remove all existing default routes
echo "Removing all existing default routes..."
ip route del default 2>/dev/null || true

# Add a simple default route via 10.240.1.1 (like ethos)
echo "Adding simple default route via 10.240.1.1..."
ip route add default via 10.240.1.1 dev eth0

# Fix MTU on all interfaces to match ethos (1500)
echo "Setting MTU to 1500 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Setting MTU 1500 on $iface..."
  ip link set $iface mtu 1500
done

# Remove IP aliases from eth0
echo "Removing IP aliases from eth0..."
for ip in $(ip addr show eth0 | grep "inet " | grep -v "10.240.1" | awk '{print $2}'); do
  echo "Removing $ip from eth0..."
  ip addr del $ip dev eth0
done

# Get list of interfaces
INTERFACES=$(ip -o link show | grep -v lo | awk -F': ' '{print $2}')

# Make sure each interface has only one IP address
echo "Ensuring each interface has the correct IP address..."
for iface in $INTERFACES; do
  if [ "$iface" != "eth0" ]; then
    # Get the current IP for this interface
    CURRENT_IP=$(ip addr show $iface | grep "inet " | awk '{print $2}' | head -1)
    if [ -n "$CURRENT_IP" ]; then
      # Flush the interface and add back the IP
      echo "Flushing $iface and adding back $CURRENT_IP..."
      ip addr flush dev $iface
      ip addr add $CURRENT_IP dev $iface
    fi
  fi
done

# Make the changes persistent
echo "Making changes persistent..."
cat > /etc/network/interfaces.d/50-cloud-init.cfg << 'EOI'
# This file is generated from information provided by the datasource.
# Changes to it will not persist across an instance reboot.
# To disable cloud-init's network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {config: disabled}

auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
    mtu 1500
EOI

# Add other interfaces to the config
for iface in $INTERFACES; do
  if [ "$iface" != "eth0" ] && [ "$iface" != "lo" ]; then
    echo "
auto $iface
iface $iface inet dhcp
    mtu 1500" >> /etc/network/interfaces.d/50-cloud-init.cfg
  fi
done

echo "Routing and network configuration has been fixed to match ethos server."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/fix_routing.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/fix_routing.sh"

# Run the script
log "Running the script to fix routing..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/fix_routing.sh"

success "Routing and network configuration has been fixed."

# Step 3: Restart Chrome Remote Desktop (if installed)
section "Step 3: Restarting Chrome Remote Desktop"
log "Checking if Chrome Remote Desktop is installed..."

if ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl list-unit-files | grep chrome-remote-desktop"; then
  log "Chrome Remote Desktop is installed. Restarting the service..."
  
  # Find the username for Chrome Remote Desktop
  CRDT_USER=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl list-units | grep chrome-remote-desktop@ | awk -F'@' '{print \$2}' | awk -F'.' '{print \$1}'")
  
  if [ -n "$CRDT_USER" ]; then
    log "Restarting Chrome Remote Desktop for user $CRDT_USER..."
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl restart chrome-remote-desktop@$CRDT_USER.service"
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@$CRDT_USER.service"
    success "Chrome Remote Desktop has been restarted."
  else
    warning "Could not determine Chrome Remote Desktop user. Please restart the service manually."
  fi
else
  log "Chrome Remote Desktop is not installed on this server."
fi

# Step 4: Test connectivity
section "Step 4: Testing connectivity"
log "Testing connectivity to Google's servers..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://www.google.com"
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://remotedesktop.google.com"

section "Summary"
success "SERVER CONFIGURATION HAS BEEN FIXED ON $SERVER_IP."
log "The server should now have the same configuration as ethos."
log "If Chrome Remote Desktop is installed, it should now be able to connect properly."