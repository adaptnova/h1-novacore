#!/bin/bash
# Script to create users on the dataops-primary server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Create user "x"
echo "Creating user 'x'..."
useradd -m -s /bin/bash x

# Set password for user "x"
echo "Setting password for user 'x'..."
echo "x:x" | chpasswd

# Create user "vertex"
echo "Creating user 'vertex'..."
useradd -m -s /bin/bash vertex

# Set password for user "vertex"
echo "Setting password for user 'vertex'..."
echo "vertex:x" | chpasswd

# Add users to sudo group
echo "Adding users to sudo group..."
usermod -aG sudo x
usermod -aG sudo vertex

# Configure sudo NOPASSWD for users
echo "Configuring sudo NOPASSWD for users..."
echo "x ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/x
echo "vertex ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/vertex
chmod 440 /etc/sudoers.d/x
chmod 440 /etc/sudoers.d/vertex

# Create .ssh directories for users
echo "Creating .ssh directories for users..."
mkdir -p /home/x/.ssh
mkdir -p /home/vertex/.ssh
chmod 700 /home/x/.ssh
chmod 700 /home/vertex/.ssh

# Copy the authorized_keys file from root to users
echo "Copying authorized_keys file from root to users..."
cp /root/.ssh/authorized_keys /home/x/.ssh/
cp /root/.ssh/authorized_keys /home/vertex/.ssh/
chmod 600 /home/x/.ssh/authorized_keys
chmod 600 /home/vertex/.ssh/authorized_keys
chown -R x:x /home/x/.ssh
chown -R vertex:vertex /home/vertex/.ssh

echo "Users created and configured successfully."
