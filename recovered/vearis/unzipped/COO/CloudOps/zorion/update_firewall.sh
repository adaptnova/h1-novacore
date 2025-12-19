#!/bin/bash
# Script to update firewall rules for Chrome Remote Desktop
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="firewall_update.log"

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

section "Checking Current Firewall Rules"
log "Checking current iptables rules..."

# Check current iptables rules
CURRENT_RULES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables -L -v && echo -e '\n=== NAT Table ===\n' && iptables -t nat -L -v")
log "$CURRENT_RULES"

section "Updating Firewall Rules"
log "Updating firewall rules for Chrome Remote Desktop..."

# Create firewall update script
cat > /tmp/update_firewall_rules.sh << 'EOF'
#!/bin/bash

# Backup current rules
iptables-save > /tmp/iptables_backup.rules
echo "Backed up current iptables rules to /tmp/iptables_backup.rules"

# Clear all existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
echo "Cleared all existing iptables rules"

# Set default policies
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
echo "Set default policies to ACCEPT"

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
echo "Allowed established and related connections"

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
echo "Allowed loopback traffic"

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
echo "Allowed SSH traffic"

# Allow Chrome Remote Desktop
iptables -A INPUT -p tcp --dport 3389 -j ACCEPT
iptables -A INPUT -p tcp --dport 5050 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
echo "Allowed Chrome Remote Desktop traffic"

# Allow outbound traffic on all interfaces
for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  iptables -A OUTPUT -o $iface -j ACCEPT
  echo "Allowed outbound traffic on $iface"
done

# Set up NAT for all interfaces
for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  iptables -t nat -A POSTROUTING -o $iface -j MASQUERADE
  echo "Set up NAT for $iface"
done

# Allow forwarding between interfaces
for src in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  for dst in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
    if [ "$src" != "$dst" ]; then
      iptables -A FORWARD -i $src -o $dst -j ACCEPT
      echo "Allowed forwarding from $src to $dst"
    fi
  done
done

# Save rules
iptables-save > /etc/iptables/rules.v4
echo "Saved iptables rules to /etc/iptables/rules.v4"

# Make sure iptables-persistent is installed
apt-get update
apt-get install -y iptables-persistent
echo "Installed iptables-persistent"

echo "Firewall rules updated successfully"
EOF

# Copy the script to the server
log "Copying firewall update script to the server..."
scp -o StrictHostKeyChecking=no /tmp/update_firewall_rules.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/update_firewall_rules.sh"

# Run the script
log "Running firewall update script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/update_firewall_rules.sh"

section "Checking Updated Firewall Rules"
log "Checking updated iptables rules..."

# Check updated iptables rules
UPDATED_RULES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables -L -v && echo -e '\n=== NAT Table ===\n' && iptables -t nat -L -v")
log "$UPDATED_RULES"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ping -c 4 www.google.com"

section "Summary"
success "Firewall rules updated"
log "Chrome Remote Desktop should now be able to connect to Google's servers"
log "If you still have issues, try restarting the Chrome Remote Desktop service:"
log "systemctl restart chrome-remote-desktop@crduser"

echo -e "\nFirewall rules updated. Check $LOG_FILE for details."