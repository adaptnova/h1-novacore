#!/bin/bash
# Script to add SSH key to authorized_keys file
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# SSH public key to add
SSH_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCUKxOrbJZN9e+dbzKLNgdP/Mq7G2padUkPKKXBAZxYaFIHxGjbCoLtTdTr9O4HOI2OGxypt81E0yl1BfmzXq4O+4UgaRYWjefS57zMCGlwj5C2f6GAr5YZHwUv34ZmaKfgKUOSuNOzzjpozM4bI7ruhQib/saHhLz2GC++RD5MtyZRRiPEl7jaXom+fBy1/nEJUwXZhCxYINPWHm2WbawRY9gGNWJvLJNkMGVmCQC+U9BCOqD6N/NlN6q7EN2IYH+7CPV9PtMWyZTlXOaRkVivRScs4GKkV/iD0anyxDZFcNEE5kW/TsmE1zLXyTmUno6fceROUpuDYxQDx1PhQ6G15kmSK4o3oLv8eZQcMM3+IgUfNY4D5b3wl5EUhHxG8+f3SA5LuJPucGS+Xyi4uPRkPW17C4SHpRtechTiC7/1Zo2ndB7x51xi6Hq+pwCqgfq3fYF6uYP+Mvrm24QeLL/MYiu45/GDIcjrXRfBtIyXCyCqPTenn25d9DWV9A4iKNWiIDVaMwCZiqWsZ7wQ+RU7Ef9j35ma3LhN+Bo2mxCxJuFfEdnMicCJv9rteNa0DMmrpPydEWdc3VNuDftFK6y+rxtFflWgtD1uPBpp+z3MNdgvRSoP2l6CFaQEWAhqYcf+LruP+uKhL2TMynXsCBL7Ph6qgjk8kdA3LKgIYHD5bw== x@adapt3"

# Function to add SSH key to authorized_keys file for a user
add_ssh_key_to_user() {
    local username=$1
    
    echo "Adding SSH key to authorized_keys file for user '$username'..."
    
    # Create .ssh directory if it doesn't exist
    if [ ! -d "/home/$username/.ssh" ]; then
        mkdir -p "/home/$username/.ssh"
        chmod 700 "/home/$username/.ssh"
        chown $username:$username "/home/$username/.ssh"
    fi
    
    # Check if the key already exists in authorized_keys
    if [ -f "/home/$username/.ssh/authorized_keys" ]; then
        if grep -q "$SSH_PUBLIC_KEY" "/home/$username/.ssh/authorized_keys"; then
            echo "SSH key already exists in authorized_keys for user '$username'."
            return
        fi
    fi
    
    # Add the key to authorized_keys
    echo "$SSH_PUBLIC_KEY" >> "/home/$username/.ssh/authorized_keys"
    chmod 600 "/home/$username/.ssh/authorized_keys"
    chown $username:$username "/home/$username/.ssh/authorized_keys"
    
    echo "SSH key added to authorized_keys for user '$username'."
}

# Add SSH key to root user
echo "Adding SSH key to authorized_keys file for root user..."

# Create .ssh directory if it doesn't exist
if [ ! -d "/root/.ssh" ]; then
    mkdir -p "/root/.ssh"
    chmod 700 "/root/.ssh"
fi

# Check if the key already exists in authorized_keys
if [ -f "/root/.ssh/authorized_keys" ]; then
    if grep -q "$SSH_PUBLIC_KEY" "/root/.ssh/authorized_keys"; then
        echo "SSH key already exists in authorized_keys for root user."
    else
        # Add the key to authorized_keys
        echo "$SSH_PUBLIC_KEY" >> "/root/.ssh/authorized_keys"
        chmod 600 "/root/.ssh/authorized_keys"
        echo "SSH key added to authorized_keys for root user."
    fi
else
    # Create authorized_keys file and add the key
    echo "$SSH_PUBLIC_KEY" > "/root/.ssh/authorized_keys"
    chmod 600 "/root/.ssh/authorized_keys"
    echo "SSH key added to authorized_keys for root user."
fi

# Check if ethos user exists and add SSH key
if id "ethos" &>/dev/null; then
    add_ssh_key_to_user "ethos"
fi

# Check if vertex user exists and add SSH key
if id "vertex" &>/dev/null; then
    add_ssh_key_to_user "vertex"
fi

echo "SSH key addition completed."