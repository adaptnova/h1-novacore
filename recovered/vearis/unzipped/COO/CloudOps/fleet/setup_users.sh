#!/bin/bash
# Script to set up users on Ethos and DataOps servers
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Function to set up a user with sudo privileges (NOPASSWD)
setup_user() {
    local server=$1
    local username=$2
    local password=$3
    
    echo "Setting up user '$username' on server '$server'..."
    
    # SSH to the server and execute commands
    ssh -o StrictHostKeyChecking=no root@$server << EOF
        # Check if user already exists
        if id "$username" &>/dev/null; then
            echo "User '$username' already exists. Updating configuration..."
        else
            # Create the user
            useradd -m -s /bin/bash $username
            echo "User '$username' created."
        fi
        
        # Set password
        echo "$username:$password" | chpasswd
        echo "Password set for user '$username'."
        
        # Configure sudo with NOPASSWD
        echo "$username ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$username
        chmod 440 /etc/sudoers.d/$username
        echo "Sudo privileges (NOPASSWD) configured for user '$username'."
        
        # Verify the setup
        echo "Verifying user setup..."
        id $username
        grep $username /etc/sudoers.d/$username
EOF
    
    echo "Setup completed for user '$username' on server '$server'."
    echo "---------------------------------------------------"
}

# Main script execution
echo "Starting user setup on servers..."

# Setup for Ethos server
setup_user "10.240.0.5" "ethos" "x"

# Setup for DataOps servers
setup_user "10.240.0.6" "vertex" "x"  # dataops-primary
setup_user "10.240.0.7" "vertex" "x"  # dataops-vector
setup_user "10.240.0.8" "vertex" "x"  # dataops-timeseries

echo "User setup completed on all servers."