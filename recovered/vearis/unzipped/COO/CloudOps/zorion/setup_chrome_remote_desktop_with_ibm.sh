#!/bin/bash
# Script to set up Chrome Remote Desktop with IBM Cloud credentials
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
IBM_USER="chase@levelup2x.com"
IBM_PASSWORD='@@ALALzmzm102938!!'
LOG_FILE="chrome_remote_desktop_ibm_setup.log"

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

section "IBM Cloud Login"
log "Logging in to IBM Cloud..."

# Login to IBM Cloud
ibmcloud login -u "$IBM_USER" -p "$IBM_PASSWORD" || {
  error "Failed to login to IBM Cloud"
  exit 1
}

success "Logged in to IBM Cloud"

section "Checking Server Connectivity"
log "Checking connectivity to the adapt server..."

# Check connectivity to the server
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'Connection successful'" || {
  error "Failed to connect to the server"
  exit 1
}

success "Connected to the server"

section "Checking Chrome Remote Desktop Installation"
log "Checking if Chrome Remote Desktop is installed..."

# Check if Chrome Remote Desktop is installed
CRD_INSTALLED=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "dpkg -l | grep chrome-remote-desktop || echo 'Not installed'")

if [[ "$CRD_INSTALLED" == *"Not installed"* ]]; then
  error "Chrome Remote Desktop is not installed"
  log "Please run the complete_chrome_remote_desktop_setup.sh script first"
  exit 1
fi

success "Chrome Remote Desktop is installed"

section "Setting Up Chrome Remote Desktop"
log "Setting up Chrome Remote Desktop with IBM Cloud credentials..."

# Create setup script
cat > /tmp/setup_crd_ibm.sh << 'EOF'
#!/bin/bash

# Create the Chrome Remote Desktop directory
mkdir -p /home/crduser/.config/chrome-remote-desktop

# Create the host configuration file
cat > /home/crduser/.config/chrome-remote-desktop/host.json << 'EOJ'
{
  "name": "adapt",
  "host_id": "$(hostname)-$(date +%s)",
  "host_version": "135.0.7049.8",
  "xsession_path": "/opt/google/chrome-remote-desktop/xfce-session",
  "xsession_args": [],
  "desktop_environment": "xfce"
}
EOJ

# Set permissions
chown -R crduser:crduser /home/crduser/.config/chrome-remote-desktop

# Restart the Chrome Remote Desktop service
systemctl restart chrome-remote-desktop@crduser

# Check the status
systemctl status chrome-remote-desktop@crduser
EOF

# Copy the script to the server
log "Copying setup script to the server..."
scp -o StrictHostKeyChecking=no /tmp/setup_crd_ibm.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/setup_crd_ibm.sh"

# Run the script
log "Running setup script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/setup_crd_ibm.sh"

section "Checking Chrome Remote Desktop Status"
log "Checking Chrome Remote Desktop status..."

# Check Chrome Remote Desktop status
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@crduser"

section "Setting Up DNS"
log "Setting up DNS for better connectivity..."

# Create DNS setup script
cat > /tmp/setup_dns.sh << 'EOF'
#!/bin/bash

# Backup the current resolv.conf
cp /etc/resolv.conf /etc/resolv.conf.bak

# Set up Google and Cloudflare DNS
cat > /etc/resolv.conf << 'EOD'
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
nameserver 1.0.0.1
EOD

# Test connectivity
ping -c 4 www.google.com
EOF

# Copy the script to the server
log "Copying DNS setup script to the server..."
scp -o StrictHostKeyChecking=no /tmp/setup_dns.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the DNS setup script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/setup_dns.sh"

# Run the script
log "Running DNS setup script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/setup_dns.sh"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ping -c 4 www.google.com"

section "Summary"
success "Chrome Remote Desktop setup with IBM Cloud credentials completed"
log "To complete the setup, follow these steps:"
log "1. Visit https://remotedesktop.google.com/headless"
log "2. Click on 'Set up another computer'"
log "3. Click on 'Begin'"
log "4. Click on 'Next'"
log "5. Click on 'Authorize'"
log "6. Copy the command that looks like:"
log "   DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/XXXX\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=\$(hostname)"
log "7. Run the command as the crduser:"
log "   su - crduser"
log "   [paste the command here]"
log "8. Set a PIN when prompted"
log "9. Go back to https://remotedesktop.google.com/access"
log "   You should see your computer listed there."
log "10. Click on it and enter your PIN to connect."
log ""
log "Note: The crduser password is \"crdpassword\""

echo -e "\nChrome Remote Desktop setup with IBM Cloud credentials completed. Check $LOG_FILE for details."