#!/bin/bash
# Script to fix X11 forwarding on dataops-vector server
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
SERVER_NAME="dataops-vector"
SERVER_IP="52.116.131.63"

print_section "Fixing X11 forwarding on $SERVER_NAME ($SERVER_IP)"

echo "Installing X11 applications on $SERVER_NAME..."

# Temporarily disable problematic repositories and install X11 applications
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "
    # Backup sources.list.d
    mkdir -p /root/sources_backup
    cp -r /etc/apt/sources.list.d/* /root/sources_backup/
    
    # Temporarily move problematic repository files
    mv /etc/apt/sources.list.d/arangodb.list /root/sources_backup/ 2>/dev/null || true
    
    # Update and install X11 applications
    apt-get update && apt-get install -y x11-apps xterm
    
    # Restore repository files
    cp -r /root/sources_backup/* /etc/apt/sources.list.d/ 2>/dev/null || true
"

# Check if installation was successful
if [ $? -eq 0 ]; then
    print_success "X11 applications installed successfully on $SERVER_NAME."
else
    print_error "Failed to install X11 applications on $SERVER_NAME."
    exit 1
fi

# Configure X11 forwarding
echo "Configuring X11 forwarding on $SERVER_NAME..."

# Ensure X11 forwarding is enabled in SSH config
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "grep -q 'X11Forwarding yes' /etc/ssh/sshd_config || echo 'X11Forwarding yes' >> /etc/ssh/sshd_config"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "grep -q 'X11UseLocalhost no' /etc/ssh/sshd_config || echo 'X11UseLocalhost no' >> /etc/ssh/sshd_config"

# Restart SSH service
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "systemctl restart sshd"

# Check if configuration was successful
if [ $? -eq 0 ]; then
    print_success "X11 forwarding configured successfully on $SERVER_NAME."
else
    print_error "Failed to configure X11 forwarding on $SERVER_NAME."
    exit 1
fi

print_section "Testing X11 forwarding on $SERVER_NAME"

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
        print_success "X11 forwarding is now working correctly on $SERVER_NAME."
    else
        print_error "X11 forwarding is still not working correctly on $SERVER_NAME."
        echo "Please check your SSH X11 forwarding configuration."
    fi
else
    print_error "Failed to run xclock on $SERVER_NAME."
    echo "Please check if X11 applications are installed and X11 forwarding is enabled."
fi

print_section "X11 Forwarding Fix Complete"