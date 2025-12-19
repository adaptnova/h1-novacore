# Comprehensive Implementation Plan (Revised)

## Overview

This document outlines the detailed implementation plan for:
1. DataOps Server Infrastructure (Phase 1 of Nova Database Evolution)
2. "Ethos" GPU Server Deployment
3. Project Tapestry Implementation

All infrastructure will be deployed in the IBM Cloud us-south-2 zone (Dallas 2).

## Current Infrastructure Status

- We have a VPC called `dataops-vpc` in the IBM Cloud us-south region
- We have a subnet called `dataops-subnet` (10.240.64.0/24) in the us-south-2 zone
- We have one running instance called `adapt3` (mx3d-96x960) in the us-south-default-vpc

## 1. DataOps Server Infrastructure

### Server Specifications

#### Server 1: Primary Database (MongoDB/PostgreSQL)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image:** ibm-ubuntu-22-04-5-minimal-amd64-2
- **Storage:** 
  - Boot volume: 100GB NVMe SSD with custom profile (3000 IOPS)
  - Data volume: 100GB NVMe SSD with custom profile (3000 IOPS), formatted as XFS
  - Backup volume: 200GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-primary

#### Server 2: Vector/Graph Database (Neo4j/ArangoDB)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image:** ibm-ubuntu-22-04-5-minimal-amd64-2
- **Storage:** 
  - Boot volume: 100GB NVMe SSD with custom profile (3000 IOPS)
  - Data volume: 80GB NVMe SSD with custom profile (3000 IOPS), formatted as XFS
  - Backup volume: 160GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-graph

#### Server 3: Time-Series/Cache (Redis/DragonflyDB)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image:** ibm-ubuntu-22-04-5-minimal-amd64-2
- **Storage:** 
  - Boot volume: 100GB NVMe SSD with custom profile (2000 IOPS)
  - Data volume: 60GB NVMe SSD with custom profile (2000 IOPS), formatted as XFS
  - Backup volume: 120GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-timeseries

## 2. "Ethos" GPU Server

#### Server 4: Ethos (GPU Server)
- **Profile:** gx3-48x240x2l40s (48 vCPUs, 240GB RAM, 2x L40S GPUs)
- **Image:** ibm-ubuntu-22-04-5-minimal-amd64-2
- **Storage:** 
  - Boot volume: 100GB NVMe SSD with custom profile (5000 IOPS)
  - Data volume: 500GB NVMe SSD with custom profile (10000 IOPS), formatted as XFS
  - Backup volume: 200GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** ethos

## 3. Implementation Steps

### Phase 1: Infrastructure Preparation

1. **Create Placement Group**
   - Create a placement group with host_spread strategy
   - Name it `dataops-placement-group`
   - This will ensure servers are placed on different hosts for better performance and availability

2. **Create Instance Group**
   - Create an instance group for the DataOps servers
   - Configure autoscaling policies based on CPU utilization
   - Set minimum and maximum instance counts

3. **Create Security Group for Database Servers**
   - Create a security group called `nova-db-sg` in the dataops-vpc
   - Configure rules to allow traffic only on required database ports between servers
   - Allow SSH access from the adapt3 instance

4. **Create Security Group for GPU Server**
   - Create a security group called `ethos-sg` in the dataops-vpc
   - Configure rules to allow necessary traffic for GPU workloads
   - Allow SSH access from the adapt3 instance

5. **Create Volumes for Each Server**
   - Create boot volumes (100GB) with NVMe SSD using custom profile
   - Create data volumes with NVMe SSD using custom profile
   - Create backup volumes with NVMe SSD using custom profile

### Phase 2: Server Deployment

1. **Deploy DataOps Servers**
   - Create the three DataOps instances with the specified profiles, images, and volumes
   - Attach them to the dataops-subnet
   - Apply the nova-db-sg security group
   - Add them to the placement group for optimal network performance
   - Add them to the instance group for autoscaling

2. **Deploy Ethos GPU Server**
   - Create the Ethos instance with the gx3-48x240x2l40s profile
   - Attach it to the dataops-subnet
   - Apply the ethos-sg security group
   - Add it to the placement group for optimal network performance

### Phase 3: Server Configuration

1. **Configure User Access**
   - Set up SSH access with key-based authentication
   - Create sudo users (synaptic, forge, x, vertex) with password "x" and NOPASSWD sudo privileges on all servers

