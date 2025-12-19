# Revised Implementation Plan

## Overview

This document outlines the revised implementation plan for our infrastructure, incorporating the following key changes:

1. Updated directory location (/data-nova/ax/COO/CloudOps)
2. Optimized disk sizing strategy (start small, resize as needed)
3. Consistent zone deployment for all components
4. Simplified network architecture separate from Project Tapestry

## Current Infrastructure Status

- We have a VPC called `dataops-vpc` in the IBM Cloud us-south region
- We have a subnet called `dataops-subnet` (10.240.64.0/24) in the us-south-2 zone
- We have one running instance called `adapt3` (to be renamed to `adapt`) in the us-south-default-vpc

## 1. Server Infrastructure

### Server Specifications

#### adapt Server (Existing, to be renamed from adapt3)
- **Profile:** mx3d-96x960 (96 vCPUs, 960GB RAM)
- **Location:** us-south-2 zone, us-south-default-vpc
- **Storage:**
  - Boot volume: 100GB
  - Data volume: 1.5TB (mounted at /data-nova)
- **Network:**
  - Public IP: 52.118.206.209
  - Private IP: 10.240.64.10
- **Purpose:** Primary compute and orchestration server
- **Status:** Active and operational
- **Planned Changes:** 
  - Rename from adapt3 to adapt
  - Include in simplified network architecture
  - Include in centralized logging infrastructure

