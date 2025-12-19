#!/bin/bash

# Script to configure routing for an IBM Cloud instance with multiple NICs
# This script sets up optimal routing based on network interface configuration

# Configuration
INSTANCE_ID="0717_ee285094-0683-4f21-a573-ae87022853e9"
INSTANCE_NAME="adapt"
SSH_USER="root"
SSH_HOST="10.240.1.6"  # Primary NIC IP

# Network configuration
# Format: "subnet_cidr:gateway:interface_name:priority"
NETWORKS=(
  "10.240.1.0/24:10.240.1.1:eth0:10"  # Primary network (management)
  "10.240.2.0/24:10.240.2.1:eth1:20"  # Secondary network
  "10.240.3.0/24:10.240.3.1:eth2:30"  # Tertiary network
  "10.240.4.0/24:10.240.4.1:eth3:40"  # Additional network
  "10.240.5.0/24:10.240.5.1:eth4:50"  # Additional network
  "10.240.6.0/24:10.240.6.1:eth5:60"  # Additional network
  "10.240.7.0/24:10.240.7.1:eth6:70"  # Additional network
  "10.240.8.0/24:10.240.8.1:eth7:80"  # Public network (with gateway)
)

# Function to check SSH connectivity
check_ssh() {
  echo "Checking SSH connectivity to $SSH_HOST..."
  ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST exit 2>/dev/null
  
  if [ $? -eq 0 ]; then
    echo "SSH connection successful"
    return 0
  else
    echo "SSH connection failed"
    return 1
  fi
}

# Function to configure network interfaces on the server
configure_interfaces() {
  echo "Configuring network interfaces..."
  
  # Create a temporary script to run on the remote server
  cat > /tmp/configure_interfaces.sh << 'EOF'
#!/bin/bash

# Detect OS type
if [ -f /etc/debian_version ]; then
  OS_TYPE="debian"
elif [ -f /etc/redhat-release ]; then
  OS_TYPE="redhat"
else
  echo "Unsupported OS type"
  exit 1
fi

# Function to configure Debian/Ubuntu interfaces
configure_debian() {
  echo "Configuring interfaces for Debian/Ubuntu..."
  
  # Backup existing configuration
  cp /etc/network/interfaces /etc/network/interfaces.bak
  
  # Create new configuration
  cat > /etc/network/interfaces << 'EOC'
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# Primary interface (Management)
auto eth0
iface eth0 inet dhcp

# Secondary interface
auto eth1
iface eth1 inet dhcp

# Tertiary interface
auto eth2
iface eth2 inet dhcp

# Additional interfaces
auto eth3
iface eth3 inet dhcp

auto eth4
iface eth4 inet dhcp

auto eth5
iface eth5 inet dhcp

auto eth6
iface eth6 inet dhcp

# Public interface
auto eth7
iface eth7 inet dhcp
EOC

  # Apply configuration
  systemctl restart networking
}

# Function to configure RHEL/CentOS interfaces
configure_redhat() {
  echo "Configuring interfaces for RHEL/CentOS..."
  
  # Configure each interface
  for i in {0..7}; do
    # Backup existing configuration
    if [ -f /etc/sysconfig/network-scripts/ifcfg-eth$i ]; then
      cp /etc/sysconfig/network-scripts/ifcfg-eth$i /etc/sysconfig/network-scripts/ifcfg-eth$i.bak
    fi
    
    # Create new configuration
    cat > /etc/sysconfig/network-scripts/ifcfg-eth$i << EOC
DEVICE=eth$i
BOOTPROTO=dhcp
ONBOOT=yes
TYPE=Ethernet
USERCTL=no
PEERDNS=yes
IPV6INIT=no
NM_CONTROLLED=no
EOC
  done
  
  # Apply configuration
  systemctl restart network
}

# Configure based on OS type
if [ "$OS_TYPE" == "debian" ]; then
  configure_debian
elif [ "$OS_TYPE" == "redhat" ]; then
  configure_redhat
fi

echo "Network interfaces configured successfully"
exit 0
EOF

  # Make the script executable
  chmod +x /tmp/configure_interfaces.sh
  
  # Copy and execute the script on the remote server
  scp -o StrictHostKeyChecking=no /tmp/configure_interfaces.sh $SSH_USER@$SSH_HOST:/tmp/
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "bash /tmp/configure_interfaces.sh"
  
  # Clean up
  rm /tmp/configure_interfaces.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "rm /tmp/configure_interfaces.sh"
}

