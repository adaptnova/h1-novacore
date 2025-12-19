632#!/bin/bash
# Template Script to set up firewall rules for Chrome Remote Desktop on IBM Cloud servers
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025
#
# Usage: ./crdt_firewall_template.sh <server_ip> [ssh_user]
# Example: ./crdt_firewall_template.sh 10.240.1.6 root

# Default values
SSH_USER="root"
LOG_FILE="crdt_firewall_setup_$(date +%Y%m%d%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
  echo "Usage: $0 <server_ip> [ssh_user]"
  echo "  server_ip: IP address of the server to configure"
  echo "  ssh_user: SSH user to connect to the server (default: root)"
  exit 1
}

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

# Check if server IP is provided
if [ $# -lt 1 ]; then
  usage
fi

SERVER_IP="$1"

# Check if SSH user is provided
if [ $# -ge 2 ]; then
  SSH_USER="$2"
fi

# Initialize log file
> "$LOG_FILE"

section "Configuration"
log "Server IP: $SERVER_IP"
log "SSH User: $SSH_USER"

section "Checking Server Connectivity"
log "Checking connectivity to the server..."

# Check connectivity to the server
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'Connection successful'" || {
  error "Failed to connect to the server"
  exit 1
}

success "Connected to the server"

section "Updating Firewall Rules"
log "Creating firewall update script for Chrome Remote Desktop..."

# Create firewall update script
cat > /tmp/update_firewall_crdt.sh << 'EOF'
#!/bin/bash

# Backup current iptables rules
BACKUP_DIR="/tmp/firewall_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
iptables-save > $BACKUP_DIR/iptables_backup.rules
echo "Backed up current iptables rules to $BACKUP_DIR/iptables_backup.rules"

# Allow outbound connections on port 443 (HTTPS) for all interfaces
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Allowing outbound TCP traffic on port 443 for interface $iface"
  iptables -A OUTPUT -o $iface -p tcp --dport 443 -j ACCEPT
  
  echo "Allowing outbound UDP traffic on port 443 for interface $iface"
  iptables -A OUTPUT -o $iface -p udp --dport 443 -j ACCEPT
done

# Allow outbound connections on port 5222 (XMPP) for all interfaces
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Allowing outbound TCP traffic on port 5222 for interface $iface"
  iptables -A OUTPUT -o $iface -p tcp --dport 5222 -j ACCEPT
done

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
echo "Allowed established and related connections"

# Save iptables rules
if [ -d "/etc/iptables" ]; then
  iptables-save > /etc/iptables/rules.v4
  echo "Saved iptables rules to /etc/iptables/rules.v4"
else
  mkdir -p /etc/iptables
  iptables-save > /etc/iptables/rules.v4
  echo "Created /etc/iptables directory and saved rules to /etc/iptables/rules.v4"
fi

# Create a script to load these rules at boot
cat > /etc/network/if-pre-up.d/iptables << 'EOI'
#!/bin/sh
/sbin/iptables-restore < /etc/iptables/rules.v4
EOI

chmod +x /etc/network/if-pre-up.d/iptables
echo "Created boot-time script to load iptables rules"

# Display updated iptables rules
echo "Updated iptables rules:"
iptables -L -v
EOF

# Copy the script to the server
log "Copying firewall update script to the server..."
scp -o StrictHostKeyChecking=no /tmp/update_firewall_crdt.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/update_firewall_crdt.sh"

# Run the script
log "Running firewall update script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/update_firewall_crdt.sh"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
GOOGLE_TEST=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w '%{http_code}' https://www.google.com || echo 'Failed to connect to Google'")

if [ "$GOOGLE_TEST" == "200" ]; then
  success "Successfully connected to Google's servers (HTTP 200)"
else
  warning "Failed to connect to Google's servers: $GOOGLE_TEST"
  log "This may indicate that there are still connectivity issues."
  log "Check the server's network configuration and DNS settings."
fi

section "Summary"
success "Firewall rules for Chrome Remote Desktop have been set up"
log "The following ports are now open for outbound connections:"
log "- TCP/UDP 443 (HTTPS) - Primary communication channel"
log "- TCP 5222 (XMPP) - Optional for signaling"
log "These rules have been saved and will persist across reboots."

echo -e "\nFirewall rules for Chrome Remote Desktop have been set up on $SERVER_IP. Check $LOG_FILE for details."