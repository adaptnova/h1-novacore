#!/bin/bash
# Script to set up the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Server IP address
SERVER_IP="52.118.146.160"
SSH_KEY="/home/x/.ssh/ibm-admin_rsa"

# Make all scripts executable
chmod +x format_and_mount_disks.sh create_users.sh check_network_interfaces.sh install_packages.sh

# Copy the scripts to the server
echo "Copying scripts to the server..."
scp -i $SSH_KEY format_and_mount_disks.sh create_users.sh check_network_interfaces.sh install_packages.sh root@$SERVER_IP:/tmp/

# SSH to the server and run the scripts
echo "Running scripts on the server..."
ssh -i $SSH_KEY root@$SERVER_IP "chmod +x /tmp/*.sh && /tmp/check_network_interfaces.sh && /tmp/install_packages.sh && /tmp/format_and_mount_disks.sh && /tmp/create_users.sh"

# Copy the SSH config file to the user's SSH config
echo "Adding SSH config entries..."
cat ethos_ssh_config >> ~/.ssh/config

echo "Ethos server setup completed successfully."
echo "You can now connect to the server using:"
echo "  ssh ethos-root  # Connect as root"
echo "  ssh ethos       # Connect as ethos user"
echo "  ssh ethos-x     # Connect as x user"