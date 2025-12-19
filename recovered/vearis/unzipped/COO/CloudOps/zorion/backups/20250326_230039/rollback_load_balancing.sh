#!/bin/bash
# Rollback script for load balancing implementation
# Generated on Wed Mar 26 11:45:07 PM MST 2025

echo "Rolling back load balancing implementation..."

# SSH to the server and restore original configuration
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "
  # Remove multipath routing
  echo 'Removing multipath routing...'
  ip route del default 2>/dev/null
  
  # Remove routing rules
  echo 'Removing routing rules...'
  ip rule show | grep -v 'from all' | cut -d: -f1 | while read -r rule_num; do
    ip rule del prio $rule_num 2>/dev/null
  done
  
  # Restore original default routes
  echo 'Restoring original default routes...'
  ip route add default via 10.240.8.1 dev eth7 metric 100
  ip route add default via 10.240.1.1 dev eth0 metric 200
  
  # Remove persistent configuration
  echo 'Removing persistent configuration...'
  rm -f /etc/network/if-up.d/multipath-routing
  rm -f /usr/local/sbin/setup-multipath-routing.sh
  
  echo 'Rollback completed.'
"

echo "Rollback script execution completed."
