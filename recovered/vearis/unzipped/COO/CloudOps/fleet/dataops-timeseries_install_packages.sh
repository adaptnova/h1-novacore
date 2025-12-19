#!/bin/bash
# Script to install necessary packages on the dataops-timeseries server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Update package lists
echo "Updating package lists..."
apt-get update

# Install xfsprogs for XFS filesystem support
echo "Installing xfsprogs..."
apt-get install -y xfsprogs

echo "Packages installed successfully."
