#!/bin/bash
# Script to fix the SSH configuration for the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Backup the existing SSH config
echo "Backing up the existing SSH config..."
cp ~/.ssh/config ~/.ssh/config.bak

# Remove all entries for the Ethos server
echo "Removing all entries for the Ethos server..."
grep -v -E "Host ethos|HostName 10.240.0.5|HostName 52.118.146.160|User (root|ethos|x)|IdentityFile.*ibm-admin_rsa|StrictHostKeyChecking no|UserKnownHostsFile /dev/null" ~/.ssh/config.bak > ~/.ssh/config.new

# Add the new entries for the Ethos server
echo "Adding the new entries for the Ethos server..."
cat ethos_ssh_config >> ~/.ssh/config.new

# Replace the existing SSH config with the new one
echo "Replacing the existing SSH config with the new one..."
mv ~/.ssh/config.new ~/.ssh/config

echo "SSH configuration fixed successfully."
echo "You can now connect to the server using:"
echo "  ssh ethos-root  # Connect as root"
echo "  ssh ethos       # Connect as ethos user"
echo "  ssh ethos-x     # Connect as x user"