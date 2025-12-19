#!/bin/bash
# Script to test X11 forwarding by running xclock on remote servers
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
    
    echo "Attempting to run xclock on $SERVER_NAME for 5 seconds..."
    echo "If an xclock window appears, X11 forwarding is working correctly."
    echo "Press Ctrl+C if xclock doesn't appear after 10 seconds."
    
    # Run xclock for 5 seconds
    ssh -i $SSH_KEY -o StrictHostKeyChecking=no -X root@$SERVER_IP "DISPLAY=\$DISPLAY xclock -update 1 & PID=\$!; sleep 5; kill \$PID"
    
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
    
    echo ""
done

print_section "X11 Forwarding Testing Complete"