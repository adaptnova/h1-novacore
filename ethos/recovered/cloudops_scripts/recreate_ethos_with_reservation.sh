#!/bin/bash
# Script to recreate the Ethos server with a reservation
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

# Variables
ETHOS_NAME="ethos"
SUBNET_ID="0717-57b4b629-9704-4ba2-9fdb-63386cdba641"
SSH_KEY_ID="r006-3183fd0f-80b8-49ce-9e49-080fdf64b115"
IMAGE_ID="r006-ae2c7bd1-25b3-4a42-8f01-59ee2cb0a6b5"
VPC_ID="r006-273e9e7d-9da9-4df2-8f93-c935d34b6a00"
PROFILE="gx3-48x240x2l40s"
ZONE="us-south-1"
RESOURCE_GROUP="adapt"

# Step 1: Get volume attachments
print_section "Step 1: Getting Volume Attachments"

echo "Getting volume attachments for $ETHOS_NAME..."
volume_attachments=$(ibmcloud is instance-volume-attachments $ETHOS_NAME --output json)

# Extract volume IDs and names
echo "Extracting volume information..."
volume_info=$(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | {id: .volume.id, name: .name}')
boot_volume_info=$(echo $volume_attachments | jq -r '.[] | select(.type == "boot") | {id: .volume.id, name: .name}')
boot_volume_id=$(echo $boot_volume_info | jq -r '.id')

echo "Boot volume ID: $boot_volume_id"
echo "Data volumes:"
echo "$volume_info" | jq

# Step 2: Stop the VM
print_section "Step 2: Stopping the VM"

echo "Stopping $ETHOS_NAME..."
ibmcloud is instance-stop $ETHOS_NAME

# Wait for the VM to stop
echo "Waiting for $ETHOS_NAME to stop..."
while [[ $(ibmcloud is instance $ETHOS_NAME --output json | jq -r '.status') != "stopped" ]]; do
    echo "Waiting for $ETHOS_NAME to stop..."
    sleep 10
done

print_success "$ETHOS_NAME stopped successfully."

# Step 3: Detach volumes
print_section "Step 3: Detaching Volumes"

echo "Detaching volumes from $ETHOS_NAME..."
for attachment in $(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | .id'); do
    echo "Detaching volume attachment $attachment..."
    ibmcloud is instance-volume-attachment-detach $ETHOS_NAME $attachment
done

# Wait for volumes to be detached
echo "Waiting for volumes to be detached..."
sleep 30

print_success "Volumes detached successfully."

# Step 4: Delete the VM
print_section "Step 4: Deleting the VM"

echo "Deleting $ETHOS_NAME..."
ibmcloud is instance-delete $ETHOS_NAME

# Wait for the VM to be deleted
echo "Waiting for $ETHOS_NAME to be deleted..."
while ibmcloud is instance $ETHOS_NAME &>/dev/null; do
    echo "Waiting for $ETHOS_NAME to be deleted..."
    sleep 10
done

print_success "$ETHOS_NAME deleted successfully."

# Step 5: Create reservation for Ethos server
print_section "Step 5: Creating Reservation for Ethos Server"

echo "Creating reservation for Ethos server..."
ibmcloud is reservation-create \
  --name ethos-reservation \
  --capacity 1 \
  --term three_year \
  --profile $PROFILE \
  --profile-resource-type instance_profile \
  --zone $ZONE \
  --affinity-policy automatic \
  --expiration-policy renew \
  --resource-group-name $RESOURCE_GROUP

# Check if reservation was created successfully
if [ $? -ne 0 ]; then
    print_error "Failed to create reservation for Ethos server."
    if ! confirm "Do you want to continue anyway?"; then
        print_error "Setup aborted."
        exit 1
    fi
fi

# Step 2: Get volume attachments
print_section "Step 2: Getting Volume Attachments"

echo "Getting volume attachments for $ETHOS_NAME..."
volume_attachments=$(ibmcloud is instance-volume-attachments $ETHOS_NAME --output json)

# Extract volume IDs and names
echo "Extracting volume information..."
volume_info=$(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | {id: .volume.id, name: .name}')
boot_volume_info=$(echo $volume_attachments | jq -r '.[] | select(.type == "boot") | {id: .volume.id, name: .name}')
boot_volume_id=$(echo $boot_volume_info | jq -r '.id')

echo "Boot volume ID: $boot_volume_id"
echo "Data volumes:"
echo "$volume_info" | jq

# Step 3: Stop the VM
print_section "Step 3: Stopping the VM"

echo "Stopping $ETHOS_NAME..."
ibmcloud is instance-stop $ETHOS_NAME

# Wait for the VM to stop
echo "Waiting for $ETHOS_NAME to stop..."
while [[ $(ibmcloud is instance $ETHOS_NAME --output json | jq -r '.status') != "stopped" ]]; do
    echo "Waiting for $ETHOS_NAME to stop..."
    sleep 10
done

print_success "$ETHOS_NAME stopped successfully."

# Step 4: Detach volumes
print_section "Step 4: Detaching Volumes"

echo "Detaching volumes from $ETHOS_NAME..."
for attachment in $(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | .id'); do
    echo "Detaching volume attachment $attachment..."
    ibmcloud is instance-volume-attachment-detach $ETHOS_NAME $attachment
done

# Wait for volumes to be detached
echo "Waiting for volumes to be detached..."
sleep 30

print_success "Volumes detached successfully."

# Step 5: Delete the VM
print_section "Step 5: Deleting the VM"

echo "Deleting $ETHOS_NAME..."
ibmcloud is instance-delete $ETHOS_NAME

# Wait for the VM to be deleted
echo "Waiting for $ETHOS_NAME to be deleted..."
while ibmcloud is instance $ETHOS_NAME &>/dev/null; do
    echo "Waiting for $ETHOS_NAME to be deleted..."
    sleep 10
done

print_success "$ETHOS_NAME deleted successfully."

# Step 6: Create a new VM with the same name
print_section "Step 6: Creating a New VM with the Same Name"

echo "Creating new $ETHOS_NAME with ibm-admin key..."
ibmcloud is instance-create $ETHOS_NAME $VPC_ID $ZONE $PROFILE $SUBNET_ID --image $IMAGE_ID --keys $SSH_KEY_ID --resource-group-id $RESOURCE_GROUP

# Wait for the VM to be running
echo "Waiting for $ETHOS_NAME to be running..."
while [[ $(ibmcloud is instance $ETHOS_NAME --output json | jq -r '.status') != "running" ]]; do
    echo "Waiting for $ETHOS_NAME to be running..."
    sleep 10
done

print_success "$ETHOS_NAME created successfully."

# Step 7: Attach volumes
print_section "Step 7: Attaching Volumes"

echo "Attaching volumes to $ETHOS_NAME..."
for volume in $(echo $volume_info | jq -c '.'); do
    volume_id=$(echo $volume | jq -r '.id')
    volume_name=$(echo $volume | jq -r '.name')
    echo "Attaching volume $volume_id as $volume_name..."
    ibmcloud is instance-volume-attachment-add $volume_name $ETHOS_NAME $volume_id
done

print_success "Volumes attached successfully."

# Step 8: Create a floating IP
print_section "Step 8: Creating a Floating IP"

echo "Creating a floating IP for $ETHOS_NAME..."
nic_id=$(ibmcloud is instance $ETHOS_NAME --output json | jq -r '.network_interfaces[0].id')
ibmcloud is floating-ip-reserve ethos-floating-ip-new --nic $nic_id

print_success "Floating IP created successfully."

# Step 9: Verify the VM is running
print_section "Step 9: Verifying the VM is Running"

echo "Verifying $ETHOS_NAME is running..."
ibmcloud is instance $ETHOS_NAME

# Step 10: Check if the VM is using the reservation
print_section "Step 10: Checking if the VM is Using the Reservation"

echo "Checking if $ETHOS_NAME is using the reservation..."
ibmcloud is instance $ETHOS_NAME --output json | jq -r '.reservation'

print_success "Ethos server recreated successfully with reservation."