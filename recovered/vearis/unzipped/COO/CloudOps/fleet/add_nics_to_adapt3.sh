#!/bin/bash
# Script to add 6 additional network interfaces to the adapt3 server
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

# Subnet ID for adapt3 server
SUBNET_ID="0727-3bfdec47-9d1e-435e-b9e5-2559d37e8a07"

# Get the existing network interface ID
print_section "Getting existing network interface information"
echo "Getting existing network interface ID..."
EXISTING_NIC_ID=$(ibmcloud is instance adapt3 --output json | jq -r '.network_interfaces[0].id')
echo "Existing network interface ID: $EXISTING_NIC_ID"

# Add eth1 interface
print_section "Adding eth1 interface"
echo "Adding eth1 interface..."
ETH1_RESULT=$(ibmcloud is instance-network-interface-create eth1 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH1_ID=$(echo $ETH1_RESULT | jq -r '.id')
if [ -n "$ETH1_ID" ] && [ "$ETH1_ID" != "null" ]; then
    print_success "Created eth1 with ID: $ETH1_ID"
else
    print_error "Failed to create eth1 interface."
fi

# Add eth2 interface
print_section "Adding eth2 interface"
echo "Adding eth2 interface..."
ETH2_RESULT=$(ibmcloud is instance-network-interface-create eth2 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH2_ID=$(echo $ETH2_RESULT | jq -r '.id')
if [ -n "$ETH2_ID" ] && [ "$ETH2_ID" != "null" ]; then
    print_success "Created eth2 with ID: $ETH2_ID"
else
    print_error "Failed to create eth2 interface."
fi

# Add eth3 interface
print_section "Adding eth3 interface"
echo "Adding eth3 interface..."
ETH3_RESULT=$(ibmcloud is instance-network-interface-create eth3 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH3_ID=$(echo $ETH3_RESULT | jq -r '.id')
if [ -n "$ETH3_ID" ] && [ "$ETH3_ID" != "null" ]; then
    print_success "Created eth3 with ID: $ETH3_ID"
else
    print_error "Failed to create eth3 interface."
fi

# Add eth4 interface
print_section "Adding eth4 interface"
echo "Adding eth4 interface..."
ETH4_RESULT=$(ibmcloud is instance-network-interface-create eth4 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH4_ID=$(echo $ETH4_RESULT | jq -r '.id')
if [ -n "$ETH4_ID" ] && [ "$ETH4_ID" != "null" ]; then
    print_success "Created eth4 with ID: $ETH4_ID"
else
    print_error "Failed to create eth4 interface."
fi

# Add eth5 interface
print_section "Adding eth5 interface"
echo "Adding eth5 interface..."
ETH5_RESULT=$(ibmcloud is instance-network-interface-create eth5 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH5_ID=$(echo $ETH5_RESULT | jq -r '.id')
if [ -n "$ETH5_ID" ] && [ "$ETH5_ID" != "null" ]; then
    print_success "Created eth5 with ID: $ETH5_ID"
else
    print_error "Failed to create eth5 interface."
fi

# Add eth6 interface
print_section "Adding eth6 interface"
echo "Adding eth6 interface..."
ETH6_RESULT=$(ibmcloud is instance-network-interface-create eth6 adapt3 $SUBNET_ID --output json || echo '{"id": ""}')
ETH6_ID=$(echo $ETH6_RESULT | jq -r '.id')
if [ -n "$ETH6_ID" ] && [ "$ETH6_ID" != "null" ]; then
    print_success "Created eth6 with ID: $ETH6_ID"
else
    print_error "Failed to create eth6 interface."
fi

# Wait for interfaces to be attached
print_section "Waiting for interfaces to be attached"
echo "Waiting for interfaces to be attached..."
sleep 30

# Verify all interfaces
print_section "Verifying all interfaces"
echo "Listing all network interfaces for adapt3..."
ibmcloud is instance-network-interfaces adapt3

print_success "All network interfaces added successfully."