#### nova-db-primary (MongoDB/PostgreSQL)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD with custom profile (3000 IOPS)
  - Data volume: 50GB NVMe SSD with custom profile (3000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-primary

#### nova-db-graph (Neo4j/ArangoDB)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD with custom profile (3000 IOPS)
  - Data volume: 40GB NVMe SSD with custom profile (3000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-graph

#### nova-db-timeseries (Redis/DragonflyDB)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD with custom profile (2000 IOPS)
  - Data volume: 30GB NVMe SSD with custom profile (2000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD with custom profile (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-db-timeseries

#### ethos (GPU Server)
- **Profile:** gx3-48x240x2l40s (48 vCPUs, 240GB RAM, 2x L40S GPUs)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD with custom profile (5000 IOPS)
  - Data volume: 100GB NVMe SSD with custom profile (10000 IOPS), formatted as XFS
  - Log volume: 20GB NVMe SSD with custom profile (2000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** ethos

#### nova-logs (Logging Server)
- **Profile:** bx2-4x16 (4 vCPUs, 16GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD with custom profile (2000 IOPS)
  - Log volume: 100GB NVMe SSD with custom profile (5000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Name:** nova-logs

## 2. Disk Scaling Strategy

All disks will follow the same scaling strategy:

1. **Start Small**
   - Begin with minimal sizes that meet immediate needs
   - Boot volumes: 50GB
   - Data volumes: Sized according to initial requirements
   - Log volumes: 10-20GB based on expected log volume

2. **Monitor Usage**
   - Implement monitoring for disk usage
   - Set alerts at 70% utilization
   - Track growth rates to predict future needs

3. **Resize as Needed**
   - Use LVM for online expansion capability
   - Expand volumes in increments based on growth patterns
   - Maintain 30% free space as buffer

4. **Optimization Process**
   ```
   1. Monitor disk usage trends
   2. When 70% threshold is reached:
      a. Evaluate actual usage patterns
      b. Calculate appropriate size increase
      c. Schedule expansion during low-usage period
      d. Expand LVM volume
      e. Resize filesystem
      f. Verify performance after expansion
   ```

## 3. Network Architecture

Instead of immediately implementing Project Tapestry's 14-network mesh, we will start with a simplified network architecture:

1. **Single VPC Architecture**
   - Use existing dataops-vpc
   - All servers in the same us-south-2 zone
   - Single subnet (dataops-subnet) for all servers

2. **Security Groups**
   - `nova-db-sg`: For database servers
   - `ethos-sg`: For GPU server
   - `nova-logs-sg`: For logging server
   - `adapt-sg`: For adapt server

3. **Network Connectivity**
   - Direct connectivity between all servers within the subnet
   - Optimized routing within the zone
   - Firewall rules to control traffic between servers

4. **Future Integration with Tapestry**
   - Design the simplified network to allow future integration
   - Document connection points for future mesh implementation
   - Maintain compatibility with Tapestry architecture

## 4. Implementation Steps

### Phase 1: Infrastructure Preparation

1. **Create Security Groups**
   - Create security groups for each server type
   - Configure appropriate rules for each security group
   - Allow necessary traffic between servers

2. **Create Volumes for Each Server**
   - Create boot volumes (50GB) with NVMe SSD using custom profile
   - Create data volumes with NVMe SSD using custom profile
   - Create log volumes with NVMe SSD using custom profile
   - Configure all volumes for future expansion

### Phase 2: Server Deployment

1. **Deploy DataOps Servers**
   - Create the three DataOps instances with the specified profiles, images, and volumes
   - Attach them to the dataops-subnet
   - Apply the nova-db-sg security group

2. **Deploy Ethos GPU Server**
   - Create the Ethos instance with the gx3-48x240x2l40s profile
   - Attach it to the dataops-subnet
   - Apply the ethos-sg security group

3. **Deploy Logging Server**
   - Create the nova-logs instance with the bx2-4x16 profile
   - Attach it to the dataops-subnet
   - Apply the nova-logs-sg security group

4. **Rename adapt3 to adapt**
   - Coordinate with operations team for rename process
   - Update DNS and other references
   - Apply the adapt-sg security group

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
   - Set up local logging with appropriate retention

4. **Configure Ethos GPU Server**
   - Install NVIDIA drivers and CUDA toolkit
   - Configure GPU optimization settings
   - Set up monitoring for GPU utilization
   - Configure data directories on the secondary disk
   - Set up local logging with appropriate retention

5. **Configure Logging Server**
   - Install and configure the ELK stack (Elasticsearch, Logstash, Kibana)
   - Set up log indices and retention policies
   - Configure Prometheus and Grafana for metrics visualization
   - Set up Alertmanager for notifications
   - Create custom dashboards for different server types

### Phase 4: Logging Configuration

1. **Configure Local Logging (Tier 1)**
   - Set up log rotation on all servers
   - Configure appropriate log levels
   - Implement local log retention policies
   - Set up basic log monitoring

2. **Configure Log Forwarding**
   - Install and configure filebeat on all servers
   - Set up secure transport (TLS) for log forwarding
   - Configure log tagging and filtering
   - Implement buffering for resilience to network issues

3. **Configure Centralized Logging (Tier 2)**
   - Set up Elasticsearch indices and mappings
   - Configure Logstash pipelines for different log types
   - Create Kibana dashboards and visualizations
   - Set up alerts for critical events

4. **Configure Log Archiving (Tier 3)**
   - Set up weekly archive jobs to object storage
   - Configure compression and encryption
   - Implement metadata indexing for archived logs
   - Set up automated cleanup of expired archives

### Phase 5: Snapshot and Backup Setup

1. **Configure Hourly Snapshots**
   - Create a snapshot schedule for hourly snapshots of all disks
   - Set 2-day retention for most snapshots
   - Configure the last snapshot to be kept for 7 days
   - Implement using IBM Cloud snapshot capabilities

2. **Configure Cron Job for Hourly Execution**
   - Set up cron job to run the snapshot script hourly
   - Configure logging for the snapshot process
   - Set up monitoring for snapshot failures

### Phase 6: Monitoring and Alerting

1. **Set Up Monitoring**
   - Configure monitoring for system metrics (CPU, memory, disk, network)
   - Set up GPU-specific monitoring for the Ethos server
   - Set up alerting based on the specified thresholds
   - Configure database-specific monitoring

2. **Configure Disk Usage Monitoring**
   - Set up detailed monitoring for disk usage
   - Configure trending analysis for growth prediction
   - Set alerts at 70% utilization
   - Create automated reports for capacity planning

3. **Configure Log-Based Alerts**
   - Set up alerts for critical log events
   - Configure anomaly detection for unusual log patterns
   - Implement correlation between metrics and log events

### Phase 7: Documentation

1. **Create Infrastructure Documentation**
   - Network diagrams
   - Server specifications
   - Access procedures
   - Backup/restore procedures
   - Snapshot retention policies
   - Logging architecture

2. **Develop Runbooks**
   - Server provisioning
   - Disk expansion
   - Backup and recovery
   - Emergency procedures
   - GPU optimization
   - Log analysis procedures

## 5. Timeline and Sequencing

Given the revised approach, we'll implement the infrastructure in the following sequence:

1. **Day 1:**
   - Create security groups
   - Create volumes for all servers
   - Deploy DataOps servers and Ethos GPU server
   - Deploy nova-logs server

2. **Day 2:**
   - Configure all servers
   - Set up storage with XFS formatting
   - Configure logging infrastructure
   - Configure hourly snapshots with retention policies

3. **Day 3:**
   - Finalize monitoring and backup configurations
   - Complete documentation for all components
   - Conduct final testing and validation
   - Verify logging and analysis capabilities

## 6. Future Expansion

While starting with a simplified approach, we'll maintain the ability to expand in the future:

1. **Disk Expansion**
   - All disks configured with LVM for online expansion
   - Monitoring in place to trigger expansion when needed
   - Documented procedures for expansion process

2. **Network Evolution**
   - Simplified network designed for future integration with Tapestry
   - Documentation of connection points for mesh implementation
   - Ability to gradually migrate to more complex architecture

3. **Server Additions**
   - Infrastructure designed to accommodate additional servers
   - Documented procedures for adding new servers
   - Monitoring and logging ready for expanded environment

4. **Nova Server Addition**
   - Planned for Q2 2025
   - Infrastructure ready for integration
   - Resource planning in place for quota management

## 7. Conclusion

This revised implementation plan provides a more cost-effective and streamlined approach to our infrastructure deployment. By starting with smaller disk sizes, using a simplified network architecture, and maintaining the ability to scale as needed, we can achieve our immediate goals while setting the foundation for future growth.

The plan maintains all the core functionality of the original approach while optimizing resource usage and reducing complexity in the initial deployment.