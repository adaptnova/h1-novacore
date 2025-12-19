#!/bin/bash
# Script to check and attach network interfaces on the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Check the number of network interfaces
echo "Checking network interfaces..."
NIC_COUNT=$(ip link | grep -c "^[0-9]")

# Subtract 1 for the loopback interface
NIC_COUNT=$((NIC_COUNT - 1))

echo "Found $NIC_COUNT network interfaces (excluding loopback)."

if [ $NIC_COUNT -lt 4 ]; then
    echo "Warning: Less than 4 network interfaces found."
    echo "Please attach additional network interfaces using the IBM Cloud CLI:"
    echo "ibmcloud is instance-network-interface-add <name> ethos <subnet_id>"
else
    echo "All 4 network interfaces are attached."
fi

# List all network interfaces
echo "Network interfaces:"
ip -o link show | grep -v "lo:" | awk -F': ' '{print $2}'