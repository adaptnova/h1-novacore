#!/bin/bash
# Script to set up Chrome Remote Desktop with a new authorization code
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
PIN="632000"

section "Setting up Chrome Remote Desktop on Adapt Server"

# Step 1: Prepare the server environment
log "Preparing the server environment..."

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
# Ensure MTU is set to 1500 on all interfaces
echo "Setting MTU to 1500 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Setting MTU 1500 on $iface..."
  ip link set $iface mtu 1500
done

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

# Fix user permissions
echo "Fixing user permissions..."
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

# Fix firewall settings
echo "Fixing firewall settings..."
iptables -F 2>/dev/null || true
iptables -X 2>/dev/null || true
iptables -t nat -F 2>/dev/null || true
iptables -t nat -X 2>/dev/null || true
iptables -t mangle -F 2>/dev/null || true
iptables -t mangle -X 2>/dev/null || true
iptables -P INPUT ACCEPT 2>/dev/null || true
iptables -P FORWARD ACCEPT 2>/dev/null || true
iptables -P OUTPUT ACCEPT 2>/dev/null || true

# Restart Chrome Remote Desktop service
echo "Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@x.service
systemctl status chrome-remote-desktop@x.service
EOF

# Step 2: Generate a new authorization URL
section "Generating a new authorization URL"
log "Please visit the following URL in your browser to generate a new authorization code:"
log "https://remotedesktop.google.com/headless"
log "Click on 'Begin' and then 'Next', and authorize with your Google account."
log "Copy the command that starts with 'DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"...\"'"

# Step 3: Ask for the new authorization command
section "Enter the new authorization command"
read -p "Paste the authorization command here: " AUTH_COMMAND

# Extract the code from the command
CODE=$(echo "$AUTH_COMMAND" | grep -o 'code="[^"]*"' | cut -d'"' -f2)

if [ -z "$CODE" ]; then
  error "Could not extract authorization code from the command."
  exit 1
fi

success "Authorization code extracted: ${CODE:0:10}..."

# Step 4: Run the command on the server with the PIN
section "Running the authorization command on the server"
log "This will automatically enter the PIN: $PIN"

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << EOF
echo "Running Chrome Remote Desktop setup as x user with automatic PIN entry..."
su - x -c "echo -e \"$PIN\n$PIN\n\" | DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"$CODE\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=\$(hostname)"

# Check if the service is running
echo "Checking Chrome Remote Desktop service status..."
systemctl status chrome-remote-desktop@x.service
EOF

section "Summary"
success "Chrome Remote Desktop setup process completed."
log "If the setup was successful, you should now be able to connect to the adapt server via Chrome Remote Desktop."
log "If you encountered any errors, please check the output above for details."