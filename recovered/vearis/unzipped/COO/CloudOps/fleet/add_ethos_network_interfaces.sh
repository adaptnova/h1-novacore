#!/bin/bash
# Script to add network interfaces to the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Subnet ID
SUBNET_ID="0717-57b4b629-9704-4ba2-9fdb-63386cdba641"

# Get the existing network interface ID
echo "Getting existing network interface ID..."
EXISTING_NIC_ID=$(ibmcloud is instance ethos --output json | jq -r '.network_interfaces[0].id')
echo "Existing network interface ID: $EXISTING_NIC_ID"

# Add eth1 interface
echo "Adding eth1 interface..."
ETH1_RESULT=$(ibmcloud is instance-network-interface-create eth1 ethos $SUBNET_ID --output json || echo '{"id": ""}')
ETH1_ID=$(echo $ETH1_RESULT | jq -r '.id')
if [ -n "$ETH1_ID" ] && [ "$ETH1_ID" != "null" ]; then
    echo "Created eth1 with ID: $ETH1_ID"
else
    echo "Failed to create eth1 interface."
fi

# Add eth2 interface
echo "Adding eth2 interface..."
ETH2_RESULT=$(ibmcloud is instance-network-interface-create eth2 ethos $SUBNET_ID --output json || echo '{"id": ""}')
ETH2_ID=$(echo $ETH2_RESULT | jq -r '.id')
if [ -n "$ETH2_ID" ] && [ "$ETH2_ID" != "null" ]; then
    echo "Created eth2 with ID: $ETH2_ID"
else
    echo "Failed to create eth2 interface."
fi

# Add eth3 interface
echo "Adding eth3 interface..."
ETH3_RESULT=$(ibmcloud is instance-network-interface-create eth3 ethos $SUBNET_ID --output json || echo '{"id": ""}')
ETH3_ID=$(echo $ETH3_RESULT | jq -r '.id')
if [ -n "$ETH3_ID" ] && [ "$ETH3_ID" != "null" ]; then
    echo "Created eth3 with ID: $ETH3_ID"
else
    echo "Failed to create eth3 interface."
fi

# Wait for interfaces to be attached
echo "Waiting for interfaces to be attached..."
sleep 30

# Create floating IPs for each interface
echo "Creating floating IP for eth0 (primary)..."
# Check if a floating IP already exists for the primary interface
EXISTING_FIP=$(ibmcloud is instance ethos --output json | jq -r '.network_interfaces[0].floating_ips[0].address // empty')
if [ -z "$EXISTING_FIP" ]; then
    ibmcloud is floating-ip-reserve ethos-eth0-fip --zone us-south-1
else
    echo "Floating IP already exists for eth0: $EXISTING_FIP"
fi

# Create floating IPs for additional interfaces if they were created successfully
if [ -n "$ETH1_ID" ] && [ "$ETH1_ID" != "null" ]; then
    echo "Creating floating IP for eth1..."
    ibmcloud is floating-ip-reserve ethos-eth1-fip --zone us-south-1
fi

if [ -n "$ETH2_ID" ] && [ "$ETH2_ID" != "null" ]; then
    echo "Creating floating IP for eth2..."
    ibmcloud is floating-ip-reserve ethos-eth2-fip --zone us-south-1
fi

if [ -n "$ETH3_ID" ] && [ "$ETH3_ID" != "null" ]; then
    echo "Creating floating IP for eth3..."
    ibmcloud is floating-ip-reserve ethos-eth3-fip --zone us-south-1
fi

echo "All network interfaces and floating IPs added successfully."