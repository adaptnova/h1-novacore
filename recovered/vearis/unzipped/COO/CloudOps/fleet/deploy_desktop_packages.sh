#!/bin/bash
# Script to deploy and execute the installation script on all servers
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
SERVERS["dataops-primary"]="52.118.145.162"
SERVERS["dataops-timeseries"]="150.240.66.13"
SERVERS["dataops-vector"]="52.116.131.63"
SERVERS["adapt3"]="52.118.206.209"

# Deploy and execute the installation script on all servers
for SERVER_NAME in "${!SERVERS[@]}"; do
    SERVER_IP=${SERVERS[$SERVER_NAME]}
    
    print_section "Deploying to $SERVER_NAME ($SERVER_IP)"
    
    # Copy the installation script to the server
    echo "Copying installation script to $SERVER_NAME..."
    scp -i $SSH_KEY -o StrictHostKeyChecking=no install_desktop_packages.sh root@$SERVER_IP:/tmp/
    
    if [ $? -eq 0 ]; then
        print_success "Installation script copied to $SERVER_NAME."
    else
        print_error "Failed to copy installation script to $SERVER_NAME."
        continue
    fi
    
    # Make the script executable
    echo "Making the script executable on $SERVER_NAME..."
    ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "chmod +x /tmp/install_desktop_packages.sh"
    
    if [ $? -eq 0 ]; then
        print_success "Script made executable on $SERVER_NAME."
    else
        print_error "Failed to make script executable on $SERVER_NAME."
        continue
    fi
    
    # Execute the installation script
    if [ "$SERVER_NAME" == "adapt3" ]; then
        # Only install Slack on adapt3
        print_section "Installing Slack on $SERVER_NAME"
        ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "apt-get update && apt-get install -y apt-transport-https curl wget gnupg software-properties-common && wget -q -O - https://packagecloud.io/slacktechnologies/slack/gpgkey | apt-key add - && sh -c 'echo \"deb https://packagecloud.io/slacktechnologies/slack/debian/ jessie main\" > /etc/apt/sources.list.d/slack.list' && apt-get update && apt-get install -y slack-desktop"
    else
        # Install all packages on other servers
        print_section "Installing all packages on $SERVER_NAME"
        ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$SERVER_IP "/tmp/install_desktop_packages.sh"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Installation completed successfully on $SERVER_NAME."
    else
        print_error "Installation failed on $SERVER_NAME."
    fi
done

print_success "Deployment completed!"