#!/bin/bash
# Script to format and mount disks on adapt3
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Step 1: Format and mount /dev/vdg as /llms
echo "Step 1: Format and mount /dev/vdg as /llms"
echo "Formatting /dev/vdg as XFS..."
mkfs.xfs /dev/vdg

echo "Creating mount point /llms..."
mkdir -p /llms

echo "Mounting /dev/vdg to /llms..."
mount /dev/vdg /llms

echo "Checking mount..."
df -h /llms

# Step 2: Create RAID 0 with /dev/vdb and /dev/vdc and mount as /lssd
echo "Step 2: Create RAID 0 with /dev/vdb and /dev/vdc and mount as /lssd"
echo "Installing mdadm if not already installed..."
apt-get update
apt-get install -y mdadm

echo "Creating RAID 0 array..."
mdadm --create --verbose /dev/md0 --level=0 --raid-devices=2 /dev/vdb /dev/vdc

echo "Waiting for RAID array to initialize..."
sleep 5

echo "Formatting RAID array as XFS..."
mkfs.xfs /dev/md0

echo "Creating mount point /lssd..."
mkdir -p /lssd

echo "Mounting RAID array to /lssd..."
mount /dev/md0 /lssd

echo "Checking mount..."
df -h /lssd

echo "All disks formatted and mounted successfully."