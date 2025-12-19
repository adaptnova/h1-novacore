# IBM Cloud Server Network Configuration Template

## Overview

This repository contains a set of scripts for configuring network interfaces and routing on IBM Cloud servers. The template is designed to ensure servers have 8 NICs properly configured with optimal routing and network performance.

Created by: Zorion (IBM Cloud Infrastructure Engineer)  
Date: March 26, 2025

## Features

- Automatically adds network interfaces to reach a total of 8 NICs
- Configures optimal routing for multi-NIC setups
- Optimizes network performance settings
- Handles instance state monitoring (waits for updates to complete)
- Includes SSH connectivity checks
- Provides verification of configuration
- Can be reused for different servers by modifying configuration variables

## Scripts

### Main Script

- **ibm_cloud_server_setup.sh**: Orchestrates the entire process of configuring a server

### Helper Scripts

- **add_nics.sh**: Adds network interfaces to an IBM Cloud instance
- **configure_routing.sh**: Configures routing and optimizes network settings

## Prerequisites

- IBM Cloud CLI installed and configured
- Access to the IBM Cloud account
- SSH access to the target server (for routing configuration)

## Usage

1. Edit the configuration variables at the top of `ibm_cloud_server_setup.sh`:

```bash
# Configuration - Edit these variables for each server
SERVER_NAME="your-server-name"
INSTANCE_ID="your-instance-id"
SSH_USER="root"
PRIMARY_IP="primary-ip-address"
SECURITY_GROUP="security-group-name"

# Network configuration - Edit as needed for different network layouts
# Format: "subnet_cidr:gateway:interface_name:priority"
NETWORKS=(
  "10.x.1.0/24:10.x.1.1:eth0:10"  # Primary network (management)
  "10.x.2.0/24:10.x.2.1:eth1:20"  # Secondary network
  # ... add more networks as needed
)

# Subnets to add (we already have the primary subnet)
SUBNETS=(
  "subnet-name-2"
  "subnet-name-3"
  # ... add more subnets as needed
)
```

2. Make the scripts executable:

```bash
chmod +x *.sh
```

3. Run the main script:

```bash
./ibm_cloud_server_setup.sh
```

## Workflow

1. **Check Prerequisites**: Verifies IBM Cloud CLI installation and login status
2. **Check Instance Status**: Ensures the instance is running and not updating
3. **Check Network Interfaces**: Counts existing interfaces and determines how many to add
4. **Add Network Interfaces**: Adds interfaces if needed to reach a total of 8
5. **Check SSH Connectivity**: Verifies SSH access to the server
6. **Configure Network**: Sets up interfaces and routing on the server
7. **Verify Configuration**: Checks that everything is properly configured

## Handling Special Cases

- If the instance is updating, the script will wait until the update completes
- If SSH connectivity fails, the script will skip the server-side configuration steps
- If the server already has 8 NICs, the script will skip the interface addition steps

## Example Output

```
IBM Cloud Server Network Configuration Template
Server: adapt (0717_ee285094-0683-4f21-a573-ae87022853e9)
Date: Wed Mar 26 12:13:55 MST 2025
----------------------------------------------

=== Checking IBM Cloud CLI ===
✓ IBM Cloud CLI is installed
✓ Already logged in to IBM Cloud

=== Checking Instance Status ===
  Retrieving status for instance adapt (0717_ee285094-0683-4f21-a573-ae87022853e9)
  Instance status: running
  Lifecycle state: updating
! Instance is currently updating (lifecycle: updating)
  Waiting for update to complete...
  Current lifecycle: stable
✓ Instance update completed

=== Checking Current Network Interfaces ===
  Retrieving network interfaces for instance adapt (0717_ee285094-0683-4f21-a573-ae87022853e9)
  Current interface count: 1
! Instance has 1 network interfaces, needs 8
  Need to add 7 network interfaces

=== Adding Network Interfaces ===
  Adding 7 network interfaces to instance adapt (0717_ee285094-0683-4f21-a573-ae87022853e9)
  Adding interface nic-nic2-interface with subnet nic2-subnet...
✓ Added network interface nic-nic2-interface
  Adding interface nic-nic3-interface with subnet nic3-subnet...
✓ Added network interface nic-nic3-interface
  ...
✓ Added all required network interfaces

=== Checking SSH Connectivity ===
  Checking SSH connectivity to 10.240.1.6...
✓ SSH connection successful

=== Configuring Network ===
  Configuring network on instance adapt (10.240.1.6)
  Configuring network interfaces...
  Configuring routing...
  Optimizing network settings...
✓ Network configuration completed

=== Verifying Configuration ===
  Verifying network configuration on instance adapt (10.240.1.6)
  Network Interfaces:
  lo               UNKNOWN        127.0.0.1/8
  eth0             UP             10.240.1.6/24
  eth1             UP             10.240.2.5/24
  eth2             UP             10.240.3.5/24
  eth3             UP             10.240.4.5/24
  eth4             UP             10.240.5.5/24
  eth5             UP             10.240.6.5/24
  eth6             UP             10.240.7.5/24
  eth7             UP             10.240.8.5/24
  ...
✓ Verification completed

=== Summary ===
Server: adapt (0717_ee285094-0683-4f21-a573-ae87022853e9)
Primary IP: 10.240.1.6
Network interfaces: Added 7 to reach 8
SSH connectivity: Available
Network configuration: Completed
Verification: Completed

Configuration template completed.
This template can be reused for other servers by modifying the configuration variables at the top of the script.
```

## Troubleshooting

- **SSH Connection Issues**: Ensure the server is accessible via SSH and that you have the correct credentials
- **Permission Denied**: Make sure you have the necessary permissions in IBM Cloud to modify the instance
- **Network Interface Addition Fails**: Check that the instance is not in an updating state and that the subnets exist
- **Routing Configuration Fails**: Verify that the server has the necessary packages installed (ip, ethtool, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.