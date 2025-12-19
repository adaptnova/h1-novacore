#!/bin/bash
# Script to format /dev/vdg as XFS and mount it as /llms
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Format the disk as XFS
echo "Formatting /dev/vdg as XFS..."
mkfs.xfs /dev/vdg

# Create the mount point
echo "Creating mount point /llms..."
mkdir -p /llms

# Mount the disk
echo "Mounting /dev/vdg to /llms..."
mount /dev/vdg /llms

# Check the mount
echo "Checking mount..."
df -h /llms

echo "Disk formatted and mounted successfully."