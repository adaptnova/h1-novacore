#!/bin/bash
# Direct script to open port 443 on all interfaces
# No complex logic, just direct commands

# Connect to the server
ssh -o StrictHostKeyChecking=no root@10.240.1.6 << 'EOF'

# Flush all iptables rules
echo "Flushing all iptables rules..."
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Explicitly allow all traffic on port 443 for all interfaces
echo "Opening port 443 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  echo "Opening port 443 on $iface..."
  iptables -A INPUT -i $iface -p tcp --dport 443 -j ACCEPT
  iptables -A INPUT -i $iface -p udp --dport 443 -j ACCEPT
  iptables -A OUTPUT -o $iface -p tcp --dport 443 -j ACCEPT
  iptables -A OUTPUT -o $iface -p udp --dport 443 -j ACCEPT
done

# Disable any firewall service
echo "Disabling firewall services..."
systemctl stop firewalld 2>/dev/null || true
systemctl disable firewalld 2>/dev/null || true
systemctl stop ufw 2>/dev/null || true
systemctl disable ufw 2>/dev/null || true

# Restart Chrome Remote Desktop
echo "Restarting Chrome Remote Desktop..."
systemctl restart chrome-remote-desktop@x.service

# Verify port 443 is open
echo "Testing connectivity to Google's servers..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://www.google.com
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://remotedesktop.google.com

echo "Port 443 is now open on all interfaces."
EOF