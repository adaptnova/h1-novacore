#!/bin/bash
# Script to check network interfaces on the dataops-primary server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Check the number of network interfaces
echo "Checking network interfaces..."
NIC_COUNT=$(ip link | grep -c "^[0-9]")

# Subtract 1 for the loopback interface
NIC_COUNT=$((NIC_COUNT - 1))

echo "Found $NIC_COUNT network interfaces (excluding loopback)."

# List all network interfaces
echo "Network interfaces:"
ip -o link show | grep -v "lo:" | awk -F': ' '{print $2}'
