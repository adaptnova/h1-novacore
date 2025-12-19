#!/bin/bash
# Chrome Remote Desktop Setup Template Script
# Version: 2.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 28, 2025
#
# This template can be used to set up Chrome Remote Desktop on any IBM Cloud server
# Usage: ./crdt_setup_template.sh <server_ip> <pin> <auth_code>

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

# Check if all required parameters are provided
if [ $# -lt 3 ]; then
  error "Usage: $0 <server_ip> <pin> <auth_code>"
  exit 1
fi

SERVER_IP="$1"
PIN="$2"
AUTH_CODE="$3"
SSH_USER="root"

section "Chrome Remote Desktop Setup on Server: $SERVER_IP"

# Step 1: Comprehensive server preparation
log "Performing comprehensive server preparation..."

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
# Update package lists
echo "Updating package lists..."
apt-get update

# Install necessary dependencies
echo "Installing necessary dependencies..."
apt-get install -y xvfb xbase-clients python3 python3-psutil python3-cryptography

# Ensure MTU is set to 1500 on all interfaces
echo "Setting MTU to 1500 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Setting MTU 1500 on $iface..."
  ip link set $iface mtu 1500
done

# Stop any running Chrome Remote Desktop service
echo "Stopping Chrome Remote Desktop service..."
systemctl stop chrome-remote-desktop@x.service || true

# Completely remove existing Chrome Remote Desktop configuration
echo "Removing existing Chrome Remote Desktop configuration..."
rm -rf /home/x/.config/chrome-remote-desktop
rm -f /home/x/.chrome-remote-desktop-session

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

# Create a session file
echo "Creating Chrome Remote Desktop session file..."
cat > /home/x/.chrome-remote-desktop-session << 'EOS'
#!/bin/bash
exec /usr/bin/xfce4-session
EOS
chmod +x /home/x/.chrome-remote-desktop-session
chown x:x /home/x/.chrome-remote-desktop-session

# Fix user permissions
echo "Fixing user permissions..."
usermod -a -G sudo x
usermod -a -G adm x
usermod -a -G systemd-journal x
usermod -a -G video x
usermod -a -G audio x

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
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Ensure outbound connectivity to Google's servers
echo "Testing connectivity to Google's servers..."
curl -v https://remotedesktop.google.com/

# Ensure the Chrome Remote Desktop service is enabled
echo "Enabling Chrome Remote Desktop service..."
systemctl enable chrome-remote-desktop@x.service

# Create a temporary script to run the Chrome Remote Desktop setup
echo "Creating temporary setup script..."
cat > /tmp/setup_crdt.sh << 'EOT'
#!/bin/bash
export DISPLAY=:20
Xvfb :20 -screen 0 1920x1080x24 &
XVFB_PID=$!
sleep 2
echo "$1" | /opt/google/chrome-remote-desktop/start-host --code="$2" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)
kill $XVFB_PID
EOT
chmod +x /tmp/setup_crdt.sh
EOF

# Step 2: Run the Chrome Remote Desktop setup with PIN
section "Running Chrome Remote Desktop setup"
log "Using authorization code: ${AUTH_CODE:0:10}..."
log "Using PIN: $PIN"

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << EOF
# Run the setup script as user x
echo "Running Chrome Remote Desktop setup as user x..."
su - x -c "/tmp/setup_crdt.sh '$PIN\n$PIN' '$AUTH_CODE'"

# Check if the service is running
echo "Checking Chrome Remote Desktop service status..."
systemctl restart chrome-remote-desktop@x.service
systemctl status chrome-remote-desktop@x.service

# Clean up
echo "Cleaning up temporary files..."
rm -f /tmp/setup_crdt.sh
EOF

section "Verifying connectivity"
log "Checking if Chrome Remote Desktop is accessible..."

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP << 'EOF'
# Check if the Chrome Remote Desktop process is running
echo "Checking Chrome Remote Desktop process..."
ps aux | grep chrome-remote-desktop

# Check if the service is listening on the expected port
echo "Checking if the service is listening on the expected port..."
netstat -tuln | grep 3389

# Check the Chrome Remote Desktop logs
echo "Checking Chrome Remote Desktop logs..."
journalctl -u chrome-remote-desktop@x.service --no-pager -n 50
EOF

section "Summary"
success "Chrome Remote Desktop setup process completed for server: $SERVER_IP"
log "If the setup was successful, you should now be able to connect to the server via Chrome Remote Desktop."
log "If you encountered any errors, please check the output above for details."