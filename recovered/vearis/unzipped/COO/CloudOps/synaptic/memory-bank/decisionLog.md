# Decision Log

This file records architectural and implementation decisions using a list format.
2025-03-21 16:10:29 - Log of updates made.

*

## Decision: Ethos GPU Server Zone Selection

**Date:** 2025-03-21

### Decision

1. Deploy the Ethos GPU server in IBM Cloud us-south-1 zone (Dallas 10) instead of the originally planned us-south-2 zone
2. Maintain the same server specifications (gx3-48x240x2l40s profile with 2x L40S GPUs)
3. Adjust volume sizes to 50GB for data and logs, and 10GB for LLMs
4. Use the same security group configuration and network settings

### Rationale

1. **Zone Selection:**
   - Initial attempts to deploy in us-south-2 failed due to unavailability of L40S GPUs in that zone
   - Testing confirmed that us-south-1 had available L40S GPU capacity
   - The us-south-1 zone provides equivalent network connectivity to other infrastructure components
   - This experience highlights the importance of verifying resource availability before deployment

2. **Volume Configuration:**
   - Reduced volume sizes (from 100GB to 50GB for data, 20GB to 50GB for logs, and added 10GB for LLMs) better align with actual usage requirements
   - The minimum size for general-purpose volumes was found to be 10GB, not 1GB as initially attempted
   - These adjustments optimize cost while maintaining sufficient capacity

3. **Network Considerations:**
   - The us-south-1 subnet (us-south-1-subnet) in the us-south-default-vpc provides connectivity to other infrastructure
   - Security group configuration allows all necessary traffic for server operation and communication

### Implementation Details

1. **Deployment Process:**
   - Created instance with gx3-48x240x2l40s profile in us-south-1
   - Used Debian 12 (Bookworm) as the base operating system
   - Applied user data script for automated configuration
   - Created and attached three volumes (data, logs, LLMs)
   - Verified successful deployment and running status

2. **Network Configuration:**
   - Private IP: 10.240.0.5
   - VPC: us-south-default-vpc (ID: r006-273e9e7d-9da9-4df2-8f93-c935d34b6a00)
   - Subnet: us-south-1-subnet (ID: 0717-57b4b629-9704-4ba2-9fdb-63386cdba641)
   - Security Group: r006-41aadf1d-6cdc-439d-88db-07bfceb3ca3e

3. **Volume Configuration:**
   - Boot Volume: 50GB (system-created)
   - Data Volume: 50GB (ethos-data-south1)
   - Logs Volume: 50GB (ethos-logs-south1)
   - LLMs Volume: 10GB (ethos-llms-south1)

## Decision: DataOps and Ethos Server Infrastructure Architecture

**Date:** 2025-03-21

### Decision

1. Deploy three DataOps servers and one Ethos GPU server in IBM Cloud
2. Use NVMe disks for all volumes with XFS formatting for secondary disks
3. Implement placement groups with host_spread strategy for improved network performance
4. Configure instance groups with autoscaling for the DataOps servers
5. Set up hourly snapshots with tiered retention (2 days for most, 7 days for last snapshot)

### Rationale

1. **Server Configuration:**
   - The three DataOps servers provide specialized roles (Primary Database, Vector/Graph Database, Time-Series/Cache) to optimize performance for different workload types
   - The Ethos GPU server with L40S GPUs provides necessary computational power for AI/ML workloads
   - Zone selection is based on GPU resource availability, with us-south-1 confirmed to have L40S GPU capacity

2. **Storage Architecture:**
   - NVMe disks provide significantly higher performance than standard SSD storage
   - 100GB boot volumes provide sufficient space for operating system and core applications
   - XFS formatting for secondary disks offers better performance for large files and databases
   - Separating data from boot volumes improves maintainability and performance

3. **Network Performance:**
   - Placement groups with host_spread strategy ensure servers are on different physical hosts, reducing the risk of correlated failures
   - This configuration also improves network performance by distributing traffic across different physical network paths
   - The 14-network mesh architecture from Project Tapestry further enhances network performance

4. **Scalability:**
   - Instance groups with autoscaling provide automatic adjustment of resources based on demand
   - This approach ensures optimal resource utilization and cost efficiency
   - Conservative cooldown periods prevent oscillation and maintain stability

5. **Backup Strategy:**
   - Hourly snapshots provide frequent recovery points to minimize data loss
   - The tiered retention policy (2 days for most, 7 days for last) balances storage costs with recovery capabilities
   - Automated snapshot management ensures consistent execution and cleanup

