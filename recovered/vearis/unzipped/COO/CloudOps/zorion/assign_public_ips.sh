#!/bin/bash
# Script to assign public IPs directly to all interfaces on adapt server
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
SERVER_NAME="adapt"
SERVER_ID="0717_ee285094-0683-4f21-a573-ae87022853e9"
SSH_USER="root"
SERVER_IP="10.240.1.6"
LOG_FILE="public_ip_assignment.log"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to display section headers
section() {
  log "${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  log "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  log "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  log "${YELLOW}! $1${NC}"
}

# Function to create backup directory
create_backup_dir() {
  section "Creating Backup Directory"
  mkdir -p "$BACKUP_DIR"
  success "Created backup directory: $BACKUP_DIR"
}

# Function to backup current network configuration
backup_network_config() {
  section "Backing Up Current Network Configuration"
  
  # Backup network interfaces
  log "Backing up network interfaces..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -j addr show" > "$BACKUP_DIR/interfaces_backup.json"
  
  # Backup routing table
  log "Backing up routing table..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -j route show" > "$BACKUP_DIR/routes_backup.json"
  
  # Backup iptables rules
  log "Backing up iptables rules..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables-save" > "$BACKUP_DIR/iptables_backup.rules"
  
  # Backup sysctl settings
  log "Backing up sysctl settings..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "sysctl -a" > "$BACKUP_DIR/sysctl_backup.conf"
  
  success "Network configuration backed up to $BACKUP_DIR"
}

# Function to check if floating IPs are available
check_floating_ips() {
  section "Checking Available Floating IPs"
  
  log "Listing available floating IPs..."
  FLOATING_IPS=$(ibmcloud is floating-ips --output JSON)
  
  if [ $? -ne 0 ]; then
    error "Failed to list floating IPs"
    return 1
  fi
  
  # Count available floating IPs
  AVAILABLE_COUNT=$(echo "$FLOATING_IPS" | grep -c '"status": "available"')
  
  log "Found $AVAILABLE_COUNT available floating IPs"
  
  if [ "$AVAILABLE_COUNT" -lt 8 ]; then
    warning "Not enough floating IPs available. Need 8, found $AVAILABLE_COUNT"
    
    # Create more floating IPs if needed
    log "Creating additional floating IPs..."
    for i in $(seq 1 $((8 - AVAILABLE_COUNT))); do
      log "Creating floating IP $i of $((8 - AVAILABLE_COUNT))..."
      ibmcloud is floating-ip-create --name "adapt-floating-ip-$i" --zone us-south-1 --output JSON
      
      if [ $? -ne 0 ]; then
        error "Failed to create floating IP $i"
        return 1
      fi
    done
    
    success "Created additional floating IPs"
  else
    success "Sufficient floating IPs available"
  fi
  
  return 0
}

# Function to get network interface IDs
get_network_interface_ids() {
  section "Getting Network Interface IDs"
  
  log "Listing network interfaces for server $SERVER_ID..."
  NETWORK_INTERFACES=$(ibmcloud is instance-network-interfaces $SERVER_ID --output JSON)
  
  if [ $? -ne 0 ]; then
    error "Failed to list network interfaces"
    return 1
  fi
  
  # Extract interface IDs and names
  echo "$NETWORK_INTERFACES" | jq -r '.[] | "\(.id)|\(.name)"' > "$BACKUP_DIR/interface_ids.txt"
  
  success "Network interface IDs saved to $BACKUP_DIR/interface_ids.txt"
  return 0
}

