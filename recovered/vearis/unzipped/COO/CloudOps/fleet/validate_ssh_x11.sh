#!/bin/bash
# Script to validate SSH X11 forwarding on servers
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
declare -A SERVERS
SERVERS["ethos"]="52.118.191.234"
SERVERS["dataops-timeseries"]="150.240.66.13"
SERVERS["dataops-vector"]="52.116.131.63"

# Test X11 forwarding on each server
for SERVER_NAME in "${!SERVERS[@]}"; do
    SERVER_IP=${SERVERS[$SERVER_NAME]}
    
    print_section "Testing X11 forwarding on $SERVER_NAME ($SERVER_IP)"
    
    # Test SSH connection with X11 forwarding
    echo "Connecting to $SERVER_NAME with X11 forwarding..."
    
    # Try to run a simple X11 test
    OUTPUT=$(ssh -i $SSH_KEY -o StrictHostKeyChecking=no -X root@$SERVER_IP "echo 'DISPLAY='$DISPLAY; which xclock; which xeyes; which xterm; ls -la /usr/bin/x*" 2>&1)
    echo "$OUTPUT"
    
    if echo "$OUTPUT" | grep -q "X11 forwarding request failed"; then
        print_error "X11 forwarding request failed on $SERVER_NAME."
    elif [ -z "$DISPLAY" ]; then
        print_error "DISPLAY variable not set on $SERVER_NAME."
    elif echo "$OUTPUT" | grep -q "/usr/bin/xclock\|/usr/bin/xeyes\|/usr/bin/xterm"; then
        print_success "X11 forwarding appears to be configured on $SERVER_NAME."
        echo "X11 applications are available."
    else
        print_error "X11 applications not found on $SERVER_NAME."
        echo "You may need to install x11-apps package."
    fi
    
    echo ""
done

print_section "X11 Forwarding Validation Complete"