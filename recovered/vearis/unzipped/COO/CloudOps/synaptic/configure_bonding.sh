#!/bin/bash

# Install required packages
apt-get update
apt-get install -y ifenslave

# Load bonding module
modprobe bonding
echo "bonding" >> /etc/modules

# Create bonding configuration
cat > /etc/network/interfaces.d/bond0.conf << 'BONDCONF'
# Bond interface
auto bond0
iface bond0 inet static
    address 10.240.0.5
    netmask 255.255.255.0
    gateway 10.240.0.1
    dns-nameservers 8.8.8.8 8.8.4.4
    bond-mode 802.3ad
    bond-miimon 100
    bond-lacp-rate 1
    bond-slaves eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7 eth8 eth9
BONDCONF

# Restart networking
systemctl restart networking

# Check bonding status
cat /proc/net/bonding/bond0

# Check network speed
ethtool bond0 | grep Speed