2. **Configure Storage**
   - Format all secondary disks with XFS filesystem
   - Configure mount options (noatime,nodiratime) for performance optimization
   - Set up LVM for online expansion capability
   - Configure fstab for automatic mounting on reboot
   - Offload all data operations to secondary disks, keeping boot disks clean

3. **Configure DataOps Servers**
   - Install and configure database software on secondary disks
   - Set up database-specific optimizations
   - Configure data directories on secondary disks

4. **Configure Ethos GPU Server**
   - Install NVIDIA drivers and CUDA toolkit
   - Configure GPU optimization settings
   - Set up monitoring for GPU utilization
   - Configure data directories on the 500GB secondary disk

### Phase 4: Snapshot and Backup Setup

1. **Configure Hourly Snapshots**
   - Create a snapshot schedule for hourly snapshots of all disks
   - Set 2-day retention for most snapshots
   - Configure the last snapshot to be kept for 7 days
   - Implement using IBM Cloud snapshot capabilities

2. **Set Up Backup Script**
   ```bash
   #!/bin/bash
   # Hourly snapshot script with retention policy
   
   # Variables
   DATE=$(date +%Y%m%d_%H%M%S)
   RETENTION_HOURS=48  # 2 days
   EXTENDED_RETENTION_HOURS=168  # 7 days for last snapshot
   
   # Function to create snapshot
   create_snapshot() {
     VOLUME_ID=$1
     VOLUME_NAME=$2
     
     # Create snapshot
     SNAPSHOT_ID=$(ibmcloud is snapshot-create --name "${VOLUME_NAME}-${DATE}" --volume $VOLUME_ID --output JSON | jq -r '.id')
     
     echo "Created snapshot ${SNAPSHOT_ID} for volume ${VOLUME_NAME}"
     
     # Tag last snapshot for extended retention
     SNAPSHOTS=$(ibmcloud is snapshots --volume $VOLUME_ID --output JSON | jq -r '.[] | select(.name | startswith("'${VOLUME_NAME}'")) | .id')
     LAST_SNAPSHOT=$(echo "$SNAPSHOTS" | tail -n 1)
     
     if [ "$SNAPSHOT_ID" = "$LAST_SNAPSHOT" ]; then
       # Tag for extended retention
       ibmcloud is snapshot-update $SNAPSHOT_ID --user-tags "retention:extended"
       echo "Tagged snapshot ${SNAPSHOT_ID} for extended retention (${EXTENDED_RETENTION_HOURS} hours)"
     fi
   }
   
   # Function to clean up old snapshots
   cleanup_snapshots() {
     VOLUME_ID=$1
     CURRENT_TIME=$(date +%s)
     
     # Get all snapshots for this volume
     SNAPSHOTS=$(ibmcloud is snapshots --volume $VOLUME_ID --output JSON)
     
     echo "$SNAPSHOTS" | jq -c '.[]' | while read -r SNAPSHOT; do
       SNAPSHOT_ID=$(echo $SNAPSHOT | jq -r '.id')
       SNAPSHOT_TIME=$(echo $SNAPSHOT | jq -r '.created_at')
       SNAPSHOT_EPOCH=$(date -d "$SNAPSHOT_TIME" +%s)
       SNAPSHOT_AGE_HOURS=$(( (CURRENT_TIME - SNAPSHOT_EPOCH) / 3600 ))
       
       # Check if snapshot has extended retention tag
       HAS_EXTENDED_TAG=$(echo $SNAPSHOT | jq -r '.user_tags | contains(["retention:extended"])')
       
       if [ "$HAS_EXTENDED_TAG" = "true" ]; then
         # Use extended retention for tagged snapshots
         if [ $SNAPSHOT_AGE_HOURS -gt $EXTENDED_RETENTION_HOURS ]; then
           echo "Deleting snapshot ${SNAPSHOT_ID} (age: ${SNAPSHOT_AGE_HOURS} hours, extended retention expired)"
           ibmcloud is snapshot-delete $SNAPSHOT_ID --force
         fi
       else
         # Use standard retention
         if [ $SNAPSHOT_AGE_HOURS -gt $RETENTION_HOURS ]; then
           echo "Deleting snapshot ${SNAPSHOT_ID} (age: ${SNAPSHOT_AGE_HOURS} hours, standard retention expired)"
           ibmcloud is snapshot-delete $SNAPSHOT_ID --force
         fi
       fi
     done
   }
   
   # Main execution
   # Get all volumes
   VOLUMES=$(ibmcloud is volumes --output JSON | jq -r '.[] | "\(.id) \(.name)"')
   
   # Process each volume
   echo "$VOLUMES" | while read -r VOLUME_INFO; do
     VOLUME_ID=$(echo $VOLUME_INFO | cut -d' ' -f1)
     VOLUME_NAME=$(echo $VOLUME_INFO | cut -d' ' -f2-)
     
     # Create snapshot
     create_snapshot "$VOLUME_ID" "$VOLUME_NAME"
     
     # Clean up old snapshots
     cleanup_snapshots "$VOLUME_ID"
   done
   ```

