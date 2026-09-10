#!/bin/bash
# Script to create users on the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Create user "x"
echo "Creating user 'x'..."
useradd -m -s /bin/bash x

# Set password for user "x"
echo "Setting password for user 'x'..."
echo "x:x" | chpasswd

# Create user "ethos"
echo "Creating user 'ethos'..."
useradd -m -s /bin/bash ethos

# Set password for user "ethos"
echo "Setting password for user 'ethos'..."
echo "ethos:x" | chpasswd

# Add users to sudo group
echo "Adding users to sudo group..."
usermod -aG sudo x
usermod -aG sudo ethos

# Configure sudo NOPASSWD for users
echo "Configuring sudo NOPASSWD for users..."
echo "x ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/x
echo "ethos ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ethos
chmod 440 /etc/sudoers.d/x
chmod 440 /etc/sudoers.d/ethos

# Create .ssh directories for users
echo "Creating .ssh directories for users..."
mkdir -p /home/x/.ssh
mkdir -p /home/ethos/.ssh
chmod 700 /home/x/.ssh
chmod 700 /home/ethos/.ssh

# Copy the authorized_keys file from root to users
echo "Copying authorized_keys file from root to users..."
cp /root/.ssh/authorized_keys /home/x/.ssh/
cp /root/.ssh/authorized_keys /home/ethos/.ssh/
chmod 600 /home/x/.ssh/authorized_keys
chmod 600 /home/ethos/.ssh/authorized_keys
chown -R x:x /home/x/.ssh
chown -R ethos:ethos /home/ethos/.ssh

# Format and mount the data volumes
echo "Formatting and mounting data volumes..."

# Check if the volumes exist
if [ -e /dev/vdd ]; then
    echo "Formatting /dev/vdd as XFS..."
    mkfs.xfs /dev/vdd
    
    echo "Creating mount point /data..."
    mkdir -p /data
    
    echo "Mounting /dev/vdd to /data..."
    mount /dev/vdd /data
    
    echo "Setting permissions for /data..."
    chown root:root /data
    chmod 755 /data
fi

if [ -e /dev/vde ]; then
    echo "Formatting /dev/vde as XFS..."
    mkfs.xfs /dev/vde
    
    echo "Creating mount point /logs..."
    mkdir -p /logs
    
    echo "Mounting /dev/vde to /logs..."
    mount /dev/vde /logs
    
    echo "Setting permissions for /logs..."
    chown root:root /logs
    chmod 755 /logs
fi

if [ -e /dev/vdf ]; then
    echo "Formatting /dev/vdf as XFS..."
    mkfs.xfs /dev/vdf
    
    echo "Creating mount point /llms..."
    mkdir -p /llms
    
    echo "Mounting /dev/vdf to /llms..."
    mount /dev/vdf /llms
    
    echo "Setting permissions for /llms..."
    chown root:root /llms
    chmod 755 /llms
fi

echo "Users created and volumes mounted successfully."