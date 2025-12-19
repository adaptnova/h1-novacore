#!/bin/bash
# Script to add a 1TB disk to adapt3, format it as XFS, and mount it as /llms2
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

# Variables
SERVER_NAME="adapt3"
DISK_NAME="adapt3-llms2"
DISK_SIZE=1024 # 1TB in GB
ZONE="us-south-2"
RESOURCE_GROUP="adapt"
FLOATING_IP="52.118.206.209"
SSH_KEY="/home/x/.ssh/ibm-admin_rsa"

# Step 1: Create the volume
print_section "Step 1: Creating Volume"

echo "Creating volume $DISK_NAME..."
ibmcloud is volume-create $DISK_NAME general-purpose $ZONE --capacity $DISK_SIZE --resource-group-name $RESOURCE_GROUP

# Wait for the volume to be available
echo "Waiting for volume to be available..."
VOLUME_ID=""
while [ -z "$VOLUME_ID" ]; do
    echo "Checking if volume exists..."
    VOLUME_ID=$(ibmcloud is volumes | grep $DISK_NAME | awk '{print $1}')
    if [ -z "$VOLUME_ID" ]; then
        echo "Volume not found yet, waiting..."
        sleep 10
    fi
done

echo "Volume ID: $VOLUME_ID"
echo "Waiting for volume to be available..."
while true; do
    STATUS=$(ibmcloud is volume $VOLUME_ID --output json 2>/dev/null | jq -r '.status' 2>/dev/null)
    if [ "$STATUS" = "available" ]; then
        break
    fi
    echo "Volume status: $STATUS, waiting..."
    sleep 10
done

print_success "Volume created successfully."

# Step 2: Attach the volume to the server
print_section "Step 2: Attaching Volume to Server"

echo "Attaching volume to $SERVER_NAME..."
ibmcloud is instance-volume-attachment-add llms2 $SERVER_NAME $VOLUME_ID

# Wait for the volume to be attached
echo "Waiting for volume to be attached..."
sleep 30

# Verify the attachment
ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $SERVER_NAME --output json | jq -r '.[] | select(.volume.id=="'$VOLUME_ID'") | .id')
if [ -n "$ATTACHMENT_ID" ]; then
    print_success "Volume attached successfully with attachment ID: $ATTACHMENT_ID"
else
    print_error "Failed to attach volume."
    exit 1
fi

# Step 3: Format and mount the volume
print_section "Step 3: Formatting and Mounting Volume"

echo "Connecting to $SERVER_NAME..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$FLOATING_IP << 'EOF'
# Find the new disk
echo "Finding the new disk..."
lsblk
NEW_DISK=$(lsblk -p | grep -v sda | grep -v vda | grep -v NAME | grep disk | grep -v vdb | grep -v vdc | grep -v vdg | awk '{print $1}' | tail -1)
echo "New disk: $NEW_DISK"

# Format the disk as XFS
echo "Formatting disk as XFS..."
mkfs.xfs $NEW_DISK

# Create the mount point
echo "Creating mount point /llms2..."
mkdir -p /llms2

# Mount the disk
echo "Mounting disk to /llms2..."
mount $NEW_DISK /llms2

# Check the mount
echo "Checking mount..."
df -h /llms2

echo "Disk formatted and mounted successfully."
EOF

print_success "Disk formatted and mounted successfully."
print_success "Note: The disk is not added to fstab, so it will not be mounted automatically after a reboot."