3. **Configure Cron Job for Hourly Execution**
   - Set up cron job to run the snapshot script hourly
   - Configure logging for the snapshot process
   - Set up monitoring for snapshot failures

### Phase 5: Monitoring and Alerting

1. **Set Up Monitoring**
   - Configure monitoring for system metrics (CPU, memory, disk, network)
   - Set up GPU-specific monitoring for the Ethos server
   - Set up alerting based on the specified thresholds
   - Configure database-specific monitoring

2. **Configure Autoscaling Alerts**
   - Set up alerts for autoscaling events
   - Configure notifications for scale-up and scale-down events
   - Implement monitoring for instance group health

### Phase 6: Documentation

1. **Create Infrastructure Documentation**
   - Network diagrams
   - Server specifications
   - Access procedures
   - Backup/restore procedures
   - Snapshot retention policies

2. **Develop Runbooks**
   - Server provisioning
   - Disk expansion
   - Backup and recovery
   - Emergency procedures
   - GPU optimization
   - Autoscaling management

## 4. Project Tapestry Implementation (8-hour timeline)

### Phase 1: Design and Documentation (1.5 hours)

1. **Network Architecture Design**
   - Design the 14-network mesh with full peering
   - Define IP address ranges for each network
   - Create network topology diagrams
   - Incorporate placement groups for optimal performance

2. **NIC Configuration Specifications**
   - Define driver parameters for optimization
   - Specify TCP/IP stack settings
   - Create IRQ affinity mapping
   - Design NUMA optimization approach

3. **VM Configuration Templates**
   - Create templates for each workload type (NovaOps, MLOps, DataOps, etc.)
   - Define resource allocations for each template
   - Specify storage configurations with NVMe disks
   - Configure autoscaling parameters

4. **Automation Script Development**
   - Develop scripts for network creation and peering
   - Create scripts for NIC configuration
   - Develop VM provisioning scripts
   - Implement snapshot automation scripts

### Phase 2: Prototype and Testing (2 hours)

1. **Network Prototype**
   - Create a subset of the networks (3-4) for testing
   - Implement peering between test networks
   - Validate bandwidth multiplication
   - Test placement group performance

2. **NIC Configuration Testing**
   - Test driver optimizations on a sample VM
   - Validate TCP/IP stack settings
   - Measure performance improvements
   - Test network performance between servers in the placement group

3. **VM Configuration Validation**
   - Deploy test VMs for key workload types
   - Validate resource allocations
   - Test performance under load
   - Verify autoscaling functionality

4. **Performance Measurement**
   - Measure actual vs. theoretical bandwidth
   - Test latency between networks
   - Validate CPU overhead reduction
   - Benchmark NVMe disk performance

### Phase 3: Implementation (3 hours)

1. **Full Network Deployment**
   - Create all 14 networks with jumbo frame support
   - Implement full mesh peering
   - Configure routing between networks
   - Set up placement groups across networks

2. **VM Deployment**
   - Deploy production VMs for each workload type
   - Apply optimized NIC configurations
   - Configure storage with NVMe disks
   - Set up instance groups with autoscaling

3. **Integration with Existing Infrastructure**
   - Connect to existing services and systems
   - Migrate workloads to new infrastructure
   - Update DNS and routing configurations
   - Integrate with DataOps and Ethos servers

4. **Security Implementation**
   - Configure security groups and network ACLs
   - Implement encryption for data in transit
   - Set up access controls
   - Configure secure snapshot access

### Phase 4: Initial Optimization (1.5 hours)

1. **Performance Monitoring**
   - Set up comprehensive monitoring for all components
   - Configure alerting for performance thresholds
   - Implement logging for troubleshooting
   - Set up snapshot monitoring

2. **Performance Tuning**
   - Identify and address performance bottlenecks
   - Fine-tune NIC configurations based on real-world performance
   - Optimize VM resource allocations
   - Adjust autoscaling parameters based on initial performance

