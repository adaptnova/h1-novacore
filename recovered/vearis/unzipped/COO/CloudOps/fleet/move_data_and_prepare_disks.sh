#!/bin/bash
# Script to move data from /dev/vdh to /dev/vdg, delete /dev/vdh, and prepare for snapshot
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

# Show current disk usage
print_section "Current Disk Usage"
df -h /llms /llms2

# Move data from /llms2 to /llms
print_section "Moving Data from /llms2 to /llms"
echo "Creating temporary directory in /llms..."
mkdir -p /llms/llms2_data

echo "Copying all data from /llms2 to /llms/llms2_data..."
rsync -av /llms2/ /llms/llms2_data/

# Verify the copy
echo "Verifying data copy..."
SOURCE_SIZE=$(du -s /llms2 | awk '{print $1}')
DEST_SIZE=$(du -s /llms/llms2_data | awk '{print $1}')

if [ "$SOURCE_SIZE" -eq "$DEST_SIZE" ]; then
    print_success "Data copy verified successfully"
else
    print_error "Data copy verification failed. Source size: $SOURCE_SIZE, Destination size: $DEST_SIZE"
    echo "Please check the data manually and try again."
    exit 1
fi

# Unmount /llms2
print_section "Unmounting /llms2"
echo "Unmounting /llms2..."
umount /llms2

if [ $? -eq 0 ]; then
    print_success "/llms2 unmounted successfully"
else
    print_error "Failed to unmount /llms2"
    echo "Please check if any processes are using /llms2 and try again."
    exit 1
fi

# Show current disk status
print_section "Current Disk Status"
lsblk
df -h

print_success "Data has been moved from /dev/vdh to /dev/vdg"
echo "The disk /dev/vdh can now be deleted."
echo "Next steps:"
echo "1. Delete /dev/vdh using IBM Cloud console or CLI"
echo "2. Create a snapshot of /dev/vdg"
echo "3. Add a 1TB disk to ethos using that snapshot"
echo "4. Add another 2TB disk to ethos"
echo "5. Format the 2TB disk with XFS"
echo "6. Mount the disks as /llms2 and /llms1 on ethos"
echo "7. Add entries to /etc/fstab for both mounts"