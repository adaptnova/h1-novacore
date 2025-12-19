#!/bin/bash
# Script to set up users and SSH keys on Ethos and DataOps servers
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# SSH public key to add to authorized_keys
SSH_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCUKxOrbJZN9e+dbzKLNgdP/Mq7G2padUkPKKXBAZxYaFIHxGjbCoLtTdTr9O4HOI2OGxypt81E0yl1BfmzXq4O+4UgaRYWjefS57zMCGlwj5C2f6GAr5YZHwUv34ZmaKfgKUOSuNOzzjpozM4bI7ruhQib/saHhLz2GC++RD5MtyZRRiPEl7jaXom+fBy1/nEJUwXZhCxYINPWHm2WbawRY9gGNWJvLJNkMGVmCQC+U9BCOqD6N/NlN6q7EN2IYH+7CPV9PtMWyZTlXOaRkVivRScs4GKkV/iD0anyxDZFcNEE5kW/TsmE1zLXyTmUno6fceROUpuDYxQDx1PhQ6G15kmSK4o3oLv8eZQcMM3+IgUfNY4D5b3wl5EUhHxG8+f3SA5LuJPucGS+Xyi4uPRkPW17C4SHpRtechTiC7/1Zo2ndB7x51xi6Hq+pwCqgfq3fYF6uYP+Mvrm24QeLL/MYiu45/GDIcjrXRfBtIyXCyCqPTenn25d9DWV9A4iKNWiIDVaMwCZiqWsZ7wQ+RU7Ef9j35ma3LhN+Bo2mxCxJuFfEdnMicCJv9rteNa0DMmrpPydEWdc3VNuDftFK6y+rxtFflWgtD1uPBpp+z3MNdgvRSoP2l6CFaQEWAhqYcf+LruP+uKhL2TMynXsCBL7Ph6qgjk8kdA3LKgIYHD5bw== x@adapt3"

# Function to set up a user with SSH key and sudo privileges
setup_user_with_key() {
    local server=$1
    local username=$2
    local password=$3
    
    echo "Setting up user '$username' on server '$server'..."
    
    # Create a temporary script to run on the remote server
    cat > temp_setup.sh << EOF
#!/bin/bash
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

# Set up SSH key
mkdir -p /home/$username/.ssh
echo "$SSH_PUBLIC_KEY" > /home/$username/.ssh/authorized_keys
chmod 700 /home/$username/.ssh
chmod 600 /home/$username/.ssh/authorized_keys
chown -R $username:$username /home/$username/.ssh
echo "SSH key added to authorized_keys for user '$username'."

# Verify the setup
echo "Verifying user setup..."
id $username
grep $username /etc/sudoers.d/$username
ls -la /home/$username/.ssh
EOF
    
    # Make the script executable
    chmod +x temp_setup.sh
    
    # Copy the script to the server and execute it
    scp -i ./id_rsa -o StrictHostKeyChecking=no temp_setup.sh root@$server:/tmp/
    ssh -i ./id_rsa -o StrictHostKeyChecking=no root@$server "chmod +x /tmp/temp_setup.sh && /tmp/temp_setup.sh && rm /tmp/temp_setup.sh"
    
    # Remove the temporary script
    rm temp_setup.sh
    
    echo "Setup completed for user '$username' on server '$server'."
    echo "---------------------------------------------------"
}

# Main script execution
echo "Starting user setup on servers..."

# Setup for Ethos server
setup_user_with_key "10.240.0.5" "ethos" "x"

# Setup for DataOps servers
setup_user_with_key "10.240.0.6" "vertex" "x"  # dataops-primary
setup_user_with_key "10.240.0.7" "vertex" "x"  # dataops-vector
setup_user_with_key "10.240.0.8" "vertex" "x"  # dataops-timeseries

echo "User setup completed on all servers."

# Create SSH config file
cat > ~/.ssh/config << EOF
# SSH Config for CloudOps Fleet Servers
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Ethos Server
Host ethos
    HostName 10.240.0.5
    User ethos
    IdentityFile $(pwd)/id_rsa
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 10
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# DataOps Primary Server
Host dataops-primary
    HostName 10.240.0.6
    User vertex
    IdentityFile $(pwd)/id_rsa
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 10
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# DataOps Timeseries Server
Host dataops-timeseries
    HostName 10.240.0.8
    User vertex
    IdentityFile $(pwd)/id_rsa
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 10
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# DataOps Vector Server
Host dataops-vector
    HostName 10.240.0.7
    User vertex
    IdentityFile $(pwd)/id_rsa
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 10
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

chmod 600 ~/.ssh/config
echo "SSH config created at ~/.ssh/config"

echo "Setup complete. You can now access the servers using the following commands:"
echo "  ssh ethos"
echo "  ssh dataops-primary"
echo "  ssh dataops-timeseries"
echo "  ssh dataops-vector"