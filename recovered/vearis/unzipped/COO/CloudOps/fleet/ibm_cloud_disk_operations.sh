#!/bin/bash
# Script to perform IBM Cloud disk operations
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

# Check if ibmcloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    print_error "IBM Cloud CLI is not installed"
    exit 1
fi

# Check if logged in to IBM Cloud
ibmcloud is volumes &> /dev/null
if [ $? -ne 0 ]; then
    print_error "Not logged in to IBM Cloud. Please log in using 'ibmcloud login' and try again."
    exit 1
fi

# Get volume IDs and attachment IDs
print_section "Getting Volume and Attachment IDs"
echo "Checking if volume adapt3-llms2 (/dev/vdh) exists..."
VDH_VOLUME_ID=$(ibmcloud is volumes --output json | jq -r '.[] | select(.name == "adapt3-llms2") | .id')

if [ -z "$VDH_VOLUME_ID" ]; then
    echo "Volume adapt3-llms2 (/dev/vdh) not found. It may have been already deleted."
    VDH_EXISTS=false
else
    print_success "Found volume ID for adapt3-llms2: $VDH_VOLUME_ID"
    VDH_EXISTS=true
fi

echo "Getting volume ID for /dev/vdg..."
VDG_VOLUME_ID=$(ibmcloud is volumes --output json | jq -r '.[] | select(.name == "adapt3-llms") | .id')

if [ -z "$VDG_VOLUME_ID" ]; then
    print_error "Could not find volume ID for adapt3-llms (/dev/vdg)"
    exit 1
else
    print_success "Found volume ID for adapt3-llms: $VDG_VOLUME_ID"
fi

# Get instance IDs
print_section "Getting Instance IDs"
echo "Getting instance ID for adapt3..."
ADAPT3_INSTANCE_ID=$(ibmcloud is instances --output json | jq -r '.[] | select(.name == "adapt3") | .id')

if [ -z "$ADAPT3_INSTANCE_ID" ]; then
    print_error "Could not find instance ID for adapt3"
    exit 1
else
    print_success "Found instance ID for adapt3: $ADAPT3_INSTANCE_ID"
fi

echo "Getting instance ID for ethos..."
ETHOS_INSTANCE_ID=$(ibmcloud is instances --output json | jq -r '.[] | select(.name == "ethos") | .id')

if [ -z "$ETHOS_INSTANCE_ID" ]; then
    print_error "Could not find instance ID for ethos"
    exit 1
else
    print_success "Found instance ID for ethos: $ETHOS_INSTANCE_ID"
fi

# Get volume attachment IDs
print_section "Getting Volume Attachment IDs"

if [ "$VDH_EXISTS" = true ]; then
    echo "Getting volume attachment ID for /dev/vdh..."
    VDH_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ADAPT3_INSTANCE_ID --output json | jq -r '.[] | select(.volume.name == "adapt3-llms2") | .id')

    if [ -z "$VDH_ATTACHMENT_ID" ]; then
        echo "Could not find volume attachment ID for adapt3-llms2 (/dev/vdh). It may be already detached."
    else
        print_success "Found volume attachment ID for adapt3-llms2: $VDH_ATTACHMENT_ID"
    fi
fi

echo "Getting volume attachment ID for /dev/vdg..."
VDG_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ADAPT3_INSTANCE_ID --output json | jq -r '.[] | select(.volume.name == "adapt3-llms") | .id')

if [ -z "$VDG_ATTACHMENT_ID" ]; then
    print_error "Could not find volume attachment ID for adapt3-llms (/dev/vdg)"
    exit 1
else
    print_success "Found volume attachment ID for adapt3-llms: $VDG_ATTACHMENT_ID"
fi

# Detach and delete /dev/vdh from adapt3 if it exists
if [ "$VDH_EXISTS" = true ] && [ ! -z "$VDH_ATTACHMENT_ID" ]; then
    # Detach /dev/vdh from adapt3
    print_section "Detaching /dev/vdh from adapt3"
    echo "Detaching volume adapt3-llms2 from adapt3..."
    ibmcloud is instance-volume-attachment-detach $ADAPT3_INSTANCE_ID $VDH_ATTACHMENT_ID --force

    if [ $? -eq 0 ]; then
        print_success "Volume adapt3-llms2 detached successfully"
    else
        print_error "Failed to detach volume adapt3-llms2"
        exit 1
    fi

    # Delete /dev/vdh
    print_section "Deleting /dev/vdh"
    echo "Deleting volume adapt3-llms2..."
    ibmcloud is volume-delete $VDH_VOLUME_ID --force

    if [ $? -eq 0 ]; then
        print_success "Volume adapt3-llms2 deleted successfully"
    else
        print_error "Failed to delete volume adapt3-llms2"
        exit 1
    fi
else
    print_section "Skipping Detach and Delete for /dev/vdh"
    echo "Skipping detach and delete operations for /dev/vdh as it doesn't exist or is already detached."
fi