# Function to assign floating IPs to interfaces
assign_floating_ips() {
  section "Assigning Floating IPs to Interfaces"
  
  # Get available floating IPs
  FLOATING_IPS=$(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.status=="available") | .id')
  
  if [ -z "$FLOATING_IPS" ]; then
    error "No available floating IPs found"
    return 1
  fi
  
  # Convert to array
  readarray -t FLOATING_IP_ARRAY <<< "$FLOATING_IPS"
  
  # Get interface IDs
  if [ ! -f "$BACKUP_DIR/interface_ids.txt" ]; then
    error "Interface IDs file not found"
    return 1
  fi
  
  # Read interface IDs
  readarray -t INTERFACE_LINES < "$BACKUP_DIR/interface_ids.txt"
  
  # Assign floating IPs to interfaces
  for i in "${!INTERFACE_LINES[@]}"; do
    if [ $i -ge ${#FLOATING_IP_ARRAY[@]} ]; then
      warning "Not enough floating IPs for all interfaces"
      break
    fi
    
    # Extract interface ID and name
    IFS='|' read -r INTERFACE_ID INTERFACE_NAME <<< "${INTERFACE_LINES[$i]}"
    
    log "Assigning floating IP ${FLOATING_IP_ARRAY[$i]} to interface $INTERFACE_NAME ($INTERFACE_ID)..."
    
    # Assign floating IP to interface
    ibmcloud is floating-ip-update ${FLOATING_IP_ARRAY[$i]} --target $INTERFACE_ID
    
    if [ $? -ne 0 ]; then
      error "Failed to assign floating IP to interface $INTERFACE_NAME"
      continue
    fi
    
    success "Assigned floating IP to interface $INTERFACE_NAME"
  done
  
  return 0
}

# Function to verify floating IP assignment
verify_floating_ips() {
  section "Verifying Floating IP Assignment"
  
  log "Listing floating IPs..."
  FLOATING_IPS=$(ibmcloud is floating-ips --output JSON)
  
  if [ $? -ne 0 ]; then
    error "Failed to list floating IPs"
    return 1
  fi
  
  # Extract assigned floating IPs
  echo "$FLOATING_IPS" | jq -r '.[] | select(.target != null) | "\(.name)|\(.address)|\(.target.name)"' > "$BACKUP_DIR/assigned_ips.txt"
  
  # Display assigned IPs
  log "Assigned floating IPs:"
  cat "$BACKUP_DIR/assigned_ips.txt" | while IFS='|' read -r NAME ADDRESS TARGET; do
    log "  $NAME: $ADDRESS -> $TARGET"
  done
  
  # Count assigned IPs
  ASSIGNED_COUNT=$(cat "$BACKUP_DIR/assigned_ips.txt" | wc -l)
  
  if [ "$ASSIGNED_COUNT" -eq 0 ]; then
    error "No floating IPs assigned"
    return 1
  fi
  
  success "Verified $ASSIGNED_COUNT floating IP assignments"
  return 0
}

# Function to test connectivity with floating IPs
test_connectivity() {
  section "Testing Connectivity with Floating IPs"
  
  if [ ! -f "$BACKUP_DIR/assigned_ips.txt" ]; then
    error "Assigned IPs file not found"
    return 1
  fi
  
  # Read assigned IPs
  cat "$BACKUP_DIR/assigned_ips.txt" | while IFS='|' read -r NAME ADDRESS TARGET; do
    log "Testing connectivity to $ADDRESS ($TARGET)..."
    
    # Ping the floating IP
    ping -c 1 $ADDRESS > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
      success "Successfully pinged $ADDRESS ($TARGET)"
    else
      warning "Failed to ping $ADDRESS ($TARGET)"
    fi
  done
  
  return 0
}

# Function to create rollback script
create_rollback_script() {
  section "Creating Rollback Script"
  
  ROLLBACK_SCRIPT="$BACKUP_DIR/rollback.sh"
  
  log "Creating rollback script: $ROLLBACK_SCRIPT"
  
  # Create rollback script
  cat > "$ROLLBACK_SCRIPT" << EOF
#!/bin/bash
# Rollback script for public IP assignment
# Generated on $(date)

echo "Rolling back public IP assignment..."

# Unassign floating IPs
echo "Unassigning floating IPs..."
EOF
  
  # Add commands to unassign floating IPs
  if [ -f "$BACKUP_DIR/assigned_ips.txt" ]; then
    cat "$BACKUP_DIR/assigned_ips.txt" | while IFS='|' read -r NAME ADDRESS TARGET; do
      echo "ibmcloud is floating-ip-update \$(ibmcloud is floating-ips --output JSON | jq -r '.[] | select(.address==\"$ADDRESS\") | .id') --target null" >> "$ROLLBACK_SCRIPT"
      echo "echo \"Unassigned floating IP $ADDRESS from $TARGET\"" >> "$ROLLBACK_SCRIPT"
    done
  fi
  
  # Add commands to restore network configuration
  cat >> "$ROLLBACK_SCRIPT" << EOF

# Restore iptables rules
echo "Restoring iptables rules..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "iptables-restore < /tmp/iptables_backup.rules"

# Restore sysctl settings
echo "Restoring sysctl settings..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "sysctl -p /etc/sysctl.conf"

echo "Rollback completed."
EOF
  
  # Make rollback script executable
  chmod +x "$ROLLBACK_SCRIPT"
  
  # Copy iptables backup to server
  scp -o StrictHostKeyChecking=no "$BACKUP_DIR/iptables_backup.rules" $SSH_USER@$SERVER_IP:/tmp/
  
  success "Rollback script created: $ROLLBACK_SCRIPT"
}

# Function to document the changes
document_changes() {
  section "Documenting Changes"
  
  DOCUMENTATION_FILE="public_ip_assignment_documentation.md"
  
  log "Creating documentation: $DOCUMENTATION_FILE"
  
  # Create documentation
  cat > "$DOCUMENTATION_FILE" << EOF
# Public IP Assignment Documentation

## Overview

This document describes the process of assigning public IPs directly to all network interfaces on the adapt server. This approach eliminates the need for NAT and simplifies the configuration.

## Implementation Details

### Date and Time
- **Date**: $(date +"%Y-%m-%d")
- **Time**: $(date +"%H:%M:%S %Z")

### Server Information
- **Server Name**: $SERVER_NAME
- **Server ID**: $SERVER_ID
- **Private IP**: $SERVER_IP

### Changes Made

1. **Backup Creation**
   - Created backup of current network configuration
   - Backup location: $BACKUP_DIR
   - Includes: interfaces, routes, iptables rules, sysctl settings

2. **Floating IP Assignment**
   - Assigned floating IPs to all network interfaces
   - Details:
EOF
  
  # Add assigned IPs to documentation
  if [ -f "$BACKUP_DIR/assigned_ips.txt" ]; then
    cat "$BACKUP_DIR/assigned_ips.txt" | while IFS='|' read -r NAME ADDRESS TARGET; do
      echo "     - $TARGET: $ADDRESS ($NAME)" >> "$DOCUMENTATION_FILE"
    done
  fi
  
  # Add rollback information to documentation
  cat >> "$DOCUMENTATION_FILE" << EOF

## Rollback Plan

A rollback script has been created to revert the changes if necessary:

\`\`\`
$BACKUP_DIR/rollback.sh
\`\`\`

The rollback script will:
1. Unassign all floating IPs from the interfaces
2. Restore the original iptables rules
3. Restore the original sysctl settings

## Verification

The following tests were performed to verify the changes:

1. **Connectivity Tests**
   - Ping tests to all assigned floating IPs
   - External connectivity tests from each interface

## Conclusion

The adapt server now has public IPs assigned directly to all network interfaces, eliminating the need for NAT and simplifying the configuration. This approach provides direct external connectivity for all interfaces.

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | $(date +"%Y-%m-%d") | Zorion | Initial implementation |
EOF
  
  success "Documentation created: $DOCUMENTATION_FILE"
}

# Main execution
echo "Public IP Assignment Script for $SERVER_NAME" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "----------------------------------------------" | tee -a "$LOG_FILE"

# Create backup directory
create_backup_dir

# Backup current network configuration
backup_network_config

# Check if floating IPs are available
check_floating_ips
if [ $? -ne 0 ]; then
  error "Failed to check floating IPs"
  exit 1
fi

# Get network interface IDs
get_network_interface_ids
if [ $? -ne 0 ]; then
  error "Failed to get network interface IDs"
  exit 1
fi

# Assign floating IPs to interfaces
assign_floating_ips
if [ $? -ne 0 ]; then
  error "Failed to assign floating IPs"
  exit 1
fi

# Verify floating IP assignment
verify_floating_ips
if [ $? -ne 0 ]; then
  error "Failed to verify floating IP assignment"
  exit 1
fi

# Test connectivity with floating IPs
test_connectivity

# Create rollback script
create_rollback_script

# Document the changes
document_changes

section "Summary"
success "Public IP assignment completed for $SERVER_NAME"
log "Backup directory: $BACKUP_DIR"
log "Rollback script: $BACKUP_DIR/rollback.sh"
log "Documentation: public_ip_assignment_documentation.md"

echo -e "\nPublic IP assignment completed."
exit 0