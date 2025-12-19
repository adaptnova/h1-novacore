#!/bin/bash
# Script to mount /dev/vdg and /dev/vdh and check their usage
# Created: 2025-03-23
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

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    print_error "This script must be run as root"
    exit 1
fi

# Show all disks
print_section "Current Disk Information"
lsblk
echo ""
df -h

# Mount /dev/vdg if not already mounted
print_section "Mounting /dev/vdg"
if mount | grep -q "/dev/vdg"; then
    print_success "/dev/vdg is already mounted"
    MOUNT_POINT=$(mount | grep "/dev/vdg" | awk '{print $3}')
    echo "Mount point: $MOUNT_POINT"
else
    echo "Mounting /dev/vdg..."
    
    # Check if the disk is formatted
    if blkid /dev/vdg | grep -q "TYPE="; then
        echo "Disk is already formatted"
    else
        echo "Formatting /dev/vdg as XFS..."
        mkfs.xfs /dev/vdg
    fi
    
    # Create mount point if it doesn't exist
    mkdir -p /llms
    
    # Mount the disk
    mount /dev/vdg /llms
    
    if [ $? -eq 0 ]; then
        print_success "/dev/vdg mounted successfully at /llms"
        MOUNT_POINT="/llms"
    else
        print_error "Failed to mount /dev/vdg"
        exit 1
    fi
fi

# Check usage of /dev/vdg
echo "Checking usage of /dev/vdg..."
df -h $MOUNT_POINT

# Mount /dev/vdh if not already mounted
print_section "Mounting /dev/vdh"
if mount | grep -q "/dev/vdh"; then
    print_success "/dev/vdh is already mounted"
    MOUNT_POINT2=$(mount | grep "/dev/vdh" | awk '{print $3}')
    echo "Mount point: $MOUNT_POINT2"
else
    echo "Mounting /dev/vdh..."
    
    # Check if the disk is formatted
    if blkid /dev/vdh | grep -q "TYPE="; then
        echo "Disk is already formatted"
    else
        echo "Formatting /dev/vdh as XFS..."
        mkfs.xfs /dev/vdh
    fi
    
    # Create mount point if it doesn't exist
    mkdir -p /llms2
    
    # Mount the disk
    mount /dev/vdh /llms2
    
    if [ $? -eq 0 ]; then
        print_success "/dev/vdh mounted successfully at /llms2"
        MOUNT_POINT2="/llms2"
    else
        print_error "Failed to mount /dev/vdh"
        exit 1
    fi
fi

# Check usage of /dev/vdh
echo "Checking usage of /dev/vdh..."
df -h $MOUNT_POINT2

# Summary
print_section "Disk Usage Summary"
echo "Disk /dev/vdg:"
df -h $MOUNT_POINT | grep -v "Filesystem" | awk '{print "Total: " $2 ", Used: " $3 " (" $5 "), Available: " $4}'

echo "Disk /dev/vdh:"
df -h $MOUNT_POINT2 | grep -v "Filesystem" | awk '{print "Total: " $2 ", Used: " $3 " (" $5 "), Available: " $4}'

print_success "Disk mounting and usage check completed"