#!/bin/bash
# Script to fix Chrome Remote Desktop permissions
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

section "Fixing Chrome Remote Desktop Permissions"
log "Connecting to the adapt server..."

# Create a script to fix permissions
cat > /tmp/fix_permissions.sh << 'EOF'
#!/bin/bash

# Add x user to necessary groups
echo "Adding x user to necessary groups..."
usermod -a -G sudo x
usermod -a -G adm x
usermod -a -G systemd-journal x

# Create a polkit rule to allow x user to manage Chrome Remote Desktop service
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

# Make sure the Chrome Remote Desktop service is configured correctly
echo "Configuring Chrome Remote Desktop service..."
systemctl stop chrome-remote-desktop@x.service

# Create a new Chrome Remote Desktop configuration
echo "Creating new Chrome Remote Desktop configuration..."
mkdir -p /home/x/.config/chrome-remote-desktop
cat > /home/x/.config/chrome-remote-desktop/config << 'EOL'
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS=
EOL

# Set correct ownership
echo "Setting correct ownership..."
chown -R x:x /home/x/.config/chrome-remote-desktop

# Restart the service
echo "Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@x.service
systemctl status chrome-remote-desktop@x.service

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

section "Testing Chrome Remote Desktop"
log "Testing Chrome Remote Desktop connectivity..."

# Test Chrome Remote Desktop connectivity
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "su - x -c 'systemctl status chrome-remote-desktop@x.service | grep \"Active:\"'"

section "Summary"
success "Chrome Remote Desktop permissions have been fixed."
log "The x user should now be able to manage the Chrome Remote Desktop service."
log "Try connecting to the Chrome Remote Desktop service now."