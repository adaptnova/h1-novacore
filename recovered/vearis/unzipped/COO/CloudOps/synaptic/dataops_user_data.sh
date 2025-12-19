#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install basic utilities
apt-get install -y build-essential cmake git python3-dev python3-pip htop iotop iftop

# Create users
for user in synaptic forge x vertex; do
    useradd -m -s /bin/bash $user
    echo "$user:x" | chpasswd
    echo "$user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$user
    mkdir -p /home/$user/.ssh
    chmod 700 /home/$user/.ssh
    chown -R $user:$user /home/$user/.ssh
done

# Format and mount data volume
mkfs.xfs /dev/vdd
mkdir -p /data
echo "/dev/vdd /data xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /data
chmod 777 /data

# Format and mount backup volume
mkfs.xfs /dev/vde
mkdir -p /backup
echo "/dev/vde /backup xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /backup
chmod 777 /backup

# Install monitoring tools
apt-get install -y prometheus-node-exporter

# Install Filebeat for log forwarding
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y filebeat

# Configure system optimizations
cat > /etc/sysctl.d/99-dataops-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-dataops-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Create deployment success marker
echo "DataOps server deployed successfully on $(date)" > /data/deployment_complete.txt
