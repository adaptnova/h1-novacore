#!/bin/bash
# Template Script for Configuring Chrome Remote Desktop on IBM Cloud Servers
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 28, 2025

# Usage: ./configure_crdt_template.sh <server_ip> <username>

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

# Check if server IP and username are provided
if [ $# -lt 2 ]; then
  error "Usage: $0 <server_ip> <username>"
  exit 1
fi

SERVER_IP="$1"
USERNAME="$2"
SSH_USER="root"

section "Configuring Chrome Remote Desktop on $SERVER_IP"
log "Using username: $USERNAME"

# Step 1: Remove iptables rules
section "Step 1: Removing iptables rules"
log "Creating script to remove iptables rules..."

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

success "iptables rules have been removed."

# Step 2: Fix user permissions
section "Step 2: Fixing user permissions"
log "Creating script to fix user permissions..."

cat > /tmp/fix_permissions.sh << EOF
#!/bin/bash

# Add $USERNAME user to necessary groups
echo "Adding $USERNAME user to necessary groups..."
usermod -a -G sudo $USERNAME
usermod -a -G adm $USERNAME
usermod -a -G systemd-journal $USERNAME

# Create a polkit rule to allow $USERNAME user to manage Chrome Remote Desktop service
echo "Creating polkit rule for Chrome Remote Desktop..."
cat > /etc/polkit-1/localauthority/50-local.d/45-allow-chrome-remote-desktop.pkla << EOL
[Allow $USERNAME to manage Chrome Remote Desktop]
Identity=unix-user:$USERNAME
Action=org.freedesktop.systemd1.manage-units
ResultAny=yes
ResultInactive=yes
ResultActive=yes
EOL

# Restart polkit
echo "Restarting polkit..."
systemctl restart polkit

# Make sure the Chrome Remote Desktop service is configured correctly
echo "Configuring Chrome Remote Desktop service..."
systemctl stop chrome-remote-desktop@$USERNAME.service

# Create a new Chrome Remote Desktop configuration
echo "Creating new Chrome Remote Desktop configuration..."
mkdir -p /home/$USERNAME/.config/chrome-remote-desktop
cat > /home/$USERNAME/.config/chrome-remote-desktop/config << EOL
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS=
EOL

# Set correct ownership
echo "Setting correct ownership..."
chown -R $USERNAME:$USERNAME /home/$USERNAME/.config/chrome-remote-desktop

# Restart the service
echo "Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@$USERNAME.service
systemctl status chrome-remote-desktop@$USERNAME.service

echo "Chrome Remote Desktop permissions have been fixed."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/fix_permissions.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/fix_permissions.sh"

# Run the script
log "Running the script to fix permissions..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/fix_permissions.sh"

success "User permissions have been fixed."

# Step 3: Test connectivity
section "Step 3: Testing connectivity"
log "Creating script to test connectivity..."

cat > /tmp/test_connectivity.sh << 'EOF'
#!/bin/bash

# Check if Chrome Remote Desktop service is running
echo "Checking Chrome Remote Desktop service status..."
systemctl status chrome-remote-desktop@$1.service

# Check if the process is running
echo "Checking Chrome Remote Desktop process..."
ps aux | grep chrome-remote-desktop | grep -v grep

# Check outbound connectivity to Google's servers
echo "Testing outbound connectivity to Google's servers..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://www.google.com
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://remotedesktop.google.com

# Check firewall status
echo "Checking firewall status..."
iptables -L OUTPUT -n | grep 443

# Check network interfaces
echo "Checking network interfaces..."
ip addr show | grep -E "eth[0-9]"

# Check listening ports
echo "Checking listening ports..."
netstat -tuln | grep -E "443|5222"

# Check Chrome Remote Desktop logs
echo "Checking Chrome Remote Desktop logs..."
journalctl -u chrome-remote-desktop@$1.service --no-pager -n 20

echo "Connectivity test completed."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/test_connectivity.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/test_connectivity.sh"

# Run the script
log "Running the connectivity test..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/test_connectivity.sh $USERNAME"

success "Connectivity test completed."

section "Summary"
success "Chrome Remote Desktop has been configured on $SERVER_IP for user $USERNAME."
log "The service should now be running and accessible from the Chrome Remote Desktop client."
log "If you encounter any issues, check the IBM firewall settings and make sure ports 443 and 5222 are open for outbound traffic."