#!/bin/bash
# Script to deploy GNOME desktop to adapt server
# Created: 2025-03-29
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

# Function to print info message
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_section "Deploying GNOME Desktop to adapt server"

# Check if the script exists
if [ ! -f "switch_to_gnome_desktop_noninteractive.sh" ]; then
    print_error "switch_to_gnome_desktop_noninteractive.sh not found."
    exit 1
fi

# Copy the script to the adapt server
print_info "Copying script to adapt server..."
scp -i /home/x/.ssh/ibm-admin_rsa switch_to_gnome_desktop_noninteractive.sh root@10.240.1.6:/root/
if [ $? -eq 0 ]; then
    print_success "Script copied successfully."
else
    print_error "Failed to copy script to adapt server."
    exit 1
fi

# Execute the script on the adapt server
print_info "Executing script on adapt server..."
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.1.6 "chmod +x /root/switch_to_gnome_desktop_noninteractive.sh && /root/switch_to_gnome_desktop_noninteractive.sh"
if [ $? -eq 0 ]; then
    print_success "Script executed successfully."
else
    print_error "Failed to execute script on adapt server."
    exit 1
fi

print_section "Summary"
print_success "GNOME desktop has been deployed to adapt server."
print_info "Chrome Remote Desktop has been configured to use GNOME desktop."
print_info "Next time you connect to Chrome Remote Desktop, you should see the GNOME desktop."
print_info "If you still see Xfce desktop, try rebooting the server with:"
print_info "  ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.1.6 \"reboot\""