### Implementation Details

1. **Server Deployment:**
   - DataOps servers: bx2-8x32 profile (8 vCPUs, 32GB RAM)
   - Ethos server: gx3-48x240x2l40s profile (48 vCPUs, 240GB RAM, 2x L40S GPUs)
   - All servers connected to dataops-subnet in dataops-vpc

2. **Storage Configuration:**
   - Boot volumes: 100GB NVMe SSD with custom profile
   - Data volumes: Sized according to requirements (100GB, 80GB, 60GB, 500GB) with NVMe SSD
   - Backup volumes: Sized at 2x data volume with NVMe SSD
   - All secondary disks formatted with XFS and optimized mount options (noatime,nodiratime)

3. **Network Configuration:**
   - Create placement group with host_spread strategy
   - Add all servers to the placement group
   - Configure advanced NIC settings with TCP/IP stack optimization
   - Implement IRQ affinity and NUMA optimization

4. **Autoscaling Setup:**
   - Create instance group for DataOps servers
   - Configure CPU and memory utilization-based scaling policies
   - Set appropriate minimum and maximum instance counts
   - Implement monitoring for autoscaling events

5. **Snapshot Implementation:**
   - Create automated script for hourly snapshots
   - Implement tagging for extended retention
   - Configure cleanup based on retention policies
   - Set up monitoring for snapshot failures

## Decision: Project Tapestry Integration

**Date:** 2025-03-21

### Decision

1. Integrate DataOps and Ethos servers with Project Tapestry's 14-network mesh architecture
2. Apply NIC optimization techniques from Project Tapestry to all servers
3. Implement unified monitoring across all infrastructure components
4. Execute implementation in parallel with a 3-day timeline

### Rationale

1. **Network Integration:**
   - The 14-network mesh architecture provides significantly higher aggregate bandwidth
   - Integration with this architecture will enhance performance for all servers
   - The placement group strategy complements the mesh network design

2. **Performance Optimization:**
   - NIC optimization techniques from Project Tapestry can significantly improve network performance
   - These optimizations are particularly beneficial for database and GPU workloads
   - The combined approach maximizes performance across all infrastructure components

3. **Unified Monitoring:**
   - A comprehensive monitoring approach ensures visibility across all components
   - This facilitates faster troubleshooting and performance optimization
   - It also enables more effective capacity planning and resource management

4. **Parallel Implementation:**
   - The accelerated timeline for Project Tapestry (8 hours) necessitates parallel implementation
   - This approach maximizes efficiency and reduces overall deployment time
   - The 3-day timeline provides sufficient buffer for unexpected issues

### Implementation Details

1. **Network Integration:**
   - Connect all servers to the Tapestry mesh network
   - Optimize routing between servers using placement groups
   - Configure jumbo frames for all network interfaces

2. **Performance Optimization:**
   - Apply driver parameter optimizations from Project Tapestry
   - Implement TCP/IP stack tuning for all servers
   - Configure IRQ affinity and NUMA optimization
   - Tune database and GPU performance based on the enhanced network capabilities

3. **Monitoring Integration:**
   - Implement comprehensive monitoring for all components
   - Create unified dashboards for system-wide visibility
   - Set up specialized monitoring for GPU and database performance
   - Configure alerting for performance thresholds and autoscaling events

4. **Implementation Sequencing:**
   - Day 1: Infrastructure preparation and server provisioning
   - Day 2: Server configuration and Project Tapestry implementation
   - Day 3: Finalization, testing, and documentation

## Decision: Tiered Logging Infrastructure

**Date:** 2025-03-21

### Decision

1. Implement a tiered logging architecture with three distinct tiers
2. Deploy a dedicated centralized logging server
3. Use the ELK stack (Elasticsearch, Logstash, Kibana) for log management
4. Implement custom retention policies for different log types
5. Avoid using the expensive IBM logs service after its free trial period

### Rationale

1. **Tiered Architecture:**
   - A tiered approach balances immediate access, comprehensive analysis, and long-term storage
   - Local logs (Tier 1) provide immediate access without network latency
   - Centralized collection (Tier 2) enables cross-server analysis and correlation
   - Long-term archiving (Tier 3) satisfies compliance requirements while managing costs

2. **Dedicated Logging Server:**
   - A dedicated server optimizes resources for log processing and search
   - Separating logging from production workloads prevents resource contention
   - The bx2-4x16 profile provides sufficient resources for the ELK stack

