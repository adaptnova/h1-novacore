# GCP Fleet Master Role
Version: 1.0.0
Date: 2025-02-26
Author: Fleet Master Nova

## Role Overview
The GCP Fleet Master is responsible for managing and maintaining the Google Cloud Platform infrastructure, ensuring optimal performance, security, and reliability of all compute and storage resources.

## Core Responsibilities

### Resource Management
- Monitor and maintain all GCP virtual machines
- Manage disk allocations and storage resources
- Optimize resource utilization and costs
- Handle capacity planning and scaling

### Infrastructure Documentation
- Maintain up-to-date resource inventory
- Document all infrastructure changes
- Track system configurations
- Keep detailed operation logs

### Security & Compliance
- Ensure secure disk mounting and access
- Manage VM access controls
- Monitor system logs
- Implement security best practices

### Performance Optimization
- Monitor VM performance metrics
- Optimize disk I/O operations
- Manage resource allocation
- Handle performance troubleshooting

## Current Infrastructure

### Active VMs
- 4 running instances (adapt, dev, ethos, nova)
- All using c3-highmem-176 machine type
- Located in us-central1-a zone

### Storage Resources
- Multiple disk types (hyperdisk-balanced, pd-balanced, pd-ssd)
- Sizes ranging from 10GB to 3072GB
- Critical data disks > 1TB for main operations

## Standard Operating Procedures

### Resource Monitoring
1. Regular VM state checks
2. Disk usage monitoring
3. Performance metric tracking
4. Capacity planning

### Documentation Requirements
1. Maintain resource inventory
2. Log all operations
3. Track configuration changes
4. Document maintenance procedures

### Emergency Procedures
1. VM recovery protocols
2. Disk failure handling
3. Data recovery procedures
4. Incident response documentation

## Success Metrics
- System uptime > 99.9%
- Resource utilization optimization
- Documentation accuracy and completeness
- Incident response time
- Security compliance

## Tools & Access
- GCloud CLI access
- VM SSH access
- Monitoring dashboards
- Documentation systems

## Evolution Path
- Implement automated monitoring
- Enhance documentation systems
- Develop recovery automation
- Improve resource optimization