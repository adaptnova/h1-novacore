# Load Balancing Implementation for Adapt Server

## Overview

This document explains the load balancing implementation for the adapt server, focusing on how it distributes network traffic across multiple high-performance interfaces to improve throughput, reliability, and overall performance.

## Implementation Approach

### Multipath Routing

We've implemented multipath routing across six high-performance interfaces:
- eth0 (weight: 10)
- eth1 (weight: 10)
- eth4 (weight: 10)
- eth5 (weight: 20) - Highest weight due to best performance
- eth6 (weight: 15)
- eth7 (weight: 15)

This approach uses the Linux kernel's built-in capabilities for multipath routing, which allows traffic to be distributed across multiple network paths based on assigned weights.

### How It Works

1. **Default Route with Multiple Nexthops**:
   - Instead of a single default route, we've configured a multipath default route with multiple nexthops
   - Each nexthop corresponds to one of our high-performance interfaces
   - Traffic is distributed according to the assigned weights

2. **Source-Based Routing**:
   - Each interface has its own routing table
   - Traffic originating from a specific interface uses that interface's routing table
   - This ensures symmetric routing (traffic goes out the same interface it came in)

3. **Weighted Distribution**:
   - eth5, which showed the highest performance (361.52 MB/s), has the highest weight (20)
   - eth6 and eth7, which also showed excellent performance, have higher weights (15)
   - Other interfaces have standard weights (10)
   - This ensures that faster interfaces handle more traffic

## Benefits

### 1. Increased Throughput

By distributing traffic across multiple interfaces, we can achieve higher overall throughput than would be possible with a single interface. For example:

- eth0: 235.35 MB/s
- eth1: 278.02 MB/s
- eth4: 234.98 MB/s
- eth5: 361.52 MB/s
- eth6: 263.60 MB/s
- eth7: 313.81 MB/s

With load balancing, we can potentially utilize the combined bandwidth of all these interfaces, significantly increasing the server's network capacity.

### 2. Improved Reliability

If one interface experiences issues or becomes unavailable, traffic will automatically be redistributed across the remaining interfaces. This provides fault tolerance and ensures continuous connectivity even if some interfaces fail.

### 3. Optimized Resource Utilization

By assigning higher weights to faster interfaces, we ensure that network resources are used optimally. Faster interfaces handle more traffic, maximizing overall performance.

### 4. Better Connection to IBM Cloud

The multipath routing implementation may help improve connectivity to IBM Cloud services by:

- Providing multiple paths to reach IBM Cloud endpoints
- Distributing connection attempts across different interfaces
- Reducing the impact of any interface-specific routing issues

## Technical Implementation

### Multipath Default Route

```bash
ip route add default \
  nexthop via 10.240.1.1 dev eth0 weight 10 \
  nexthop via 10.240.2.1 dev eth1 weight 10 \
  nexthop via 10.240.5.1 dev eth4 weight 10 \
  nexthop via 10.240.6.1 dev eth5 weight 20 \
  nexthop via 10.240.7.1 dev eth6 weight 15 \
  nexthop via 10.240.8.1 dev eth7 weight 15
```

### Source-Based Routing Tables

For each interface, we create a separate routing table and add rules to use that table for traffic originating from that interface:

```bash
# For eth0
ip route add 10.240.1.0/24 dev eth0 src 10.240.1.6 table 1
ip route add default via 10.240.1.1 dev eth0 table 1
ip rule add from 10.240.1.6 table 1

# Similar configuration for other interfaces
```

### Persistent Configuration

The configuration is made persistent across reboots by:

1. Creating a setup script at `/usr/local/sbin/setup-multipath-routing.sh`
2. Adding a network interface hook at `/etc/network/if-up.d/multipath-routing`

## Monitoring and Verification

The implementation includes verification steps to ensure that load balancing is working correctly:

1. **Route Selection Tests**:
   - Multiple tests to check route selection for external destinations
   - Verification that different interfaces are used for different connection attempts

2. **Performance Tests**:
   - Sequential download tests to measure performance
   - Parallel download tests to verify concurrent usage of multiple interfaces
   - Interface statistics monitoring to confirm traffic distribution

## Conclusion

The load balancing implementation provides a robust solution for maximizing the network performance of the adapt server. By distributing traffic across multiple high-performance interfaces, we can achieve higher throughput, improved reliability, and optimized resource utilization.

This approach should help address connectivity issues, including potential improvements in connectivity to IBM Cloud services, by providing multiple paths for network traffic and ensuring optimal use of available network resources.