# Function to configure routing on the server
configure_routing() {
  echo "Configuring routing..."
  
  # Create a temporary script to run on the remote server
  cat > /tmp/configure_routing.sh << 'EOF'
#!/bin/bash

# Detect OS type
if [ -f /etc/debian_version ]; then
  OS_TYPE="debian"
elif [ -f /etc/redhat-release ]; then
  OS_TYPE="redhat"
else
  echo "Unsupported OS type"
  exit 1
fi

# Clear existing routing rules
ip rule flush
ip rule add from all lookup local pref 0

# Add routing rules for each network
# Format: "subnet_cidr:gateway:interface_name:priority"
while IFS=: read -r subnet gateway interface priority; do
  echo "Configuring routing for $subnet via $gateway on $interface (priority $priority)..."
  
  # Add routing table
  table_num=$priority
  
  # Add rule to use this table for traffic from this subnet
  ip rule add from $subnet lookup $table_num pref $priority
  
  # Add routes to the table
  ip route add default via $gateway dev $interface table $table_num
  ip route add $subnet dev $interface table $table_num
  
  # Add source routing
  ip route add $subnet dev $interface src $(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
done < /tmp/networks.txt

# Make routing persistent
if [ "$OS_TYPE" == "debian" ]; then
  # For Debian/Ubuntu
  cat > /etc/network/if-up.d/routing << 'EOC'
#!/bin/bash
# Load routing rules on interface up
ip rule flush
ip rule add from all lookup local pref 0
while IFS=: read -r subnet gateway interface priority; do
  table_num=$priority
  ip rule add from $subnet lookup $table_num pref $priority
  ip route add default via $gateway dev $interface table $table_num
  ip route add $subnet dev $interface table $table_num
  ip route add $subnet dev $interface src $(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
done < /etc/network/routing_tables
EOC
  chmod +x /etc/network/if-up.d/routing
  
  # Save network configuration
  cp /tmp/networks.txt /etc/network/routing_tables
  
elif [ "$OS_TYPE" == "redhat" ]; then
  # For RHEL/CentOS
  cat > /etc/sysconfig/network-scripts/route-up << 'EOC'
#!/bin/bash
# Load routing rules on interface up
ip rule flush
ip rule add from all lookup local pref 0
while IFS=: read -r subnet gateway interface priority; do
  table_num=$priority
  ip rule add from $subnet lookup $table_num pref $priority
  ip route add default via $gateway dev $interface table $table_num
  ip route add $subnet dev $interface table $table_num
  ip route add $subnet dev $interface src $(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
done < /etc/sysconfig/network-scripts/routing_tables
EOC
  chmod +x /etc/sysconfig/network-scripts/route-up
  
  # Save network configuration
  cp /tmp/networks.txt /etc/sysconfig/network-scripts/routing_tables
  
  # Add to rc.local for startup
  echo "/etc/sysconfig/network-scripts/route-up" >> /etc/rc.d/rc.local
  chmod +x /etc/rc.d/rc.local
fi

echo "Routing configured successfully"
exit 0
EOF

  # Make the script executable
  chmod +x /tmp/configure_routing.sh
  
  # Create networks.txt file
  cat > /tmp/networks.txt << EOF
${NETWORKS[0]}
${NETWORKS[1]}
${NETWORKS[2]}
${NETWORKS[3]}
${NETWORKS[4]}
${NETWORKS[5]}
${NETWORKS[6]}
${NETWORKS[7]}
EOF
  
  # Copy files to the remote server
  scp -o StrictHostKeyChecking=no /tmp/configure_routing.sh $SSH_USER@$SSH_HOST:/tmp/
  scp -o StrictHostKeyChecking=no /tmp/networks.txt $SSH_USER@$SSH_HOST:/tmp/
  
  # Execute the script on the remote server
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "bash /tmp/configure_routing.sh"
  
  # Clean up
  rm /tmp/configure_routing.sh /tmp/networks.txt
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "rm /tmp/configure_routing.sh /tmp/networks.txt"
}

# Function to optimize network settings
optimize_network() {
  echo "Optimizing network settings..."
  
  # Create a temporary script to run on the remote server
  cat > /tmp/optimize_network.sh << 'EOF'
#!/bin/bash

# Backup sysctl.conf
cp /etc/sysctl.conf /etc/sysctl.conf.bak

# Add network optimization settings
cat >> /etc/sysctl.conf << 'EOC'

# Network Optimization Settings
# Increase system IP port limits
net.ipv4.ip_local_port_range = 1024 65535

# Increase TCP max buffer size
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# Increase Linux autotuning TCP buffer limits
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Enable TCP window scaling
net.ipv4.tcp_window_scaling = 1

# Enable TCP timestamps
net.ipv4.tcp_timestamps = 1

# Enable TCP SACK
net.ipv4.tcp_sack = 1

# Increase the maximum amount of option memory buffers
net.core.optmem_max = 65536

# Increase the maximum number of skb-heads to be cached
net.core.netdev_max_backlog = 5000

# Enable TCP Fast Open
net.ipv4.tcp_fastopen = 3

# Increase the maximum TCP receive buffer size
net.ipv4.tcp_rmem = 4096 87380 16777216

# Increase the maximum TCP send buffer size
net.ipv4.tcp_wmem = 4096 65536 16777216

# Increase the maximum TCP buffer size
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# Enable MTU probing
net.ipv4.tcp_mtu_probing = 1

# Enable TCP keepalive
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 5

# Enable BBR congestion control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Increase the maximum number of connections
net.core.somaxconn = 65535
EOC

# Apply sysctl settings
sysctl -p

# Optimize NIC settings for each interface
for i in {0..7}; do
  if [ -e /sys/class/net/eth$i ]; then
    echo "Optimizing eth$i..."
    
    # Set MTU to 9000 (jumbo frames) if supported
    ip link set dev eth$i mtu 9000 || ip link set dev eth$i mtu 1500
    
    # Enable TX/RX offloading
    ethtool -K eth$i tso on gso on gro on lro on tx on rx on 2>/dev/null || true
    
    # Set ring buffer sizes
    ethtool -G eth$i rx 4096 tx 4096 2>/dev/null || true
    
    # Set interrupt coalescing
    ethtool -C eth$i rx-usecs 100 tx-usecs 100 2>/dev/null || true
  fi
done

echo "Network optimization completed"
exit 0
EOF

  # Make the script executable
  chmod +x /tmp/optimize_network.sh
  
  # Copy and execute the script on the remote server
  scp -o StrictHostKeyChecking=no /tmp/optimize_network.sh $SSH_USER@$SSH_HOST:/tmp/
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "bash /tmp/optimize_network.sh"
  
  # Clean up
  rm /tmp/optimize_network.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "rm /tmp/optimize_network.sh"
}

# Main execution
echo "Starting network configuration for instance $INSTANCE_NAME ($INSTANCE_ID)"

# Check SSH connectivity
if check_ssh; then
  # Configure interfaces
  configure_interfaces
  
  # Configure routing
  configure_routing
  
  # Optimize network
  optimize_network
  
  echo "Network configuration completed successfully"
else
  echo "Cannot proceed with network configuration due to SSH connectivity issues"
  echo "Please ensure the instance is accessible via SSH before running this script"
  exit 1
fi

# Exit successfully
exit 0