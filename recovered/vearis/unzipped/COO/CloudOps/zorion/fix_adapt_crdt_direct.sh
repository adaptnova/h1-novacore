#!/bin/bash
# Script to directly fix Chrome Remote Desktop on adapt server
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

section "Fixing Chrome Remote Desktop on Adapt Server"
log "Connecting to the adapt server..."

# SSH into the adapt server and execute commands directly
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
# Step 1: Check and fix network configuration
echo "Step 1: Checking and fixing network configuration..."

# Ensure MTU is set to 1500 on all interfaces
echo "Setting MTU to 1500 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Setting MTU 1500 on $iface..."
  ip link set $iface mtu 1500
done

# Check connectivity to Google's servers
echo "Testing connectivity to Google's servers..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://www.google.com
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://remotedesktop.google.com

# Step 2: Fix Chrome Remote Desktop configuration
echo "Step 2: Fixing Chrome Remote Desktop configuration..."

# Stop any running Chrome Remote Desktop service
echo "Stopping Chrome Remote Desktop service..."
systemctl stop chrome-remote-desktop@x.service

# Remove existing Chrome Remote Desktop configuration
echo "Removing existing Chrome Remote Desktop configuration..."
rm -rf /home/x/.config/chrome-remote-desktop/*

# Create new Chrome Remote Desktop configuration directory
echo "Creating new Chrome Remote Desktop configuration directory..."
mkdir -p /home/x/.config/chrome-remote-desktop
chown -R x:x /home/x/.config/chrome-remote-desktop

# Create a basic config file
echo "Creating basic config file..."
cat > /home/x/.config/chrome-remote-desktop/config << 'EOC'
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS=
EOC
chown x:x /home/x/.config/chrome-remote-desktop/config

# Step 3: Fix user permissions
echo "Step 3: Fixing user permissions..."

# Add x user to necessary groups
echo "Adding x user to necessary groups..."
usermod -a -G sudo x
usermod -a -G adm x
usermod -a -G systemd-journal x

# Create a polkit rule to allow x user to manage the service
echo "Creating polkit rule for Chrome Remote Desktop..."
cat > /etc/polkit-1/localauthority/50-local.d/45-allow-chrome-remote-desktop.pkla << 'EOL'
[Allow x to manage Chrome Remote Desktop]
Identity=unix-user:x
Action=org.freedesktop.systemd1.manage-units
ResultAny=yes
ResultInactive=yes
ResultActive=yes
EOL

# Restart polkit
echo "Restarting polkit..."
systemctl restart polkit

# Step 4: Fix firewall settings
echo "Step 4: Fixing firewall settings..."

# Ensure outbound traffic on port 443 is allowed
echo "Ensuring outbound traffic on port 443 is allowed..."
iptables -F 2>/dev/null || true
iptables -X 2>/dev/null || true
iptables -t nat -F 2>/dev/null || true
iptables -t nat -X 2>/dev/null || true
iptables -t mangle -F 2>/dev/null || true
iptables -t mangle -X 2>/dev/null || true
iptables -P INPUT ACCEPT 2>/dev/null || true
iptables -P FORWARD ACCEPT 2>/dev/null || true
iptables -P OUTPUT ACCEPT 2>/dev/null || true

# Step 5: Restart Chrome Remote Desktop service
echo "Step 5: Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@x.service
systemctl status chrome-remote-desktop@x.service

# Step 6: Run Chrome Remote Desktop setup as x user
echo "Step 6: Running Chrome Remote Desktop setup as x user..."
echo "Note: You will need to enter a PIN when prompted."
su - x -c 'DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="4/0AQSTgQHdYxWzqIpfYNDTTDn2M7yrEOf2a8-Tf1Mg9hF2gnaRlEiF3Kj5A2NkyOIKXLTIXQ" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)'

echo "Chrome Remote Desktop setup complete."
EOF

section "Summary"
success "Chrome Remote Desktop setup has been completed on the adapt server."
log "If you were prompted to enter a PIN, the setup should now be complete."
log "If you encountered any errors, please check the output above for details."