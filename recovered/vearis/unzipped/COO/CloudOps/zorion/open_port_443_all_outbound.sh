#!/bin/bash
# Script to open port 443 for ALL outbound traffic
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="open_port_443.log"

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

section "Checking Server Connectivity"
log "Checking connectivity to the adapt server..."

# Check connectivity to the server
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'Connection successful'" || {
  error "Failed to connect to the server"
  exit 1
}

success "Connected to the server"

section "Opening Port 443 for ALL Outbound Traffic"
log "Creating firewall update script..."

# Create firewall update script
cat > /tmp/open_port_443.sh << 'EOF'
#!/bin/bash

# Backup current iptables rules
BACKUP_DIR="/tmp/firewall_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
iptables-save > $BACKUP_DIR/iptables_backup.rules
echo "Backed up current iptables rules to $BACKUP_DIR/iptables_backup.rules"

# Allow ALL outbound connections on port 443 (HTTPS) for all interfaces
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Allowing ALL outbound TCP traffic on port 443 for interface $iface"
  iptables -A OUTPUT -o $iface -p tcp --dport 443 -j ACCEPT
  
  echo "Allowing ALL outbound UDP traffic on port 443 for interface $iface"
  iptables -A OUTPUT -o $iface -p udp --dport 443 -j ACCEPT
done

# Allow ALL outbound connections on port 5222 (XMPP) for all interfaces
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Allowing ALL outbound TCP traffic on port 5222 for interface $iface"
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
scp -o StrictHostKeyChecking=no /tmp/open_port_443.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/open_port_443.sh"

# Run the script
log "Running firewall update script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/open_port_443.sh"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
GOOGLE_TEST=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w '%{http_code}' https://www.google.com || echo 'Failed to connect to Google'")

if [ "$GOOGLE_TEST" == "200" ]; then
  success "Successfully connected to Google's servers (HTTP 200)"
else
  warning "Failed to connect to Google's servers: $GOOGLE_TEST"
  log "This may indicate that there are still connectivity issues."
fi

section "Summary"
success "Port 443 is now open for ALL outbound connections"
log "The following ports are now open for ALL outbound connections:"
log "- TCP/UDP 443 (HTTPS) - Primary communication channel"
log "- TCP 5222 (XMPP) - Optional for signaling"
log "These rules have been saved and will persist across reboots."

echo -e "\nPort 443 is now open for ALL outbound connections. Check $LOG_FILE for details."