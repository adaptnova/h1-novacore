#!/bin/bash
# Rollback script for public IP assignment
# Generated on Wed Mar 26 10:18:48 PM MST 2025

echo "Rolling back public IP assignment..."

# Unassign floating IPs
echo "Unassigning floating IPs..."
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="52.118.187.172") | .id') --target null
echo "Unassigned floating IP 52.118.187.172 from shortage-overcast-panda-keep"
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="52.118.145.162") | .id') --target null
echo "Unassigned floating IP 52.118.145.162 from bunt-comic-sixth-wrongness"
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="150.240.66.13") | .id') --target null
echo "Unassigned floating IP 150.240.66.13 from unmanaged-cyclist-providing-crux"
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="52.116.131.63") | .id') --target null
echo "Unassigned floating IP 52.116.131.63 from washday-await-corsage-obscurity"
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="52.118.191.234") | .id') --target null
echo "Unassigned floating IP 52.118.191.234 from activate-hazelnut-garage-automaker"
ibmcloud is floating-ip-update $(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address=="150.240.165.95") | .id') --target null
echo "Unassigned floating IP 150.240.165.95 from pgw-b1c7a2f0-0911-11f0-8f69-a725ab1e392f"

# Restore iptables rules
echo "Restoring iptables rules..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "iptables-restore < /tmp/iptables_backup.rules"

# Restore sysctl settings
echo "Restoring sysctl settings..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "sysctl -p /etc/sysctl.conf"

echo "Rollback completed."