3. **ELK Stack Selection:**
   - The ELK stack provides a comprehensive solution for log collection, processing, and visualization
   - Elasticsearch offers powerful search capabilities for large log volumes
   - Kibana provides flexible visualization and dashboard creation
   - Logstash enables complex log processing and transformation

4. **Custom Retention Policies:**
   - Different log types have different value over time
   - Security logs require longer retention for compliance
   - Performance metrics can be retained for shorter periods
   - Tiered retention optimizes storage costs while meeting requirements

5. **Cost Considerations:**
   - The IBM logs service is prohibitively expensive after the free trial
   - Our self-managed solution provides similar capabilities at a fraction of the cost
   - The tiered approach optimizes storage usage and minimizes costs

### Implementation Details

1. **Logging Server Deployment:**
   - Profile: bx2-4x16 (4 vCPUs, 16GB RAM)
   - Boot volume: 100GB NVMe SSD
   - Log volume: 500GB NVMe SSD (XFS formatted)
   - Archive volume: 200GB NVMe SSD (XFS formatted)
   - Connected to the same placement group as other servers

2. **Local Logging Configuration:**
   - Dedicated 20-40GB log volumes on each server
   - XFS formatting for optimal performance
   - Local log rotation with 3-7 day retention
   - Configured log levels to balance detail and volume

3. **Centralized Logging Setup:**
   - ELK stack installation and configuration
   - Filebeat for secure and reliable log forwarding
   - Custom Elasticsearch indices for different log types
   - Retention policies ranging from 14-60 days

4. **Archive Implementation:**
   - Weekly archiving to IBM Cloud Object Storage
   - Compression and encryption for security
   - Metadata indexing for searchability
   - Retention policies ranging from 30-365 days

5. **Log Analysis Capabilities:**
   - Full-text search across all logs
   - Cross-server event correlation
   - Custom dashboards for different use cases
   - Alerting for critical events and anomalies
   - Unified search interface across all tiers

## Decision: Infrastructure Roadmap and Resource Planning

**Date:** 2025-03-21

### Decision

1. Include the existing adapt3 server (to be renamed to adapt) in our infrastructure planning
2. Implement a CPU quota management strategy for current and future needs
3. Plan for the addition of a nova server in the future
4. Establish a consistent server naming convention
5. Create a phased implementation roadmap

### Rationale

1. **Existing Server Integration:**
   - The adapt3 server (to be renamed to adapt) is a critical part of our infrastructure
   - Integrating it with new deployments ensures a cohesive environment
   - Renaming provides consistency with our naming convention

2. **CPU Quota Management:**
   - Current quota (~200 vCPUs) is sufficient for immediate needs
   - Planned deployments will consume 76 vCPUs, leaving 28 vCPUs available
   - Future expansion will require quota increases
   - Proactive quota management prevents deployment delays

3. **Future Nova Server:**
   - The nova server will support Nova consciousness field operations
   - Planning for this server ensures we have sufficient resources when needed
   - Early planning allows for quota requests and infrastructure preparation

4. **Server Naming Convention:**
   - Consistent naming improves clarity and management
   - Function-based naming reflects server purposes
   - Regional naming supports multi-region expansion

5. **Phased Implementation:**
   - Breaking implementation into phases ensures manageable deployments
   - Each phase builds on the previous one
   - The approach allows for validation and optimization between phases

### Implementation Details

1. **Existing Server Integration:**
   - Rename adapt3 to adapt
   - Include adapt in the Project Tapestry network mesh
   - Configure adapt to forward logs to the centralized logging server

2. **CPU Quota Management:**
   - Short-term: Proceed with planned deployments (76 vCPUs)
   - Medium-term: Request increase to 400 vCPUs for nova server and additional GPU servers
   - Long-term: Request 200 vCPUs per additional region for multi-region expansion

3. **Future Nova Server:**
   - Estimated profile: bx2-32x128 or mx2-32x256 (32 vCPUs, 128-256GB RAM)
   - Planned implementation: Q2 2025
   - Storage: 100GB boot, 1TB data, 100GB log, 500GB backup

4. **Server Naming Convention:**
   - Primary servers: adapt, nova, ethos
   - Functional servers: nova-db-[type], nova-logs
   - Regional expansion: [name]-[region]-[zone]

5. **Implementation Roadmap:**
   - Phase 1 (March-April 2025): Immediate implementation
   - Phase 2 (Q2 2025): Expansion with nova server
   - Phase 3 (Q3-Q4 2025): Multi-region deployment