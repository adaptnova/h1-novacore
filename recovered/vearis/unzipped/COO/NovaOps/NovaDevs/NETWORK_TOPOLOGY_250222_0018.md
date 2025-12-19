# NovaNet Clean Route Architecture
Date: February 22, 2025 00:18 MST
Author: V.I. (Vaeris Intelligence)
Status: DESIGN PROPOSAL

## Overview
Designing clean routes between networks to enable direct access while maintaining high-performance ML workload paths.

## Current Network Topology

### High-Speed Networks (8896 MTU)
1. nova-8896-1-primary
   - CIDR: 10.1.0.0/24
   - Purpose: ML Primary Network
   - Key Instance: ml (10.1.0.51)

2. nova-8896-2-secondary through nova-8896-8-octonary
   - CIDRs: 10.2.0.0/24 through 10.8.0.0/24
   - Purpose: ML Workload Distribution
   - High-bandwidth interconnects

### External Access Networks (1500 MTU)
1. nova-1500-1-primary through nova-1500-4-quaternary
   - Purpose: External Connectivity
   - Internet Access
   - Service Exposure

### ML-Specific Networks (8896 MTU)
1. ethos-net-1 through ethos-net-8
   - Purpose: ML Workload Optimization
   - RDMA Enabled
   - Full Mesh Topology

## Clean Route Design

### Primary Access Path
1. Direct Route to ML:
   ```
   Network: nova-8896-1-primary (10.1.0.0/24)
   Next Hop: Direct
   Priority: 100
   Tags: ml-access
   ```

2. Backup Route:
   ```
   Network: nova-8896-1-primary (10.1.0.0/24)
   Next Hop: via nova-1500-1-primary
   Priority: 200
   Tags: ml-access-backup
   ```

### Network Peering Configuration
1. Primary Peering:
   ```
   Networks: nova-8896-1-primary <-> nova-1500-1-primary
   Export Routes: Custom
   Import Routes: Custom
   MTU: 1500 (auto-adjusted)
   ```

2. Secondary Peerings:
   ```
   Networks: nova-8896-[2-8] <-> nova-1500-[1-4]
   Export Routes: Custom
   Import Routes: Custom
   MTU: 1500 (auto-adjusted)
   ```

### Route Priorities
1. Direct ML Access: 100
2. Backup Paths: 200
3. Default Routes: 1000
4. Custom Routes: 500-999

## Implementation Phases

### Phase 1: Primary Route Setup
1. Create direct route to 10.1.0.0/24
2. Configure network peering
3. Set route priorities
4. Test basic connectivity

### Phase 2: Backup Route Configuration
1. Establish backup paths
2. Configure failover
3. Test failover scenarios
4. Validate recovery

### Phase 3: Route Optimization
1. Fine-tune MTU handling
2. Optimize route priorities
3. Configure QoS policies
4. Monitor performance

## Security Considerations

### Firewall Rules
1. Allow direct SSH access
2. Maintain ML workload isolation
3. Enable monitoring access
4. Control external exposure

### Network Tags
1. ml-access: Direct route access
2. ml-access-backup: Backup route access
3. nova-net: Existing ML tags
4. ethos-net: ML workload tags

## Monitoring & Maintenance

### Metrics to Track
1. Route availability
2. Network latency
3. Path utilization
4. Failover events

### Maintenance Windows
1. Route updates: Off-peak hours
2. Performance tuning: Scheduled maintenance
3. Security updates: Coordinated with team

## Success Criteria
1. Direct SSH access working
2. ML workload performance maintained
3. Clean network paths established
4. Monitoring in place
5. Documentation updated

## Rollback Plan
1. Document all changes
2. Maintain current routes
3. Enable quick restoration
4. Test rollback procedures

## Next Steps
1. Review design with Atlas
2. Schedule implementation
3. Prepare testing plan
4. Update documentation

## Notes
- Design prioritizes clean, maintainable routes
- Focuses on direct access while maintaining ML performance
- Includes backup paths for resilience
- Enables future network expansion