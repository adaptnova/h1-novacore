#!/bin/bash
# Comprehensive script to fix X11 forwarding on dataops-vector server
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

print_section "Comprehensive X11 Forwarding Fix for $SERVER_NAME ($SERVER_IP)"

# Step 1: Check local X11 forwarding configuration
print_section "Step 1: Checking local X11 forwarding configuration"

if [ -z "$DISPLAY" ]; then
    print_error "Local DISPLAY variable is not set. X11 forwarding may not work."
    echo "Setting DISPLAY variable to :0.0"
    export DISPLAY=:0.0
else
    print_success "Local DISPLAY variable is set to $DISPLAY"
fi

# Step 2: Install X11 applications on the server
print_section "Step 2: Installing X11 applications on $SERVER_NAME"

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "
    # Backup sources.list.d
    mkdir -p /root/sources_backup
    cp -r /etc/apt/sources.list.d/* /root/sources_backup/ 2>/dev/null || true
    
    # Temporarily move problematic repository files
    mv /etc/apt/sources.list.d/arangodb.list /root/sources_backup/ 2>/dev/null || true
    
    # Update and install X11 applications
    apt-get update && apt-get install -y x11-apps xterm xauth
    
    # Restore repository files
    cp -r /root/sources_backup/* /etc/apt/sources.list.d/ 2>/dev/null || true
"

if [ $? -eq 0 ]; then
    print_success "X11 applications installed successfully on $SERVER_NAME."
else
    print_error "Failed to install X11 applications on $SERVER_NAME."
    exit 1
fi

# Step 3: Configure SSH server for X11 forwarding
print_section "Step 3: Configuring SSH server for X11 forwarding on $SERVER_NAME"

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "
    # Backup sshd_config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
    
    # Configure X11 forwarding
    sed -i 's/#X11Forwarding yes/X11Forwarding yes/g' /etc/ssh/sshd_config
    sed -i 's/X11Forwarding no/X11Forwarding yes/g' /etc/ssh/sshd_config
    
    # Add X11 forwarding configuration if not present
    grep -q 'X11Forwarding yes' /etc/ssh/sshd_config || echo 'X11Forwarding yes' >> /etc/ssh/sshd_config
    grep -q 'X11UseLocalhost no' /etc/ssh/sshd_config || echo 'X11UseLocalhost no' >> /etc/ssh/sshd_config
    grep -q 'X11DisplayOffset 10' /etc/ssh/sshd_config || echo 'X11DisplayOffset 10' >> /etc/ssh/sshd_config
    
    # Restart SSH service
    systemctl restart sshd
    
    # Verify configuration
    echo 'SSH server configuration:'
    grep -i 'x11' /etc/ssh/sshd_config
"

if [ $? -eq 0 ]; then
    print_success "SSH server configured successfully for X11 forwarding on $SERVER_NAME."
else
    print_error "Failed to configure SSH server for X11 forwarding on $SERVER_NAME."
    exit 1
fi

# Step 4: Configure SSH client for X11 forwarding
print_section "Step 4: Configuring SSH client for X11 forwarding"

# Check if ForwardX11 is enabled in SSH config
if grep -q "ForwardX11 yes" ~/.ssh/config 2>/dev/null; then
    print_success "ForwardX11 is already enabled in SSH client config."
else
    echo "Enabling ForwardX11 in SSH client config..."
    mkdir -p ~/.ssh
    echo -e "\nHost $SERVER_IP\n    ForwardX11 yes\n    ForwardX11Trusted yes" >> ~/.ssh/config
    print_success "ForwardX11 enabled in SSH client config."
fi

# Step 5: Test X11 forwarding
print_section "Step 5: Testing X11 forwarding on $SERVER_NAME"

echo "Attempting to run xclock on $SERVER_NAME for 5 seconds..."
echo "If an xclock window appears, X11 forwarding is working correctly."
echo "Press Ctrl+C if xclock doesn't appear after 10 seconds."

# Run xclock with explicit DISPLAY setting and debug output
ssh -i $SSH_KEY -o StrictHostKeyChecking=no -v -X root@$SERVER_IP "
    echo 'DISPLAY environment variable: '\$DISPLAY
    echo 'Xauth entries:'
    xauth list
    echo 'Running xclock...'
    DISPLAY=\$DISPLAY xclock -update 1 & 
    PID=\$!
    sleep 5
    kill \$PID 2>/dev/null || true
"

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

print_section "Comprehensive X11 Forwarding Fix Complete"