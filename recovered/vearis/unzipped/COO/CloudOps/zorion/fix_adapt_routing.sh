#!/bin/bash
# Script to fix routing on adapt server to match ethos
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 28, 2025

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

SERVER_IP="10.240.1.6"
SSH_USER="root"

section "Fixing Routing Configuration on Adapt Server"
log "Connecting to the adapt server..."

# Create a script to fix routing
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
for ip in $(ip addr show eth0 | grep "inet " | grep -v "10.240.1.6" | awk '{print $2}'); do
  echo "Removing $ip from eth0..."
  ip addr del $ip dev eth0
done

# Make sure each interface has only one IP address
echo "Ensuring each interface has the correct IP address..."
ip addr flush dev eth1
ip addr add 10.240.2.6/24 dev eth1

ip addr flush dev eth2
ip addr add 10.240.3.6/24 dev eth2

ip addr flush dev eth3
ip addr add 10.240.4.6/24 dev eth3

ip addr flush dev eth4
ip addr add 10.240.5.4/24 dev eth4

ip addr flush dev eth5
ip addr add 10.240.6.4/24 dev eth5

ip addr flush dev eth6
ip addr add 10.240.7.4/24 dev eth6

ip addr flush dev eth7
ip addr add 10.240.8.4/24 dev eth7

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

auto eth1
iface eth1 inet dhcp
    mtu 1500

auto eth2
iface eth2 inet dhcp
    mtu 1500

auto eth3
iface eth3 inet dhcp
    mtu 1500

auto eth4
iface eth4 inet dhcp
    mtu 1500

auto eth5
iface eth5 inet dhcp
    mtu 1500

auto eth6
iface eth6 inet dhcp
    mtu 1500

auto eth7
iface eth7 inet dhcp
    mtu 1500
EOI

# Restart networking to apply changes
echo "Restarting networking..."
systemctl restart networking || true

# Display new routing configuration
echo "New routing configuration:"
ip route show

# Display new interface configuration
echo "New interface configuration:"
ip addr show

echo "Routing configuration has been fixed to match ethos server."
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

# Restart Chrome Remote Desktop
section "Restarting Chrome Remote Desktop"
log "Restarting Chrome Remote Desktop service..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl restart chrome-remote-desktop@x.service"
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@x.service"

section "Summary"
success "Routing configuration has been fixed to match ethos server."
log "The adapt server should now have the same routing configuration as ethos."
log "Chrome Remote Desktop should now be able to connect properly."