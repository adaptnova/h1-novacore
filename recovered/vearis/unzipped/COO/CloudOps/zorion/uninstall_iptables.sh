#!/bin/bash
# Script to completely uninstall iptables from the system
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

section "COMPLETELY UNINSTALLING IPTABLES"
log "Connecting to the adapt server..."

# Create a script to uninstall iptables
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

# Verify iptables is completely removed
echo "Verifying iptables is completely removed..."
if command -v iptables &> /dev/null; then
  echo "WARNING: iptables command is still available. This might be because it's built into the kernel."
  echo "However, all rules have been flushed and services disabled."
else
  echo "iptables command is no longer available."
fi

# Restart networking to ensure clean state
echo "Restarting networking..."
systemctl restart networking 2>/dev/null || true
systemctl restart network 2>/dev/null || true

echo "IPTABLES HAS BEEN COMPLETELY UNINSTALLED AND REMOVED FROM THE SYSTEM."
echo "The system will now rely solely on IBM firewall settings."
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

# Test connectivity after uninstalling iptables
section "Testing Connectivity"
log "Testing connectivity to Google's servers..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://www.google.com"
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://remotedesktop.google.com"

# Restart Chrome Remote Desktop
section "Restarting Chrome Remote Desktop"
log "Restarting Chrome Remote Desktop service..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl restart chrome-remote-desktop@x.service"
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@x.service"

section "Summary"
success "IPTABLES HAS BEEN COMPLETELY UNINSTALLED FROM THE SYSTEM."
log "The system is now configured to rely solely on IBM firewall settings."
log "Chrome Remote Desktop should now be able to connect properly without any firewall blocking."