#!/bin/bash
# Script to set up the DataOps VMs after recreation
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# SSH Key
SSH_KEY="/home/x/.ssh/ibm-admin_rsa"

# Function to set up a VM
setup_vm() {
    local vm_name=$1
    local floating_ip=$2
    
    echo "Setting up $vm_name..."
    
    # Create the setup scripts
    create_setup_scripts $vm_name
    
    # Make the scripts executable
    chmod +x ${vm_name}_format_and_mount_disks.sh ${vm_name}_create_users.sh ${vm_name}_check_network_interfaces.sh ${vm_name}_install_packages.sh
    
    # Create a floating IP if one doesn't exist
    if [ -z "$floating_ip" ]; then
        echo "Creating floating IP for $vm_name..."
        # Get the network interface ID
        nic_id=$(ibmcloud is instance $vm_name --output json | jq -r '.network_interfaces[0].id')
        # Create the floating IP
        floating_ip_json=$(ibmcloud is floating-ip-reserve ${vm_name}-floating-ip --nic $nic_id --output json)
        floating_ip=$(echo $floating_ip_json | jq -r '.address')
        echo "Created floating IP: $floating_ip"
        
        # Add additional network interfaces (3 more for a total of 4)
        echo "Adding additional network interfaces to $vm_name..."
        
        # Get subnet ID
        subnet_id=$(ibmcloud is instance $vm_name --output json | jq -r '.network_interfaces[0].subnet.id')
        
        # Add eth1 interface
        echo "Adding eth1 interface to $vm_name..."
        eth1_result=$(ibmcloud is instance-network-interface-create eth1 $vm_name $subnet_id --output json)
        eth1_id=$(echo $eth1_result | jq -r '.id')
        echo "Created eth1 with ID: $eth1_id"
        
        # Add eth2 interface
        echo "Adding eth2 interface to $vm_name..."
        eth2_result=$(ibmcloud is instance-network-interface-create eth2 $vm_name $subnet_id --output json)
        eth2_id=$(echo $eth2_result | jq -r '.id')
        echo "Created eth2 with ID: $eth2_id"
        
        # Add eth3 interface
        echo "Adding eth3 interface to $vm_name..."
        eth3_result=$(ibmcloud is instance-network-interface-create eth3 $vm_name $subnet_id --output json)
        eth3_id=$(echo $eth3_result | jq -r '.id')
        echo "Created eth3 with ID: $eth3_id"
        
        # Wait for interfaces to be attached
        echo "Waiting for interfaces to be attached..."
        sleep 30
        
        # Create floating IPs for each additional interface
        echo "Creating floating IP for eth1..."
        ibmcloud is floating-ip-reserve ${vm_name}-eth1-fip --nic $eth1_id
        
        echo "Creating floating IP for eth2..."
        ibmcloud is floating-ip-reserve ${vm_name}-eth2-fip --nic $eth2_id
        
        echo "Creating floating IP for eth3..."
        ibmcloud is floating-ip-reserve ${vm_name}-eth3-fip --nic $eth3_id
    fi
    
    # Copy the scripts to the server
    echo "Copying scripts to $vm_name ($floating_ip)..."
    scp -i $SSH_KEY ${vm_name}_format_and_mount_disks.sh ${vm_name}_create_users.sh ${vm_name}_check_network_interfaces.sh ${vm_name}_install_packages.sh root@$floating_ip:/tmp/
    
    # SSH to the server and run the scripts
    echo "Running scripts on $vm_name..."
    ssh -i $SSH_KEY root@$floating_ip "chmod +x /tmp/*.sh && /tmp/${vm_name}_check_network_interfaces.sh && /tmp/${vm_name}_install_packages.sh && /tmp/${vm_name}_format_and_mount_disks.sh && /tmp/${vm_name}_create_users.sh"
    
    # Create SSH config entry
    create_ssh_config $vm_name $floating_ip
    
    echo "$vm_name setup completed successfully."
}

