# Dedicated vs. Regular Instances in IBM Cloud

## Overview

IBM Cloud offers two primary deployment models for virtual servers:

1. **Regular (Multi-tenant) Instances**: Virtual servers that share physical hardware with other customers
2. **Dedicated Hosts**: Single-tenant physical servers dedicated exclusively to your workloads

This document compares these options to help make informed decisions for the CloudOps Fleet infrastructure.

## Dedicated Hosts

### What are Dedicated Hosts?

Dedicated hosts are physical servers allocated entirely to a single customer. You have exclusive access to all resources on that physical machine, allowing you to deploy multiple VMs on the same host.

### Available Dedicated Host Profiles

IBM Cloud offers several dedicated host profiles, including:

| Profile | vCPUs | Memory (GB) | Storage (GB) | Family |
|---------|-------|-------------|--------------|--------|
| cx3d-host-176x440 | 176 | 440 | 2x3200 | compute |
| bx3d-host-176x880 | 176 | 880 | 2x3200 | balanced |
| mx3d-host-176x1760 | 176 | 1760 | 2x3200 | memory |
| cx2-host-152x304 | 152 | 304 | - | compute |
| bx2-host-152x608 | 152 | 608 | - | balanced |
| mx2-host-152x1216 | 152 | 1216 | - | memory |
| vx2d-host-176x2464 | 176 | 2464 | 2x3200 | very-high-memory |

### Benefits of Dedicated Hosts

1. **Performance**:
   - Consistent performance with no "noisy neighbor" issues
   - Predictable performance for latency-sensitive applications
   - Full access to all physical resources

2. **Security & Compliance**:
   - Physical isolation from other customers' workloads
   - Helps meet strict compliance requirements (HIPAA, PCI DSS, etc.)
   - Reduces potential attack vectors

3. **Control & Flexibility**:
   - Deploy multiple VMs with different profiles on the same host
   - Control VM placement and density
   - Manage maintenance windows

4. **Cost Optimization**:
   - Potential cost savings for high-density deployments
   - Ability to maximize resource utilization

## Cost Comparison

### Regular Instances

- Pay only for the specific instance size you need
- On-demand pricing with hourly or monthly billing
- Reserved instance discounts available (1 or 3 year terms)
- Lower entry cost for smaller workloads

### Dedicated Hosts

- Fixed cost for the entire physical server
- Higher upfront cost but potentially lower per-VM cost at scale
- Cost-effective when running multiple VMs that fully utilize the host
- Reserved pricing available for additional savings

### Cost Efficiency Breakeven Point

The breakeven point depends on the specific workloads and instance types, but generally:

- **For our DataOps VMs (bx2-8x32)**: A dedicated host becomes cost-effective when running 8+ instances of this size
- **For our Ethos server (gx3-48x240x2l40s)**: Due to its specialized GPU requirements, a dedicated host would be cost-effective only if we plan to run multiple GPU-intensive workloads

## Performance Considerations

### Network Performance

- **Regular Instances**: Standard network performance based on instance profile
- **Dedicated Hosts**: Potentially better network performance due to dedicated resources and reduced contention

### Disk I/O Performance

- **Regular Instances**: Variable I/O performance that may be affected by other tenants
- **Dedicated Hosts**: More consistent I/O performance, especially for disk-intensive workloads

### CPU Performance

- **Regular Instances**: May experience CPU steal time during high contention periods
- **Dedicated Hosts**: Guaranteed CPU resources with no contention from other customers

## Reservations with Dedicated Hosts

Reservations can be used with both regular instances and dedicated hosts:

- For regular instances, reservations provide capacity guarantees and discounted pricing
- For dedicated hosts, reservations offer similar benefits but at the host level

## Recommendation for CloudOps Fleet

Based on our current workload profile:

1. **For Ethos Server**: 
   - If consistent GPU performance is critical, consider a dedicated host
   - Otherwise, a reserved instance provides good cost savings with acceptable performance

2. **For DataOps VMs**:
   - With only 3 VMs, regular reserved instances are likely more cost-effective than a dedicated host
   - Consider dedicated hosts if planning to scale to 8+ similar VMs in the future

3. **Hybrid Approach**:
   - Use reserved instances for current workloads
   - Consider dedicated hosts for future expansion if workloads increase significantly

## Implementation Steps

### For Reserved Instances (Current Recommendation)

1. Create reservations using the `create_reservations.sh` script
2. Recreate VMs with the ibm-admin key using the `recreate_dataops_vms.sh` script
3. Set up the recreated VMs using the `setup_dataops_vms.sh` script

### For Dedicated Hosts (Future Consideration)

1. Create a dedicated host group
2. Create dedicated hosts within the group
3. Deploy VMs on the dedicated hosts
4. Migrate workloads to the new VMs

## Conclusion

For the current CloudOps Fleet infrastructure with 1 Ethos server and 3 DataOps VMs, reserved instances offer the best balance of cost and performance. As the infrastructure grows, dedicated hosts may become a more attractive option, especially if consistent performance and workload isolation become higher priorities.