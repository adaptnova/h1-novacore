#!/bin/bash
# Script to create network attachments for a server
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

# Check if required parameters are provided
if [ $# -lt 3 ]; then
    print_error "Usage: $0 <instance_name> <subnet_id> <num_interfaces>"
    print_error "Example: $0 adapt3 0727-3bfdec47-9d1e-435e-b9e5-2559d37e8a07 6"
    exit 1
fi

# Parameters
INSTANCE_NAME=$1
SUBNET_ID=$2
NUM_INTERFACES=$3

# Get the existing network interface ID
print_section "Getting existing network interface information"
echo "Getting existing network interface ID..."
EXISTING_NIC_ID=$(ibmcloud is instance $INSTANCE_NAME --output json | jq -r '.network_interfaces[0].id')
echo "Existing network interface ID: $EXISTING_NIC_ID"

# Create network attachments
for i in $(seq 1 $NUM_INTERFACES); do
    print_section "Adding eth$i interface"
    echo "Adding eth$i interface..."
    RESULT=$(ibmcloud is instance-network-attachment-create $INSTANCE_NAME --vni-subnet $SUBNET_ID --vni-name eth$i --name eth$i-attachment --output json || echo '{"id": ""}')
    ID=$(echo $RESULT | jq -r '.id')
    if [ -n "$ID" ] && [ "$ID" != "null" ]; then
        print_success "Created eth$i with ID: $ID"
    else
        print_error "Failed to create eth$i interface."
    fi
    
    # Wait a bit between requests to avoid rate limiting
    sleep 5
done

# Wait for interfaces to be attached
print_section "Waiting for interfaces to be attached"
echo "Waiting for interfaces to be attached..."
sleep 30

# Verify all interfaces
print_section "Verifying all interfaces"
echo "Listing all network attachments for $INSTANCE_NAME..."
ibmcloud is instance-network-attachments $INSTANCE_NAME

print_success "All network attachments added successfully."