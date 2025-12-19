#!/bin/bash
# Script to format and mount the new disk on adapt3
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Find the new disk
echo "Finding the new disk..."
lsblk
NEW_DISK=$(lsblk -p | grep -v sda | grep -v vda | grep -v NAME | grep disk | awk '{print $1}' | tail -1)
echo "New disk: $NEW_DISK"

# Format the disk as XFS
echo "Formatting disk as XFS..."
mkfs.xfs $NEW_DISK

# Create the mount point
echo "Creating mount point /llms..."
mkdir -p /llms

# Mount the disk
echo "Mounting disk to /llms..."
mount $NEW_DISK /llms

# Check the mount
echo "Checking mount..."
df -h /llms

echo "Disk formatted and mounted successfully."