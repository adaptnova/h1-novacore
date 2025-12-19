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

# Format and mount llms volume (for ethos only)
mkfs.xfs /dev/vdf
LLMS_UUID=$(blkid -s UUID -o value /dev/vdf)
mkdir -p /llms
echo "UUID=$LLMS_UUID /llms xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /llms
chmod 755 /llms

# Set up NVIDIA drivers and CUDA
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
dpkg -i cuda-keyring_1.1-1_all.deb
apt-get update

# Install NVIDIA drivers and CUDA
apt-get install -y cuda-drivers cuda

# Set up environment variables
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> /etc/profile.d/cuda.sh
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> /etc/profile.d/cuda.sh
chmod +x /etc/profile.d/cuda.sh

# Install Docker and NVIDIA Container Toolkit
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Install monitoring tools
apt-get install -y prometheus-node-exporter

# Install NVIDIA DCGM
apt-get install -y datacenter-gpu-manager

# Install Filebeat for log forwarding
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y filebeat

# Configure system optimizations
cat > /etc/sysctl.d/99-gpu-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-gpu-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Enable NVIDIA persistence mode
nvidia-smi -pm 1

# Create deployment success marker
echo "Ethos GPU server deployed successfully on $(date)" > /data/deployment_complete.txt
echo "Disk UUIDs:" >> /data/deployment_complete.txt
echo "DATA_UUID=$DATA_UUID" >> /data/deployment_complete.txt
echo "LOGS_UUID=$LOGS_UUID" >> /data/deployment_complete.txt
echo "LLMS_UUID=$LLMS_UUID" >> /data/deployment_complete.txt