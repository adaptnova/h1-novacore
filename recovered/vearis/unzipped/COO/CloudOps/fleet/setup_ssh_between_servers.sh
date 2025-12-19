#!/bin/bash
# Script to set up SSH key authentication between adapt3 and other servers
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

# Check if the public key exists
if [ ! -f "id_rsa.pub" ]; then
    print_error "Public key file id_rsa.pub not found in the current directory."
    exit 1
fi

# Copy the public key to each server
for SERVER_NAME in "${!SERVERS[@]}"; do
    SERVER_IP=${SERVERS[$SERVER_NAME]}
    
    print_section "Setting up SSH key authentication for $SERVER_NAME ($SERVER_IP)"
    
    # Copy the public key to the server
    echo "Copying public key to $SERVER_NAME..."
    
    # Create a temporary file with the public key
    TMP_FILE=$(mktemp)
    cat id_rsa.pub > $TMP_FILE
    
    # Copy the temporary file to the server
    scp -i $SSH_KEY -o StrictHostKeyChecking=no $TMP_FILE root@$SERVER_IP:/tmp/adapt3_id_rsa.pub
    
    if [ $? -eq 0 ]; then
        print_success "Public key copied to $SERVER_NAME."
    else
        print_error "Failed to copy public key to $SERVER_NAME."
        rm $TMP_FILE
        continue
    fi
    
    # Add the public key to the authorized_keys file for the x user
    echo "Adding public key to authorized_keys for x user on $SERVER_NAME..."
    ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "
        # Check if x user exists, create if not
        if ! id -u x > /dev/null 2>&1; then
            echo 'Creating x user...'
            useradd -m -s /bin/bash x
            echo 'x:x' | chpasswd
            usermod -aG sudo x
            echo 'x ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/x
            chmod 440 /etc/sudoers.d/x
        fi
        
        mkdir -p /home/x/.ssh
        cat /tmp/adapt3_id_rsa.pub >> /home/x/.ssh/authorized_keys
        chmod 700 /home/x/.ssh
        chmod 600 /home/x/.ssh/authorized_keys
        chown -R x:x /home/x/.ssh
        rm /tmp/adapt3_id_rsa.pub
    "
    
    if [ $? -eq 0 ]; then
        print_success "Public key added to authorized_keys for x user on $SERVER_NAME."
    else
        print_error "Failed to add public key to authorized_keys for x user on $SERVER_NAME."
    fi
    
    # Clean up
    rm $TMP_FILE
done

print_section "Testing SSH connections"

# Test SSH connections
for SERVER_NAME in "${!SERVERS[@]}"; do
    SERVER_IP=${SERVERS[$SERVER_NAME]}
    
    echo "Testing SSH connection to $SERVER_NAME ($SERVER_IP)..."
    ssh -i ./id_rsa -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 x@$SERVER_IP "echo 'SSH connection successful'"
    
    if [ $? -eq 0 ]; then
        print_success "SSH connection to $SERVER_NAME successful."
    else
        print_error "SSH connection to $SERVER_NAME failed."
    fi
done

print_success "SSH key authentication setup completed!"