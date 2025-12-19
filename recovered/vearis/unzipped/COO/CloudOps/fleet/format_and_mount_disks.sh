#!/bin/bash
# Script to format and mount disks on the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Format and mount /data (vdd)
echo "Formatting /dev/vdd as XFS..."
mkfs.xfs -f /dev/vdd
DATA_UUID=$(blkid -s UUID -o value /dev/vdd)
echo "UUID for /dev/vdd: $DATA_UUID"

echo "Creating /data directory..."
mkdir -p /data
echo "Mounting /dev/vdd to /data..."
mount /dev/vdd /data

echo "Adding entry to /etc/fstab for /data..."
echo "UUID=$DATA_UUID /data xfs defaults 0 2" >> /etc/fstab

# Format and mount /logs (vde)
echo "Formatting /dev/vde as XFS..."
mkfs.xfs -f /dev/vde
LOGS_UUID=$(blkid -s UUID -o value /dev/vde)
echo "UUID for /dev/vde: $LOGS_UUID"

echo "Creating /logs directory..."
mkdir -p /logs
echo "Mounting /dev/vde to /logs..."
mount /dev/vde /logs

echo "Adding entry to /etc/fstab for /logs..."
echo "UUID=$LOGS_UUID /logs xfs defaults 0 2" >> /etc/fstab

# Format and mount /llms (vdf)
echo "Formatting /dev/vdf as XFS..."
mkfs.xfs -f /dev/vdf
LLMS_UUID=$(blkid -s UUID -o value /dev/vdf)
echo "UUID for /dev/vdf: $LLMS_UUID"

echo "Creating /llms directory..."
mkdir -p /llms
echo "Mounting /dev/vdf to /llms..."
mount /dev/vdf /llms

echo "Adding entry to /etc/fstab for /llms..."
echo "UUID=$LLMS_UUID /llms xfs defaults 0 2" >> /etc/fstab

echo "All disks formatted and mounted successfully."