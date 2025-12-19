#!/bin/bash
# Script to test Chrome Remote Desktop connectivity
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

section "Testing Chrome Remote Desktop Connectivity"
log "Connecting to the adapt server..."

# Create a script to test connectivity
cat > /tmp/test_connectivity.sh << 'EOF'
#!/bin/bash

# Check if Chrome Remote Desktop service is running
echo "Checking Chrome Remote Desktop service status..."
systemctl status chrome-remote-desktop@x.service

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
journalctl -u chrome-remote-desktop@x.service --no-pager -n 20

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
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/test_connectivity.sh"

section "Summary"
success "Connectivity test completed."
log "Check the output above to verify that Chrome Remote Desktop is properly configured and connected."
log "If the service is running and can connect to Google's servers, you should be able to connect to the remote desktop."