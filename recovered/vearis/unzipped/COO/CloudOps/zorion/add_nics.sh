#!/bin/bash

# Script to add network interfaces to an IBM Cloud instance
# This script monitors the instance status and adds NICs once the instance is ready

# Configuration
INSTANCE_ID="0717_ee285094-0683-4f21-a573-ae87022853e9"
INSTANCE_NAME="adapt"
SECURITY_GROUP="trekker-refill-quit-refueling"  # Using the same security group as the primary interface

# Subnets to add (we already have nic1-subnet)
SUBNETS=(
  "nic2-subnet"
  "nic3-subnet"
  "nic4-subnet"
  "nic5-subnet"
  "nic6-subnet"
  "nic7-subnet"
  "nic8-subnet"
)

# Function to check instance lifecycle state
check_instance_state() {
  local state=$(ibmcloud is instance $INSTANCE_ID --output JSON | grep -o '"lifecycle_state": "[^"]*"' | cut -d'"' -f4)
  echo $state
}

# Function to add a network interface
add_network_interface() {
  local subnet=$1
  local name="nic-${subnet:0:3}-interface"
  
  echo "Adding network interface $name with subnet $subnet..."
  ibmcloud is instance-network-interface-create $name $INSTANCE_ID $subnet --allow-ip-spoofing true
  
  if [ $? -eq 0 ]; then
    echo "Successfully added network interface $name"
    return 0
  else
    echo "Failed to add network interface $name"
    return 1
  fi
}

# Function to optimize network interface
optimize_network_interface() {
  local nic_id=$1
  
  echo "Optimizing network interface $nic_id..."
  # Add optimization commands here
  # For example:
  # ibmcloud is instance-network-interface-update $INSTANCE_ID $nic_id --name "optimized-$nic_id"
  
  return 0
}

# Main execution
echo "Starting NIC addition process for instance $INSTANCE_NAME ($INSTANCE_ID)"
echo "Waiting for instance to be ready (not in updating state)..."

# Wait for instance to be ready
while true; do
  STATE=$(check_instance_state)
  echo "Current instance state: $STATE"
  
  if [ "$STATE" != "updating" ]; then
    echo "Instance is ready. Proceeding with NIC addition."
    break
  fi
  
  echo "Instance is still updating. Waiting 30 seconds before checking again..."
  sleep 30
done

# Add network interfaces
echo "Adding network interfaces..."
for subnet in "${SUBNETS[@]}"; do
  add_network_interface $subnet
  
  # Wait a bit between additions to avoid rate limiting
  sleep 5
done

# List all network interfaces to verify
echo "Listing all network interfaces after addition:"
ibmcloud is instance-network-interfaces $INSTANCE_ID

echo "NIC addition process completed."
echo "Next steps: Configure routing and optimize network settings"

# Exit successfully
exit 0