# Create snapshot of /dev/vdg
print_section "Creating Snapshot of /dev/vdg"
echo "Creating snapshot of volume adapt3-llms..."
SNAPSHOT_NAME="adapt3-llms-snapshot-$(date +%Y%m%d%H%M%S)"
SNAPSHOT_ID=$(ibmcloud is snapshot-create --name $SNAPSHOT_NAME --volume $VDG_VOLUME_ID --output json | jq -r '.id')

if [ -z "$SNAPSHOT_ID" ]; then
    print_error "Failed to create snapshot of volume adapt3-llms"
    exit 1
else
    print_success "Snapshot created successfully with ID: $SNAPSHOT_ID"
fi

# Wait for snapshot to be available
echo "Waiting for snapshot to be available..."
SNAPSHOT_STATUS="pending"
while [ "$SNAPSHOT_STATUS" != "stable" ]; do
    sleep 10
    SNAPSHOT_STATUS=$(ibmcloud is snapshot $SNAPSHOT_ID --output json | jq -r '.lifecycle_state')
    echo "Snapshot status: $SNAPSHOT_STATUS"
    if [ "$SNAPSHOT_STATUS" == "failed" ]; then
        print_error "Snapshot creation failed"
        exit 1
    fi
done

print_success "Snapshot is now available"

# Check if 1TB volume for ethos already exists
print_section "Checking for Existing 1TB Volume for ethos"
echo "Checking if volume ethos-llms already exists..."
ETHOS_LLMS_VOLUME_NAME="ethos-llms"
ETHOS_LLMS_VOLUME_ID=$(ibmcloud is volumes --output json | jq -r '.[] | select(.name == "ethos-llms") | .id')

if [ -z "$ETHOS_LLMS_VOLUME_ID" ]; then
    # Create 1TB volume for ethos from snapshot
    print_section "Creating 1TB Volume for ethos from Snapshot"
    echo "Creating 1TB volume for ethos from snapshot..."
    ETHOS_LLMS_VOLUME_ID=$(ibmcloud is volume-create $ETHOS_LLMS_VOLUME_NAME general-purpose us-south-1 --snapshot $SNAPSHOT_ID --output json | jq -r '.id')

    if [ -z "$ETHOS_LLMS_VOLUME_ID" ]; then
        print_error "Failed to create volume for ethos from snapshot"
        exit 1
    else
        print_success "Volume created successfully with ID: $ETHOS_LLMS_VOLUME_ID"
    fi

    # Wait for volume to be available
    echo "Waiting for volume to be available..."
    VOLUME_STATUS="pending"
    while [ "$VOLUME_STATUS" != "available" ]; do
        sleep 10
        VOLUME_STATUS=$(ibmcloud is volume $ETHOS_LLMS_VOLUME_ID --output json | jq -r '.status')
        echo "Volume status: $VOLUME_STATUS"
        if [ "$VOLUME_STATUS" == "failed" ]; then
            print_error "Volume creation failed"
            exit 1
        fi
    done

    print_success "Volume is now available"
else
    print_success "Volume ethos-llms already exists with ID: $ETHOS_LLMS_VOLUME_ID"
fi

# Check if 2TB volume for ethos already exists
print_section "Checking for Existing 2TB Volume for ethos"
echo "Checking if volume ethos-llms1 already exists..."
ETHOS_LLMS1_VOLUME_NAME="ethos-llms1"
ETHOS_LLMS1_VOLUME_ID=$(ibmcloud is volumes --output json | jq -r '.[] | select(.name == "ethos-llms1") | .id')

if [ -z "$ETHOS_LLMS1_VOLUME_ID" ]; then
    # Create 2TB volume for ethos
    print_section "Creating 2TB Volume for ethos"
    echo "Creating 2TB volume for ethos..."
    ETHOS_LLMS1_VOLUME_ID=$(ibmcloud is volume-create $ETHOS_LLMS1_VOLUME_NAME general-purpose us-south-1 --capacity 2048 --output json | jq -r '.id')

    if [ -z "$ETHOS_LLMS1_VOLUME_ID" ]; then
        print_error "Failed to create 2TB volume for ethos"
        exit 1
    else
        print_success "2TB volume created successfully with ID: $ETHOS_LLMS1_VOLUME_ID"
    fi

    # Wait for volume to be available
    echo "Waiting for 2TB volume to be available..."
    VOLUME_STATUS="pending"
    while [ "$VOLUME_STATUS" != "available" ]; do
        sleep 10
        VOLUME_STATUS=$(ibmcloud is volume $ETHOS_LLMS1_VOLUME_ID --output json | jq -r '.status')
        echo "Volume status: $VOLUME_STATUS"
        if [ "$VOLUME_STATUS" == "failed" ]; then
            print_error "2TB volume creation failed"
            exit 1
        fi
    done

    print_success "2TB volume is now available"
else
    print_success "Volume ethos-llms1 already exists with ID: $ETHOS_LLMS1_VOLUME_ID"
fi

# Check if volumes are already attached to ethos
print_section "Checking Volume Attachments to ethos"
echo "Checking if 1TB volume is already attached to ethos..."
ETHOS_LLMS_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ETHOS_INSTANCE_ID --output json | jq -r '.[] | select(.volume.id == "'$ETHOS_LLMS_VOLUME_ID'") | .id')

