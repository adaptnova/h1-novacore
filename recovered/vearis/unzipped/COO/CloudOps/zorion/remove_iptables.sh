#!/bin/bash
# Script to remove iptables rules and disable iptables from loading at boot
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

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

section "Removing iptables rules"
log "Connecting to the adapt server..."

# Create a script to remove iptables rules
cat > /tmp/remove_iptables.sh << 'EOF'
#!/bin/bash

# Backup current iptables rules
BACKUP_DIR="/tmp/firewall_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
iptables-save > $BACKUP_DIR/iptables_backup.rules
echo "Backed up current iptables rules to $BACKUP_DIR/iptables_backup.rules"

# Flush all iptables rules
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

# Disable iptables from loading at boot
if [ -f /etc/network/if-pre-up.d/iptables ]; then
  echo "Disabling iptables from loading at boot..."
  mv /etc/network/if-pre-up.d/iptables /etc/network/if-pre-up.d/iptables.disabled
fi

# Remove iptables rules file
if [ -f /etc/iptables/rules.v4 ]; then
  echo "Removing iptables rules file..."
  mv /etc/iptables/rules.v4 /etc/iptables/rules.v4.backup
fi

echo "iptables rules have been removed and disabled from loading at boot."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/remove_iptables.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/remove_iptables.sh"

# Run the script
log "Running the script to remove iptables rules..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/remove_iptables.sh"

section "Testing Chrome Remote Desktop"
log "Testing Chrome Remote Desktop connectivity..."

# Test Chrome Remote Desktop connectivity
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@x.service | grep 'Active:'"

section "Summary"
success "iptables rules have been removed and disabled from loading at boot."
log "The system is now using only the IBM firewall settings."
log "Chrome Remote Desktop should now be able to connect properly."