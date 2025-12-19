#!/bin/bash
# Main script to set up the IBM Cloud Fleet with reservations
# Created: 2025-03-22
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

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# Main execution

print_section "IBM Cloud Fleet Setup"

echo "This script will set up the IBM Cloud Fleet with reservations and recreate VMs with the ibm-admin key."
echo "The following steps will be performed:"
echo "1. Create reservations for all servers (Ethos and DataOps VMs)"
echo "2. Add network interfaces to Ethos server"
echo "3. Recreate DataOps VMs with the ibm-admin key"
echo "4. Set up DataOps VMs with users, mount points, etc."

if ! confirm "Do you want to proceed?"; then
    print_error "Setup aborted."
    exit 1
fi

# Step 1: Create reservations
print_section "Step 1: Creating Reservations"

if confirm "Do you want to create reservations for all servers?"; then
    ./create_reservations.sh
    if [ $? -eq 0 ]; then
        print_success "Reservations created successfully."
    else
        print_error "Failed to create reservations."
        if ! confirm "Do you want to continue anyway?"; then
            print_error "Setup aborted."
            exit 1
        fi
    fi
else
    print_success "Skipping reservation creation."
fi

# Step 2: Add network interfaces to Ethos server
print_section "Step 2: Adding Network Interfaces to Ethos Server"

if confirm "Do you want to add network interfaces to the Ethos server?"; then
    ./add_ethos_network_interfaces.sh
    if [ $? -eq 0 ]; then
        print_success "Network interfaces added to Ethos server successfully."
    else
        print_error "Failed to add network interfaces to Ethos server."
        if ! confirm "Do you want to continue anyway?"; then
            print_error "Setup aborted."
            exit 1
        fi
    fi
else
    print_success "Skipping adding network interfaces to Ethos server."
fi

# Step 3: Recreate DataOps VMs
print_section "Step 3: Recreating DataOps VMs"

if confirm "Do you want to recreate DataOps VMs with the ibm-admin key?"; then
    ./recreate_dataops_vms.sh
    if [ $? -eq 0 ]; then
        print_success "DataOps VMs recreated successfully."
    else
        print_error "Failed to recreate DataOps VMs."
        if ! confirm "Do you want to continue anyway?"; then
            print_error "Setup aborted."
            exit 1
        fi
    fi
else
    print_success "Skipping DataOps VMs recreation."
fi

# Step 4: Set up DataOps VMs
print_section "Step 4: Setting Up DataOps VMs"

if confirm "Do you want to set up DataOps VMs with users, mount points, etc.?"; then
    ./setup_dataops_vms.sh
    if [ $? -eq 0 ]; then
        print_success "DataOps VMs set up successfully."
    else
        print_error "Failed to set up DataOps VMs."
        print_error "Setup incomplete."
        exit 1
    fi
else
    print_success "Skipping DataOps VMs setup."
fi

print_section "Setup Complete"
print_success "IBM Cloud Fleet setup completed successfully."
echo "You can now connect to the servers using the SSH config entries."
echo "For more information about dedicated hosts vs. regular instances, see dedicated_vs_regular_instances.md."