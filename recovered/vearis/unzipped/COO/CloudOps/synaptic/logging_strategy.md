# Logging Strategy for Infrastructure Implementation

## Overview

This document outlines a comprehensive logging strategy for our infrastructure implementation, addressing the need for cost-effective, reliable, and scalable logging without relying on the expensive IBM logs service after its free trial period.

## Recommended Architecture: Tiered Logging System

I recommend a **hybrid approach** that combines centralized and distributed logging in a tiered architecture:

### Tier 1: Local Log Storage

- Each server maintains short-term logs locally (3-7 days)
- Small dedicated partition on each server's data volume (XFS formatted)
- Local log rotation to prevent disk space issues
- Basic local monitoring for immediate issues

### Tier 2: Centralized Log Server

- Dedicated log server with larger storage capacity
- Separate 500GB NVMe disk specifically for logs
- Runs the ELK stack (Elasticsearch, Logstash, Kibana) or Graylog
- Collects important logs from all servers via rsyslog or filebeat
- Implements log compression and intelligent retention policies
- Provides centralized dashboards and alerting

### Tier 3: Long-term Archive

- Weekly rotation of important logs to low-cost object storage
- Compressed and encrypted for security
- Retention based on compliance requirements (30-90 days)
- Automated cleanup of expired archives

## Benefits of This Approach

### Cost Efficiency

- Avoids expensive IBM logging service costs
- Uses existing infrastructure efficiently
- Minimizes storage requirements through tiered retention
- Leverages low-cost object storage for long-term archives

### Performance

- Local logs provide immediate access without network latency
- Dedicated log server optimized for search and analysis
- Minimal impact on production server performance
- Efficient log forwarding with minimal overhead

### Reliability

- No single point of failure for recent logs
- Redundancy through multiple storage tiers
- Resilient to network issues between servers
- Critical logs preserved even if central server fails

### Scalability

- Easy to add new servers to the logging infrastructure
- Can scale the central log server independently
- Flexible retention policies based on log importance
- Horizontal scaling possible for the ELK/Graylog stack

## Implementation Details

### Log Server Specifications

- Instance Type: bx2-4x16 (4 vCPUs, 16GB RAM)
- Boot Volume: 100GB NVMe SSD
- Log Volume: 500GB NVMe SSD (XFS formatted)
- Located in the same placement group as other servers
- Connected to the same network for optimal performance

### Log Forwarding Configuration

- Use rsyslog or filebeat for efficient log forwarding
- Configure appropriate log levels to avoid excessive data
- Implement log tagging for better searchability
- Set up secure transport (TLS) for log forwarding
- Buffering for resilience to network issues

### Monitoring Stack

- ELK Stack (Elasticsearch, Logstash, Kibana) or Graylog
- Prometheus + Grafana for metrics visualization
- Alertmanager for notification system
- Custom dashboards for different server types
- Integration with existing monitoring systems

### Retention Policies

| Log Type | Local Retention | Central Retention | Archive Retention |
|----------|----------------|-------------------|-------------------|
| System Logs | 7 days | 30 days | 90 days |
| Application Logs | 3 days | 14 days | 60 days |
| Security Logs | 7 days | 60 days | 1 year |
| Performance Metrics | 2 days | 14 days | 30 days |
| Database Logs | 3 days | 30 days | 90 days |
| GPU Performance Logs | 2 days | 14 days | 30 days |

### Log Categories and Priorities

#### High Priority (Always Forwarded)
- Authentication events
- System errors
- Security-related events
- Critical application errors
- Database errors
- GPU errors (for Ethos server)

#### Medium Priority (Selectively Forwarded)
- Warning-level messages
- Performance metrics
- Application state changes
- Database performance metrics
- GPU performance metrics

#### Low Priority (Locally Stored Only)
- Debug information
- Verbose application logs
- Routine operations
- Successful transactions
- Regular health checks

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  nova-db-primary │     │  nova-db-graph  │     │nova-db-timeseries│     │      ethos      │
│                 │     │                 │     │                 │     │                 │
│  Local Logs     │     │  Local Logs     │     │  Local Logs     │     │  Local Logs     │
│  (Tier 1)       │     │  (Tier 1)       │     │  (Tier 1)       │     │  (Tier 1)       │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                Log Forwarding (rsyslog/filebeat)                        │
│                                                                                         │
└───────────────────────────────────────┬─────────────────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                  Centralized Log Server                                 │
│                                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐                   │
│  │                 │     │                 │     │                 │                   │
│  │  Elasticsearch  │     │    Logstash     │     │     Kibana      │                   │
│  │                 │     │                 │     │                 │                   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘                   │
│                                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐                   │
│  │                 │     │                 │     │                 │                   │
│  │   Prometheus    │     │     Grafana     │     │  Alertmanager   │                   │
│  │                 │     │                 │     │                 │                   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘                   │
│                                                                                         │
│                              500GB NVMe Log Volume                                      │
│                                  (Tier 2)                                               │
└───────────────────────────────────────┬─────────────────────────────────────────────────┘
                                        │
                                        │ Weekly Archive
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                             Long-term Archive Storage                                   │
│                                                                                         │
│                       Compressed, Encrypted Log Archives                                │
│                                  (Tier 3)                                               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Steps

1. **Initial Setup**
   - Provision the log server with appropriate volumes
   - Configure XFS partitions for log storage on all servers
   - Install and configure the ELK/Graylog stack on the log server

2. **Log Forwarding Configuration**
   - Install and configure rsyslog/filebeat on all servers
   - Set up log rotation and retention policies
   - Configure secure transport for log forwarding

3. **Monitoring and Alerting**
   - Set up Prometheus and Grafana for metrics visualization
   - Configure Alertmanager for notifications
   - Create custom dashboards for different server types

4. **Archive System**
   - Set up weekly archive jobs to object storage
   - Configure compression and encryption
   - Implement automated cleanup of expired archives

5. **Testing and Validation**
   - Verify log collection from all servers
   - Test search and analysis capabilities
   - Validate alerting functionality
   - Confirm archive and retrieval processes

## Cost Comparison

| Solution | Monthly Cost (Estimated) | Setup Complexity | Maintenance Effort |
|----------|--------------------------|------------------|-------------------|
| IBM Logs Service | $2,000-$5,000 | Low | Low |
| Proposed Tiered Logging | $200-$300 | Medium | Medium |
| Fully Distributed Logging | $100-$150 | High | High |
| Fully Centralized Logging | $300-$400 | Medium | Medium |

The proposed tiered logging approach offers the best balance of cost, reliability, and maintenance effort.

## Conclusion

This tiered logging strategy provides a cost-effective, reliable, and scalable solution for our infrastructure implementation. By combining local storage, centralized collection, and long-term archiving, we can meet all logging requirements without relying on expensive third-party services while maintaining high availability and performance.