# Function to create setup scripts for a VM
create_setup_scripts() {
    local vm_name=$1
    
    # Create install_packages.sh
    cat > ${vm_name}_install_packages.sh << EOF
#!/bin/bash
# Script to install necessary packages on the $vm_name server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Update package lists
echo "Updating package lists..."
apt-get update

# Install xfsprogs for XFS filesystem support
echo "Installing xfsprogs..."
apt-get install -y xfsprogs

echo "Packages installed successfully."
EOF
    
    # Create format_and_mount_disks.sh
    cat > ${vm_name}_format_and_mount_disks.sh << EOF
#!/bin/bash
# Script to format and mount disks on the $vm_name server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Format and mount /data (vdd)
echo "Formatting /dev/vdd as XFS..."
mkfs.xfs -f /dev/vdd
DATA_UUID=\$(blkid -s UUID -o value /dev/vdd)
echo "UUID for /dev/vdd: \$DATA_UUID"

echo "Creating /data directory..."
mkdir -p /data
echo "Mounting /dev/vdd to /data..."
mount /dev/vdd /data

echo "Adding entry to /etc/fstab for /data..."
echo "UUID=\$DATA_UUID /data xfs defaults 0 2" >> /etc/fstab

# Format and mount /backup (vde)
echo "Formatting /dev/vde as XFS..."
mkfs.xfs -f /dev/vde
BACKUP_UUID=\$(blkid -s UUID -o value /dev/vde)
echo "UUID for /dev/vde: \$BACKUP_UUID"

echo "Creating /backup directory..."
mkdir -p /backup
echo "Mounting /dev/vde to /backup..."
mount /dev/vde /backup

echo "Adding entry to /etc/fstab for /backup..."
echo "UUID=\$BACKUP_UUID /backup xfs defaults 0 2" >> /etc/fstab

echo "All disks formatted and mounted successfully."
EOF
    
    # Create create_users.sh
    cat > ${vm_name}_create_users.sh << EOF
#!/bin/bash
# Script to create users on the $vm_name server
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
EOF
    
    # Create check_network_interfaces.sh
    cat > ${vm_name}_check_network_interfaces.sh << EOF
#!/bin/bash
# Script to check network interfaces on the $vm_name server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Check the number of network interfaces
echo "Checking network interfaces..."
NIC_COUNT=\$(ip link | grep -c "^[0-9]")

# Subtract 1 for the loopback interface
NIC_COUNT=\$((NIC_COUNT - 1))

echo "Found \$NIC_COUNT network interfaces (excluding loopback)."

# List all network interfaces
echo "Network interfaces:"
ip -o link show | grep -v "lo:" | awk -F': ' '{print \$2}'
EOF
}

# Function to create SSH config for a VM
create_ssh_config() {
    local vm_name=$1
    local floating_ip=$2
    
    # Create SSH config file
    cat > ${vm_name}_ssh_config << EOF
# SSH Config for $vm_name Server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# $vm_name Server (root user)
Host ${vm_name}-root
    HostName $floating_ip
    User root
    IdentityFile /home/x/.ssh/ibm-admin_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# $vm_name Server (vertex user)
Host $vm_name
    HostName $floating_ip
    User vertex
    IdentityFile /home/x/.ssh/ibm-admin_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# $vm_name Server (x user)
Host ${vm_name}-x
    HostName $floating_ip
    User x
    IdentityFile /home/x/.ssh/ibm-admin_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
    
    # Add to SSH config
    echo "Adding SSH config entries for $vm_name..."
    cat ${vm_name}_ssh_config >> ~/.ssh/config
}

# Set up dataops-primary
setup_vm "dataops-primary" ""

# Set up dataops-timeseries
setup_vm "dataops-timeseries" ""

# Set up dataops-vector
setup_vm "dataops-vector" ""

echo "All DataOps VMs set up successfully."