if [ -z "$ETHOS_LLMS_ATTACHMENT_ID" ]; then
    # Attach 1TB volume to ethos
    echo "Attaching 1TB volume to ethos..."
    ATTACH_OUTPUT=$(ibmcloud is instance-volume-attachment-add llms $ETHOS_INSTANCE_ID $ETHOS_LLMS_VOLUME_ID --output json 2>&1)
    
    if [[ $ATTACH_OUTPUT == *"already exists"* ]]; then
        print_success "1TB volume is already attached to ethos with name: llms"
        # Get the attachment ID from the instance-volume-attachments command
        ETHOS_LLMS_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ETHOS_INSTANCE_ID --output json | jq -r '.[] | select(.name == "llms") | .id')
        if [ -n "$ETHOS_LLMS_ATTACHMENT_ID" ]; then
            print_success "Found attachment ID: $ETHOS_LLMS_ATTACHMENT_ID"
        fi
    else
        ETHOS_LLMS_ATTACHMENT_ID=$(echo $ATTACH_OUTPUT | jq -r '.id')
        if [ -z "$ETHOS_LLMS_ATTACHMENT_ID" ] || [ "$ETHOS_LLMS_ATTACHMENT_ID" == "null" ]; then
            print_error "Failed to attach 1TB volume to ethos"
            exit 1
        else
            print_success "1TB volume attached successfully with attachment ID: $ETHOS_LLMS_ATTACHMENT_ID"
        fi
    fi
else
    print_success "1TB volume is already attached to ethos with attachment ID: $ETHOS_LLMS_ATTACHMENT_ID"
fi

echo "Checking if 2TB volume is already attached to ethos..."
ETHOS_LLMS1_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ETHOS_INSTANCE_ID --output json | jq -r '.[] | select(.volume.id == "'$ETHOS_LLMS1_VOLUME_ID'") | .id')

if [ -z "$ETHOS_LLMS1_ATTACHMENT_ID" ]; then
    # Attach 2TB volume to ethos
    echo "Attaching 2TB volume to ethos..."
    ATTACH_OUTPUT=$(ibmcloud is instance-volume-attachment-add llms1 $ETHOS_INSTANCE_ID $ETHOS_LLMS1_VOLUME_ID --output json 2>&1)
    
    if [[ $ATTACH_OUTPUT == *"already exists"* ]]; then
        print_success "2TB volume is already attached to ethos with name: llms1"
        # Get the attachment ID from the instance-volume-attachments command
        ETHOS_LLMS1_ATTACHMENT_ID=$(ibmcloud is instance-volume-attachments $ETHOS_INSTANCE_ID --output json | jq -r '.[] | select(.name == "llms1") | .id')
        if [ -n "$ETHOS_LLMS1_ATTACHMENT_ID" ]; then
            print_success "Found attachment ID: $ETHOS_LLMS1_ATTACHMENT_ID"
        fi
    else
        ETHOS_LLMS1_ATTACHMENT_ID=$(echo $ATTACH_OUTPUT | jq -r '.id')
        if [ -z "$ETHOS_LLMS1_ATTACHMENT_ID" ] || [ "$ETHOS_LLMS1_ATTACHMENT_ID" == "null" ]; then
            print_error "Failed to attach 2TB volume to ethos"
            exit 1
        else
            print_success "2TB volume attached successfully with attachment ID: $ETHOS_LLMS1_ATTACHMENT_ID"
        fi
    fi
else
    print_success "2TB volume is already attached to ethos with attachment ID: $ETHOS_LLMS1_ATTACHMENT_ID"
fi

print_section "Summary"
echo "1. Detached and deleted /dev/vdh (adapt3-llms2) from adapt3"
echo "2. Created snapshot of /dev/vdg (adapt3-llms): $SNAPSHOT_NAME"
echo "3. Created 1TB volume for ethos from snapshot: $ETHOS_LLMS_VOLUME_NAME"
echo "4. Created 2TB volume for ethos: $ETHOS_LLMS1_VOLUME_NAME"
echo "5. Attached both volumes to ethos"

print_section "Next Steps"
echo "Connect to ethos and run the following commands to format and mount the volumes:"
echo ""
echo "# Format the 2TB volume (check device name first with lsblk)"
echo "mkfs.xfs /dev/vdX  # Replace vdX with the actual device name for the 2TB volume"
echo ""
echo "# Create mount points"
echo "mkdir -p /llms /llms1"
echo ""
echo "# Mount the volumes"
echo "mount /dev/vdY /llms  # Replace vdY with the actual device name for the 1TB volume"
echo "mount /dev/vdX /llms1  # Replace vdX with the actual device name for the 2TB volume"
echo ""
echo "# Add entries to /etc/fstab"
echo "echo '/dev/vdY /llms xfs defaults 0 0' >> /etc/fstab"
echo "echo '/dev/vdX /llms1 xfs defaults 0 0' >> /etc/fstab"
echo ""
echo "# Verify mounts"
echo "df -h /llms /llms1"

print_success "IBM Cloud disk operations completed successfully"