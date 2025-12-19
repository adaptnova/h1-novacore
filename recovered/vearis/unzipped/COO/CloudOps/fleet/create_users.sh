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

echo "Users created and configured successfully."