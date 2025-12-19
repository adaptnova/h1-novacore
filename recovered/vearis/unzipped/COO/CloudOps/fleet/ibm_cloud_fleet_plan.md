# IBM Cloud Fleet Implementation Plan

## Overview

This document outlines the implementation plan for the IBM Cloud Fleet, including the Ethos server and DataOps VMs. The plan includes creating reservations, adding network interfaces, recreating VMs with the ibm-admin key, and setting up the VMs with users, mount points, etc.

## Current Infrastructure

| Server | Profile | Zone | IP Address | Floating IP | Status |
|--------|---------|------|------------|-------------|--------|
| ethos | gx3-48x240x2l40s | us-south-1 | 10.240.0.15 | 52.118.146.160 | Running |
| dataops-primary | bx2-8x32 | us-south-1 | 10.240.0.6 | - | Running |
| dataops-timeseries | bx2-8x32 | us-south-1 | 10.240.0.17 | - | Being recreated |
| dataops-vector | bx2-8x32 | us-south-1 | 10.240.0.7 | - | Being recreated |

## Implementation Steps

### 1. Create Reservations

Create individual 3-year reservations with monthly payment for each server:

- Ethos server (gx3-48x240x2l40s)
- dataops-primary (bx2-8x32)
- dataops-timeseries (bx2-8x32)
- dataops-vector (bx2-8x32)

Each reservation will have:
- Capacity: 1
- Term: 3 years
- Affinity policy: automatic
- Expiration policy: renew

### 2. Add Network Interfaces to Ethos Server

Add 3 additional network interfaces to the Ethos server (for a total of 4):

- eth0 (primary, already exists)
- eth1 (new)
- eth2 (new)
- eth3 (new)

Each network interface will have a floating IP assigned to it.

### 3. Recreate DataOps VMs

Recreate each DataOps VM with the ibm-admin key:

1. Stop the VM
2. Detach volumes
3. Delete the VM
4. Create a new VM with the same name, profile, and the ibm-admin key
5. Attach the original volumes

### 4. Set Up DataOps VMs

For each DataOps VM:

1. Add 3 additional network interfaces (for a total of 4)
2. Assign floating IPs to all network interfaces
3. Format and mount volumes:
   - /dev/vdd as /data
   - /dev/vde as /backup
4. Create users:
   - x (with sudo NOPASSWD)
   - vertex (with sudo NOPASSWD)
5. Configure SSH access

## Network Configuration

Each server will have 4 network interfaces, each with a floating IP:

- eth0: Primary interface for management
- eth1: Secondary interface for data transfer
- eth2: Tertiary interface for backup
- eth3: Quaternary interface for monitoring

## User Configuration

Each server will have the following users:

- root (SSH key authentication)
- x (password: x, sudo NOPASSWD)
- ethos/vertex (password: x, sudo NOPASSWD)

## SSH Configuration

SSH config entries will be created for each server and user:

- ethos-root, dataops-primary-root, dataops-timeseries-root, dataops-vector-root (root access)
- ethos, dataops-primary, dataops-timeseries, dataops-vector (ethos/vertex user access)
- ethos-x, dataops-primary-x, dataops-timeseries-x, dataops-vector-x (x user access)

## Future Considerations

### Dedicated Hosts

As the infrastructure scales, dedicated hosts may be considered for:

- Consistent performance
- Physical isolation
- Control over VM placement
- Potential cost savings at scale

See dedicated_vs_regular_instances.md for a detailed comparison.

### Additional VMs

Additional VMs may be added to the fleet in the future:

- adapt: Purpose and specifications to be determined
- nova: Purpose and specifications to be determined

## Scripts

The following scripts have been created to implement this plan:

- ibm_cloud_fleet_setup.sh: Main script to orchestrate the setup process
- create_reservations.sh: Create reservations for all servers
- add_ethos_network_interfaces.sh: Add network interfaces to the Ethos server
- recreate_dataops_vms.sh: Recreate DataOps VMs with the ibm-admin key
- setup_dataops_vms.sh: Set up DataOps VMs with users, mount points, etc.