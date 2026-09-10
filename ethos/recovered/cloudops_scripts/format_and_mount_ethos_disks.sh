#!/bin/bash
# Script to format and mount disks on ethos server
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

# Show current disk information
print_section "Current Disk Information"
lsblk
echo ""
df -h

# Identify the disks
print_section "Identifying Disks"
echo "Please enter the device name for the 1TB disk (e.g., vdd):"
read DISK_1TB

echo "Please enter the device name for the 2TB disk (e.g., vde):"
read DISK_2TB

# Confirm disk selection
echo "You selected:"
echo "1TB disk: /dev/$DISK_1TB"
echo "2TB disk: /dev/$DISK_2TB"
echo "Is this correct? (y/n)"
read CONFIRM

if [ "$CONFIRM" != "y" ]; then
    print_error "Disk selection not confirmed. Exiting."
    exit 1
fi

# Format the 2TB disk
print_section "Formatting 2TB Disk"
echo "Formatting /dev/$DISK_2TB as XFS..."
mkfs.xfs /dev/$DISK_2TB

if [ $? -eq 0 ]; then
    print_success "Disk /dev/$DISK_2TB formatted successfully"
else
    print_error "Failed to format disk /dev/$DISK_2TB"
    exit 1
fi

# Create mount points
print_section "Creating Mount Points"
echo "Creating mount points /llms and /llms1..."
mkdir -p /llms /llms1

# Mount the disks
print_section "Mounting Disks"
echo "Mounting /dev/$DISK_1TB to /llms..."
mount /dev/$DISK_1TB /llms

if [ $? -eq 0 ]; then
    print_success "Disk /dev/$DISK_1TB mounted successfully at /llms"
else
    print_error "Failed to mount disk /dev/$DISK_1TB at /llms"
    exit 1
fi

echo "Mounting /dev/$DISK_2TB to /llms1..."
mount /dev/$DISK_2TB /llms1

if [ $? -eq 0 ]; then
    print_success "Disk /dev/$DISK_2TB mounted successfully at /llms1"
else
    print_error "Failed to mount disk /dev/$DISK_2TB at /llms1"
    exit 1
fi

# Add entries to /etc/fstab
print_section "Adding Entries to /etc/fstab"
echo "Adding entries to /etc/fstab..."

# Check if entries already exist
if grep -q "/llms " /etc/fstab; then
    echo "Entry for /llms already exists in /etc/fstab"
else
    echo "/dev/$DISK_1TB /llms xfs defaults 0 0" >> /etc/fstab
    print_success "Entry for /llms added to /etc/fstab"
fi

if grep -q "/llms1 " /etc/fstab; then
    echo "Entry for /llms1 already exists in /etc/fstab"
else
    echo "/dev/$DISK_2TB /llms1 xfs defaults 0 0" >> /etc/fstab
    print_success "Entry for /llms1 added to /etc/fstab"
fi

# Verify mounts
print_section "Verifying Mounts"
echo "Checking disk usage..."
df -h /llms /llms1

print_success "Disks formatted and mounted successfully"
echo "The disks are now mounted and configured to mount automatically at boot."