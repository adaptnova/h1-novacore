#!/bin/bash
# Script to set up the "ethos" user on the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

USERNAME="ethos"
PASSWORD="x"

echo "Setting up user '$USERNAME' on Ethos server..."

# Check if user already exists
if id "$USERNAME" &>/dev/null; then
    echo "User '$USERNAME' already exists. Updating configuration..."
else
    # Create the user
    useradd -m -s /bin/bash $USERNAME
    echo "User '$USERNAME' created."
fi

# Set password
echo "$USERNAME:$PASSWORD" | chpasswd
echo "Password set for user '$USERNAME'."

# Configure sudo with NOPASSWD
echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME
chmod 440 /etc/sudoers.d/$USERNAME
echo "Sudo privileges (NOPASSWD) configured for user '$USERNAME'."

# Verify the setup
echo "Verifying user setup..."
id $USERNAME
grep $USERNAME /etc/sudoers.d/$USERNAME

echo "Setup completed for user '$USERNAME' on Ethos server."