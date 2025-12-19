# Adapt Platform

## Overview

The Adapt Platform is a comprehensive cloud infrastructure deployed in IBM Cloud to support data operations, GPU computing, and centralized logging. This platform serves as the foundation for Nova's cloud operations and provides the necessary resources for Project Tapestry.

## Infrastructure Components

### Servers

#### adapt (Primary Compute Server)
- **Profile:** mx3d-96x960 (96 vCPUs, 960GB RAM)
- **Location:** us-south-2 zone, us-south-default-vpc
- **Storage:**
  - Boot volume: 100GB
  - Data volume: 1.5TB (mounted at /data-nova)
- **Network:**
  - Public IP: 52.118.206.209
  - Private IP: 10.240.64.10
- **Purpose:** Primary compute and orchestration server
- **Status:** Active and operational (renamed from adapt3)

#### ethos (GPU Server)
- **Profile:** gx3-48x240x2l40s (48 vCPUs, 240GB RAM, 2x L40S GPUs)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD (5000 IOPS)
  - Data volume: 100GB NVMe SSD (10000 IOPS), formatted as XFS
  - Log volume: 20GB NVMe SSD (2000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Purpose:** GPU-accelerated computing
- **Status:** Planned for immediate deployment

#### nova-db-primary (Primary Database Server)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD (3000 IOPS)
  - Data volume: 50GB NVMe SSD (3000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Purpose:** Primary database server (MongoDB/PostgreSQL)
- **Status:** Planned for deployment after ethos

#### nova-db-graph (Graph Database Server)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD (3000 IOPS)
  - Data volume: 40GB NVMe SSD (3000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Purpose:** Vector/graph database server (Neo4j/ArangoDB)
- **Status:** Planned for deployment after ethos

#### nova-db-timeseries (Time-Series Database Server)
- **Profile:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD (2000 IOPS)
  - Data volume: 30GB NVMe SSD (2000 IOPS), formatted as XFS
  - Log volume: 10GB NVMe SSD (1000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Purpose:** Time-series/cache server (Redis/DragonflyDB)
- **Status:** Planned for deployment after ethos

#### nova-logs (Logging Server)
- **Profile:** bx2-4x16 (4 vCPUs, 16GB RAM)
- **Location:** us-south-2 zone, dataops-vpc
- **Storage:** 
  - Boot volume: 50GB NVMe SSD (2000 IOPS)
  - Log volume: 100GB NVMe SSD (5000 IOPS), formatted as XFS
- **Network:** Connected to dataops-subnet
- **Purpose:** Centralized logging and analysis
- **Status:** Planned for deployment after ethos

### Network Architecture

- **VPC:** dataops-vpc
- **Subnet:** dataops-subnet (10.240.64.0/24)
- **Security Groups:**
  - nova-db-sg: For database servers
  - ethos-sg: For GPU server
  - nova-logs-sg: For logging server
  - adapt-sg: For adapt server

### Storage Strategy

All disks follow the same scaling strategy:

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

### Logging Architecture

A tiered logging approach is implemented:

1. **Tier 1: Local Log Storage**
   - Local logs on each server with 7-day retention
   - Configured log levels to balance detail and volume

2. **Tier 2: Centralized Log Server**
   - ELK stack (Elasticsearch, Logstash, Kibana)
   - Prometheus and Grafana for metrics visualization
   - Log indices with 14-60 day retention

3. **Tier 3: Long-term Archive**
   - IBM Cloud Object Storage
   - Compressed and encrypted logs
   - 30-365 day retention based on log type

## Implementation Priority

The implementation will prioritize the GPU server (ethos) first to ensure its availability, followed by the remaining infrastructure components.

## Related Projects

- [Project Tapestry](/projects/tapestry) - Network mesh architecture for enhanced connectivity