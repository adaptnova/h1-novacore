#!/bin/bash
# Script to complete Chrome Remote Desktop authorization
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="chrome_remote_desktop_auth.log"

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

section "Chrome Remote Desktop Authorization"
log "This script will help you complete the Chrome Remote Desktop authorization process."
log "Please follow these steps:"
log ""
log "1. Visit https://remotedesktop.google.com/headless"
log "2. Click on 'Set up another computer'"
log "3. Click on 'Begin'"
log "4. Click on 'Next'"
log "5. Click on 'Authorize'"
log "6. Copy the command that looks like:"
log "   DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/XXXX\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=\$(hostname)"
log ""
log "Please paste the command here (the one that starts with DISPLAY=):"
read -p "Command: " AUTH_COMMAND

if [[ -z "$AUTH_COMMAND" ]]; then
  error "No command provided. Exiting."
  exit 1
fi

section "Running Authorization Command"
log "Running the authorization command on the server..."

# Create authorization script
cat > /tmp/run_auth.sh << EOA
#!/bin/bash

# Switch to crduser
su - crduser << 'EOSUDO'
# Run the authorization command
$AUTH_COMMAND
EOSUDO

# Check if the service is running
systemctl status chrome-remote-desktop@crduser
EOA

# Copy the script to the server
log "Copying authorization script to the server..."
scp -o StrictHostKeyChecking=no /tmp/run_auth.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/run_auth.sh"

# Run the script
log "Running authorization script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/run_auth.sh"

section "Checking Chrome Remote Desktop Status"
log "Checking Chrome Remote Desktop status..."

# Check Chrome Remote Desktop status
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@crduser"

section "Summary"
success "Chrome Remote Desktop authorization completed"
log "You should now be able to access the server via Chrome Remote Desktop"
log "1. Go to https://remotedesktop.google.com/access"
log "2. You should see your computer listed there"
log "3. Click on it and enter your PIN to connect"

echo -e "\nChrome Remote Desktop authorization completed. Check $LOG_FILE for details."