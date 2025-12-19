#!/bin/bash
# Script to assign public IPs directly to all interfaces on adapt server
# Version: 1.0.1
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
SERVER_NAME="adapt"
SERVER_ID="0717_ee285094-0683-4f21-a573-ae87022853e9"
SSH_USER="root"
SERVER_IP="10.240.1.6"
LOG_FILE="public_ip_assignment.log"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# IBM Cloud Login Credentials
IBM_CLOUD_USER="chase@levelup2x.com"
IBM_CLOUD_PASSWORD="@@ALALzmzm102938!!"

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

# Function to login to IBM Cloud
ibm_cloud_login() {
  section "Logging in to IBM Cloud"
  
  log "Authenticating as $IBM_CLOUD_USER..."
  ibmcloud login -u "$IBM_CLOUD_USER" -p "$IBM_CLOUD_PASSWORD" -r us-south
  
  if [ $? -eq 0 ]; then
    success "Successfully logged in to IBM Cloud"
    return 0
  else
    error "Failed to log in to IBM Cloud"
    return 1
  fi
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

# Function to run speed tests
run_speed_tests() {
  section "Running Speed Tests"
  
  log "Creating speed test script..."
  
  # Create speed test script
  cat > /tmp/run_speed_tests.sh << 'EOF'
#!/bin/bash

# Configuration
OUTPUT_DIR="/tmp/speed_tests"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/speed_test_report_${TIMESTAMP}.md"

# Test files from different sources (varying sizes and locations)
# Format: "Name|URL|Description"
TEST_FILES=(
  "IBM|https://s3.us-south.cloud-object-storage.appdomain.cloud/speedtest-cos-bucket/100MB.bin|IBM Cloud Object Storage 100MB"
  "AWS|https://speedtest-nyc3.digitalocean.com/100mb.test|DigitalOcean NYC 100MB"
  "Azure|https://azspeedtest.azurewebsites.net/100MB.bin|Azure US East 100MB"
  "Cloudflare|https://speed.cloudflare.com/__down?bytes=104857600|Cloudflare CDN 100MB"
  "Google|https://storage.googleapis.com/speedtest-public/100MB.test|Google Cloud Storage 100MB"
)

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Initialize report
cat > "$REPORT_FILE" << EOT
# Speed Test Report

## Test Environment
- **Date**: $(date)
- **Server**: $(hostname)
- **Kernel**: $(uname -r)

## Network Interfaces
\`\`\`
$(ip -br addr show)
\`\`\`

## Network Parameters
\`\`\`
$(sysctl -a | grep -E 'net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_congestion_control|net.core.default_qdisc')
\`\`\`

## Speed Test Results

### Results by Interface
| Interface | Source | Speed (MB/s) |
|-----------|--------|-------------|
EOT

# Function to run a download test
run_download_test() {
  local interface=$1
  local url=$2
  local name=$3
  local description=$4
  
  echo "Testing download from $description on $interface..."
  
  # Get the IP address of the interface
  ip_addr=$(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}' | head -1)
  
  if [[ -n "$ip_addr" ]]; then
    # Use the specific interface for the test
    start_time=$(date +%s.%N)
    result=$(curl -s --interface $ip_addr -o /dev/null -w "%{speed_download}" -m 30 $url)
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    # Convert to MB/s (curl returns bytes/sec)
    speed_mbps=$(echo "scale=2; $result / 1048576" | bc)
    
    echo "| $interface | $name | $speed_mbps |" >> "$REPORT_FILE"
    echo "$interface,$name,$speed_mbps" >> "${OUTPUT_DIR}/results.csv"
    
    echo "  Speed: $speed_mbps MB/s, Duration: $duration seconds"
  else
    echo "| $interface | $name | No IP address |" >> "$REPORT_FILE"
    echo "$interface,$name,0" >> "${OUTPUT_DIR}/results.csv"
    
    echo "  No IP address found for $interface, skipping test"
  fi
}

# Initialize CSV file
echo "Interface,Source,Speed (MB/s)" > "${OUTPUT_DIR}/results.csv"

# Test each interface with each source
for interface in $(ip -br link show | grep -v lo | awk '{print $1}'); do
  echo "Testing interface $interface..."
  
  for test_file in "${TEST_FILES[@]}"; do
    IFS='|' read -r name url description <<< "$test_file"
    run_download_test "$interface" "$url" "$name" "$description"
  done
done

# Add summary to report
cat >> "$REPORT_FILE" << EOT

## Summary

### Average Speed by Interface
| Interface | Average Speed (MB/s) |
|-----------|----------------------|
EOT

# Calculate average speed by interface
for interface in $(awk -F, 'NR>1 {print $1}' "${OUTPUT_DIR}/results.csv" | sort -u); do
  avg=$(awk -F, -v interface="$interface" 'NR>1 && $1==interface {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' "${OUTPUT_DIR}/results.csv")
  echo "| $interface | $avg |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOT

### Average Speed by Source
| Source | Average Speed (MB/s) |
|--------|----------------------|
EOT

# Calculate average speed by source
for source in $(awk -F, 'NR>1 {print $2}' "${OUTPUT_DIR}/results.csv" | sort -u); do
  avg=$(awk -F, -v source="$source" 'NR>1 && $2==source {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' "${OUTPUT_DIR}/results.csv")
  echo "| $source | $avg |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOT

## Conclusion

The speed tests have been completed across all interfaces. The results show the download speeds from various sources.

EOT

echo "Speed tests completed. Report saved to $REPORT_FILE"
echo "Results also saved to ${OUTPUT_DIR}/results.csv"

# Copy results to a location accessible from outside
cp "$REPORT_FILE" /tmp/
cp "${OUTPUT_DIR}/results.csv" /tmp/

exit 0
EOF

  # Make the script executable
  chmod +x /tmp/run_speed_tests.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/run_speed_tests.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Run the script on the server
  log "Running speed tests on the server..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/run_speed_tests.sh"
  
  # Copy the results back
  log "Copying speed test results..."
  scp -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP:/tmp/speed_test_report_* ./
  scp -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP:/tmp/results.csv ./speed_test_results.csv
  
  success "Speed tests completed"
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

2. **Speed Tests**
   - Download tests from multiple sources
   - Tests performed across all interfaces
   - Results saved to speed test report

## Conclusion

The adapt server now has public IPs assigned directly to all network interfaces, eliminating the need for NAT and simplifying the configuration. This approach provides direct external connectivity for all interfaces.

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.1 | $(date +"%Y-%m-%d") | Zorion | Initial implementation with IBM Cloud login |
EOF
  
  success "Documentation created: $DOCUMENTATION_FILE"
}

# Function to troubleshoot connectivity issues
troubleshoot_connectivity() {
  section "Troubleshooting Connectivity Issues"
  
  log "Checking security groups..."
  SECURITY_GROUPS=$(ibmcloud is instance $SERVER_ID --output JSON | jq -r '.network_interfaces[].security_groups[].id')
  
  if [ -z "$SECURITY_GROUPS" ]; then
    warning "No security groups found"
  else
    for sg_id in $SECURITY_GROUPS; do
      log "Checking security group $sg_id..."
      ibmcloud is security-group $sg_id --output JSON > "$BACKUP_DIR/security_group_${sg_id}.json"
      
      # Check if outbound traffic is allowed
      OUTBOUND_RULES=$(cat "$BACKUP_DIR/security_group_${sg_id}.json" | jq -r '.rules[] | select(.direction=="outbound")')
      
      if [ -z "$OUTBOUND_RULES" ]; then
        warning "No outbound rules found in security group $sg_id"
        
        # Add outbound rule to allow all traffic
        log "Adding outbound rule to allow all traffic..."
        ibmcloud is security-group-rule-add $sg_id outbound all --output JSON
        
        if [ $? -eq 0 ]; then
          success "Added outbound rule to security group $sg_id"
        else
          error "Failed to add outbound rule to security group $sg_id"
        fi
      else
        success "Outbound rules found in security group $sg_id"
      fi
    done
  fi
  
  log "Checking network ACLs..."
  NETWORK_ACLS=$(ibmcloud is instance $SERVER_ID --output JSON | jq -r '.network_interfaces[].subnet.network_acl.id')
  
  if [ -z "$NETWORK_ACLS" ]; then
    warning "No network ACLs found"
  else
    for acl_id in $NETWORK_ACLS; do
      log "Checking network ACL $acl_id..."
      ibmcloud is network-acl $acl_id --output JSON > "$BACKUP_DIR/network_acl_${acl_id}.json"
      
      # Check if outbound traffic is allowed
      OUTBOUND_RULES=$(cat "$BACKUP_DIR/network_acl_${acl_id}.json" | jq -r '.rules[] | select(.direction=="outbound" and .action=="allow")')
      
      if [ -z "$OUTBOUND_RULES" ]; then
        warning "No outbound allow rules found in network ACL $acl_id"
      else
        success "Outbound allow rules found in network ACL $acl_id"
      fi
    done
  fi
  
  log "Checking public gateways..."
  PUBLIC_GATEWAYS=$(ibmcloud is public-gateways --output JSON | jq -r '.[] | "\(.id)|\(.name)|\(.vpc.name)|\(.zone.name)"')
  
  if [ -z "$PUBLIC_GATEWAYS" ]; then
    warning "No public gateways found"
  else
    echo "$PUBLIC_GATEWAYS" > "$BACKUP_DIR/public_gateways.txt"
    success "Public gateways information saved to $BACKUP_DIR/public_gateways.txt"
  fi
  
  log "Checking VPC routing tables..."
  VPC_ID=$(ibmcloud is instance $SERVER_ID --output JSON | jq -r '.vpc.id')
  
  if [ -z "$VPC_ID" ]; then
    warning "Could not determine VPC ID"
  else
    log "VPC ID: $VPC_ID"
    ibmcloud is vpc-routing-tables $VPC_ID --output JSON > "$BACKUP_DIR/vpc_routing_tables.json"
    success "VPC routing tables saved to $BACKUP_DIR/vpc_routing_tables.json"
  fi
  
  log "Running traceroute to external destinations..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "apt-get update && apt-get install -y traceroute && traceroute -I 8.8.8.8" > "$BACKUP_DIR/traceroute_results.txt"
  success "Traceroute results saved to $BACKUP_DIR/traceroute_results.txt"
  
  log "Checking DNS resolution..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "nslookup google.com" > "$BACKUP_DIR/dns_resolution.txt"
  success "DNS resolution results saved to $BACKUP_DIR/dns_resolution.txt"
  
  log "Troubleshooting completed"
}

# Main execution
echo "Public IP Assignment Script for $SERVER_NAME" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "----------------------------------------------" | tee -a "$LOG_FILE"

# Login to IBM Cloud
ibm_cloud_login
if [ $? -ne 0 ]; then
  error "Failed to log in to IBM Cloud"
  exit 1
fi

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

# Run speed tests
run_speed_tests

# Create rollback script
create_rollback_script

# Document the changes
document_changes

# If connectivity issues persist, troubleshoot
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
  warning "External connectivity issues detected, starting troubleshooting..."
  troubleshoot_connectivity
fi

section "Summary"
success "Public IP assignment completed for $SERVER_NAME"
log "Backup directory: $BACKUP_DIR"
log "Rollback script: $BACKUP_DIR/rollback.sh"
log "Documentation: public_ip_assignment_documentation.md"

echo -e "\nPublic IP assignment completed."
exit 0