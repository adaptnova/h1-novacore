#!/bin/bash
# Script to format and mount disks on the dataops-timeseries server
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

# Format and mount /backup (vde)
echo "Formatting /dev/vde as XFS..."
mkfs.xfs -f /dev/vde
BACKUP_UUID=$(blkid -s UUID -o value /dev/vde)
echo "UUID for /dev/vde: $BACKUP_UUID"

echo "Creating /backup directory..."
mkdir -p /backup
echo "Mounting /dev/vde to /backup..."
mount /dev/vde /backup

echo "Adding entry to /etc/fstab for /backup..."
echo "UUID=$BACKUP_UUID /backup xfs defaults 0 2" >> /etc/fstab

echo "All disks formatted and mounted successfully."
