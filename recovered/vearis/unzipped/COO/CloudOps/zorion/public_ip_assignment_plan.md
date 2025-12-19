# Public IP Assignment Plan for Adapt Server

## Overview

This document outlines the plan to assign public IPs directly to all network interfaces on the adapt server. This approach will eliminate the need for NAT and simplify the configuration, providing direct external connectivity for all interfaces.

## Current State

The adapt server currently has:
- 8 physical network interfaces (eth0-eth7)
- Only eth7 has external connectivity (can reach 8.8.8.8)
- NAT and IP forwarding configured to use eth7 for external access
- Download speed tests show 0 MB/s across all interfaces

## Proposed Solution

We will assign public floating IPs directly to all network interfaces, which will:
1. Provide direct external connectivity for each interface
2. Eliminate the need for NAT and IP forwarding
3. Simplify the routing configuration
4. Potentially resolve the download speed issues

## Implementation Plan

### Step 1: Backup Current Configuration
- Create a backup directory with timestamp
- Backup network interfaces configuration
- Backup routing table
- Backup iptables rules
- Backup sysctl settings

### Step 2: Check Available Floating IPs
- List available floating IPs in IBM Cloud
- Create additional floating IPs if needed (8 total required)

### Step 3: Get Network Interface IDs
- List network interfaces for the adapt server
- Extract interface IDs and names
- Save to backup directory for reference

### Step 4: Assign Floating IPs to Interfaces
- Assign one floating IP to each network interface
- Document the assignments

### Step 5: Verify Floating IP Assignment
- List assigned floating IPs
- Verify that each interface has a floating IP assigned

### Step 6: Test Connectivity
- Test connectivity to each floating IP
- Test external connectivity from each interface

### Step 7: Create Rollback Script
- Create a script to revert all changes if necessary
- Include commands to unassign floating IPs
- Include commands to restore original configuration

### Step 8: Document Changes
- Create comprehensive documentation of all changes
- Include details of floating IP assignments
- Include verification results
- Include rollback instructions

## Rollback Plan

If any issues are encountered during or after the implementation, the rollback script will:
1. Unassign all floating IPs from the interfaces
2. Restore the original iptables rules
3. Restore the original sysctl settings
4. Restore the original routing configuration

The rollback script will be located in the backup directory and will be executable with a single command.

## Versioning

All files and configurations will be versioned:
- The script is versioned as 1.0.0
- Backups will include timestamps
- Documentation will include version history
- Changes will be tracked in the operations history

## Expected Outcome

After implementation, the adapt server should have:
- 8 network interfaces, each with a public floating IP
- Direct external connectivity for all interfaces
- Simplified routing configuration
- Improved download speeds

## Monitoring and Verification

After implementation, we will:
- Verify connectivity to external destinations from all interfaces
- Run download speed tests from multiple sources
- Monitor network performance
- Document the results

## Conclusion

This plan provides a comprehensive approach to assigning public IPs directly to all network interfaces on the adapt server. The implementation includes proper backup, verification, and rollback procedures to ensure a smooth transition and minimize risk.

The script `assign_public_ips.sh` will execute this plan automatically, with detailed logging and documentation of all changes.