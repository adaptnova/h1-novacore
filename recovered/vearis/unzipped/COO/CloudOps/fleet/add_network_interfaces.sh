#!/bin/bash
# Script to add network interfaces to the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Subnet ID
SUBNET_ID="0717-57b4b629-9704-4ba2-9fdb-63386cdba641"

# Add eth1 interface
echo "Adding eth1 interface..."
ibmcloud is instance-network-interface-create eth1 ethos $SUBNET_ID

# Add eth2 interface
echo "Adding eth2 interface..."
ibmcloud is instance-network-interface-create eth2 ethos $SUBNET_ID

# Add eth3 interface
echo "Adding eth3 interface..."
ibmcloud is instance-network-interface-create eth3 ethos $SUBNET_ID

echo "Network interfaces added successfully."