3. **Documentation Finalization**
   - Complete all technical documentation
   - Create operational runbooks
   - Develop troubleshooting guides
   - Document snapshot and backup procedures

4. **Handover and Training**
   - Provide knowledge transfer to operations team
   - Conduct training sessions on the new infrastructure
   - Establish ongoing support processes
   - Train team on autoscaling management

## 5. Integration Between Projects

The DataOps servers and Ethos GPU server will be integrated with the Project Tapestry infrastructure to ensure optimal performance and connectivity:

1. **Network Integration**
   - Connect all servers to the Tapestry mesh network
   - Optimize routing between servers using placement groups
   - Implement advanced NIC configurations on all servers
   - Configure autoscaling to maintain network performance

2. **Performance Optimization**
   - Apply NIC optimization techniques from Project Tapestry to all servers
   - Tune database and GPU performance based on the enhanced network capabilities
   - Implement workload-specific optimizations
   - Optimize NVMe disk performance

3. **Monitoring Integration**
   - Incorporate all server monitoring into the Tapestry monitoring framework
   - Create unified dashboards for comprehensive visibility
   - Set up specialized GPU monitoring for the Ethos server
   - Implement snapshot and backup monitoring

4. **Security Alignment**
   - Ensure consistent security policies across all infrastructure
   - Implement end-to-end encryption between components
   - Apply defense-in-depth security principles
   - Secure snapshot access and management

## 6. Timeline and Sequencing

Given the urgent nature of all projects, we'll implement them in parallel with the following sequence:

1. **Day 1 (Today):**
   - Begin DataOps and Ethos server provisioning
   - Create placement groups and instance groups
   - Start Project Tapestry Phase 1 (Design and Documentation)

2. **Day 2:**
   - Complete server configuration
   - Set up NVMe disks with XFS formatting
   - Configure hourly snapshots with retention policies
   - Execute Project Tapestry Phases 2-4 (Prototype, Implementation, Optimization)
   - Integrate all servers with Tapestry infrastructure

3. **Day 3:**
   - Finalize monitoring and backup configurations
   - Complete documentation for all projects
   - Conduct final testing and validation
   - Verify autoscaling functionality

## 7. Risk Management

### Identified Risks and Mitigation Strategies

1. **Resource Contention**
   - **Risk:** Simultaneous implementation of all projects may lead to resource contention
   - **Mitigation:** Prioritize critical components and sequence resource-intensive tasks

2. **Integration Challenges**
   - **Risk:** Integrating all servers with the Tapestry infrastructure may present unforeseen challenges
   - **Mitigation:** Create detailed integration plans and conduct thorough testing

3. **Performance Expectations**
   - **Risk:** Actual performance may not meet theoretical projections
   - **Mitigation:** Set realistic expectations and focus on measurable improvements over baseline

4. **Timeline Pressure**
   - **Risk:** The accelerated timeline for Project Tapestry may lead to implementation issues
   - **Mitigation:** Focus on core functionality first, then enhance with additional optimizations

5. **GPU Availability**
   - **Risk:** L40S GPU availability in the us-south-2 zone may be limited
   - **Mitigation:** Have fallback options for different GPU types or zones if needed

6. **Snapshot Storage Costs**
   - **Risk:** Hourly snapshots may lead to increased storage costs
   - **Mitigation:** Implement strict retention policies and monitor snapshot storage usage

7. **Autoscaling Stability**
   - **Risk:** Autoscaling may lead to instability if not properly configured
   - **Mitigation:** Implement conservative autoscaling policies with appropriate cooldown periods

## 8. Success Criteria

The implementation will be considered successful when:

1. All servers are provisioned and configured according to specifications
2. NVMe disks are properly configured with XFS formatting
3. Hourly snapshots are working with the specified retention policies
4. Project Tapestry is implemented with the 14-network mesh architecture
5. Placement groups and instance groups are properly configured
6. Autoscaling is functioning correctly
7. All monitoring and backup systems are operational
8. Performance metrics meet or exceed the baseline requirements
9. Documentation is complete and comprehensive
10. All sudo users are created with the specified access

## 9. Next Steps

1. Obtain final approval for this implementation plan
2. Begin server provisioning immediately
3. Create placement groups and instance groups
4. Set up NVMe disks with XFS formatting
5. Configure hourly snapshots with retention policies
6. Initiate Project Tapestry design phase
7. Schedule daily status updates during implementation