#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install basic utilities
apt-get install -y build-essential cmake git python3-dev python3-pip htop iotop iftop

# Install GNOME Desktop (full version)
apt-get install -y task-gnome-desktop

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install VS Code
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
apt-get update
apt-get install -y code

# Install Chrome Remote Desktop
wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
apt-get install -y ./chrome-remote-desktop_current_amd64.deb

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
DATA_UUID=$(blkid -s UUID -o value /dev/vdd)
mkdir -p /data
echo "UUID=$DATA_UUID /data xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /data
chmod 777 /data

# Format and mount logs volume
mkfs.xfs /dev/vde
LOGS_UUID=$(blkid -s UUID -o value /dev/vde)
mkdir -p /logs
echo "UUID=$LOGS_UUID /logs xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /logs
chmod 755 /logs

# Install Filebeat for log forwarding
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y filebeat

# Configure system optimizations
cat > /etc/sysctl.d/99-server-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-server-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Create deployment success marker
echo "Server deployed successfully on $(date)" > /data/deployment_complete.txt
echo "Disk UUIDs:" >> /data/deployment_complete.txt
echo "DATA_UUID=$DATA_UUID" >> /data/deployment_complete.txt
echo "LOGS_UUID=$LOGS_UUID" >> /data/deployment_complete.txt

# Get hostname to determine which server type this is
HOSTNAME=$(hostname)

if [[ "$HOSTNAME" == *"primary"* ]]; then
    # Install MongoDB and PostgreSQL
    apt-get install -y mongodb postgresql
    echo "Installed MongoDB and PostgreSQL on primary database server" >> /data/deployment_complete.txt
elif [[ "$HOSTNAME" == *"graph"* ]]; then
    # Install Neo4j
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list
    apt-get update
    apt-get install -y neo4j
    echo "Installed Neo4j on graph database server" >> /data/deployment_complete.txt
elif [[ "$HOSTNAME" == *"timeseries"* ]]; then
    # Install Redis
    apt-get install -y redis-server
    echo "Installed Redis on timeseries database server" >> /data/deployment_complete.txt
elif [[ "$HOSTNAME" == *"logs"* ]]; then
    # Install ELK stack
    apt-get install -y elasticsearch kibana logstash
    
    # Install Prometheus, Grafana, and Alertmanager
    apt-get install -y prometheus prometheus-alertmanager grafana
    
    # Start services
    systemctl enable elasticsearch kibana logstash prometheus grafana-server
    systemctl start elasticsearch kibana logstash prometheus grafana-server
    
    echo "Installed ELK stack and monitoring tools on logging server" >> /data/deployment_complete.txt
fi