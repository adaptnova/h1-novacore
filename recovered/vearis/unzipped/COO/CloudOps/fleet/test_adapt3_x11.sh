#!/bin/bash
# Script to test X11 forwarding on adapt3 server
# Created: 2025-03-23
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}===== $1 =====${NC}\n"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# SSH key path
SSH_KEY="/home/x/.ssh/ibm-admin_rsa"

# Server information
SERVER_NAME="adapt3"
SERVER_IP="52.118.206.209"  # Updated with correct IP from fleet inventory

print_section "Testing X11 forwarding on $SERVER_NAME ($SERVER_IP)"

echo "Attempting to run xclock on $SERVER_NAME for 5 seconds..."
echo "If an xclock window appears, X11 forwarding is working correctly."
echo "Press Ctrl+C if xclock doesn't appear after 10 seconds."

# Run xclock with explicit DISPLAY setting and debug output
ssh -i $SSH_KEY -o StrictHostKeyChecking=no -v -X x@$SERVER_IP "
    echo 'DISPLAY environment variable: '\$DISPLAY
    echo 'Xauth entries:'
    xauth list 2>/dev/null || echo 'No xauth entries found'
    echo 'Checking for X11 applications:'
    which xclock xeyes xterm 2>/dev/null || echo 'X11 applications not found'
    echo 'Running xclock...'
    if which xclock >/dev/null 2>&1; then
        DISPLAY=\$DISPLAY xclock -update 1 & 
        PID=\$!
        sleep 5
        kill \$PID 2>/dev/null || true
    else
        echo 'xclock not found. Installing X11 applications...'
        apt-get update && apt-get install -y x11-apps xterm xauth
        echo 'Running xclock after installation...'
        DISPLAY=\$DISPLAY xclock -update 1 & 
        PID=\$!
        sleep 5
        kill \$PID 2>/dev/null || true
    fi
"

# Check the exit status
if [ $? -eq 0 ]; then
    print_success "X11 forwarding test completed on $SERVER_NAME."
    echo "Did you see the xclock window? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_success "X11 forwarding is working correctly on $SERVER_NAME."
    else
        print_error "X11 forwarding is not working correctly on $SERVER_NAME."
        echo "Please check your SSH X11 forwarding configuration."
    fi
else
    print_error "Failed to run xclock on $SERVER_NAME."
    echo "Please check if X11 applications are installed and X11 forwarding is enabled."
fi

print_section "X11 Forwarding Test Complete"