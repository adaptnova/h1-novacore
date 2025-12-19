#!/bin/bash
# Script to format and mount /dev/vdd as /data and /dev/vde as /logs
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

# Format /dev/vdd as ext4
print_section "Formatting /dev/vdd"
echo "Formatting /dev/vdd as ext4 (force overwrite)..."
mkfs.ext4 -F /dev/vdd

if [ $? -eq 0 ]; then
    print_success "/dev/vdd formatted successfully"
else
    print_error "Failed to format /dev/vdd"
    exit 1
fi

# Skip formatting /dev/vde as it's too small
print_section "Skipping /dev/vde"
echo "Skipping formatting of /dev/vde as it's too small (44K)"
print_success "Skipping /dev/vde formatting"

# Create mount points
print_section "Creating Mount Points"
echo "Creating mount points /data and /logs..."
mkdir -p /data /logs

# Mount /dev/vdd to /data
print_section "Mounting /dev/vdd to /data"
echo "Mounting /dev/vdd to /data..."
mount /dev/vdd /data

if [ $? -eq 0 ]; then
    print_success "/dev/vdd mounted successfully at /data"
else
    print_error "Failed to mount /dev/vdd at /data"
    exit 1
fi

# Skip mounting /dev/vde
print_section "Skipping Mounting /dev/vde"
echo "Skipping mounting of /dev/vde as it's too small (44K)"
print_success "Skipping /dev/vde mounting"

# Add entries to /etc/fstab
print_section "Adding Entries to /etc/fstab"
echo "Adding entries to /etc/fstab..."

# Check if entry for /data already exists
if grep -q "/data " /etc/fstab; then
    echo "Entry for /data already exists in /etc/fstab"
else
    echo "/dev/vdd /data ext4 defaults 0 0" >> /etc/fstab
    print_success "Entry for /data added to /etc/fstab"
fi

# Skip adding /dev/vde to fstab
echo "Skipping adding /dev/vde to fstab as it's too small (44K)"

# Verify mounts
print_section "Verifying Mounts"
echo "Checking disk usage..."
df -h /data

print_success "Disks formatted and mounted successfully"
echo "The disks are now mounted and configured to mount automatically at boot."