# VPC Connectivity Final Report

## Executive Summary

We have successfully implemented and tested load balancing across multiple network interfaces on the adapt server. Our investigation revealed that the multipath routing is working correctly for specific IP addresses, but domain name resolution is limited to eth7, which is the only interface with a public gateway attached in the VPC configuration.

## Current State

### Network Configuration

- **8 physical interfaces** (eth0-eth7) are properly configured and UP
- **Multipath routing** is correctly implemented with weighted distribution
- **Load balancing** is working for specific IP addresses
- **Only eth7** has external connectivity for domain name resolution

### VPC Configuration

- **VPC Name**: adapt-vpc-dallas
- **Routing Table**: crouch-spotting-quote-nuptials (0 routes)
- **Public Gateway**: Only attached to nic8-subnet (eth7)
- **Subnets**: 8 subnets (nic1-subnet through nic8-subnet)

### Connectivity Test Results

| Destination | IP Address | Interface Used | Success Rate |
|-------------|------------|----------------|--------------|
| IBM COS US East | 169.63.118.82 | eth5 | 100% |
| IBM COS US South | 169.62.82.68 | eth7 | 100% |
| IBM Cloud | 72.247.204.160 | eth1 | 100% |
| Google DNS | 8.8.8.8 | eth7 | 100% |
| Cloudflare DNS | 1.1.1.1 | eth7 | 100% |

### Internal Routing

All subnet gateways (10.240.1.1 through 10.240.8.1) are routed through eth0, which is expected since eth0 has all the virtual interfaces configured.

## Key Findings

1. **Multipath Routing Works**: The multipath routing configuration is correctly distributing traffic across different interfaces based on destination IP addresses.

2. **Domain Name Resolution Limited**: Domain name resolution requires DNS access, which is only available through eth7 (the interface with the public gateway).

3. **VPC Routing Table Empty**: The VPC routing table "crouch-spotting-quote-nuptials" has 0 routes, which explains why traffic can't be properly routed through other interfaces.

4. **Public Gateway Missing**: Only nic8-subnet has a public gateway attached, which is why only eth7 can reach external destinations for domain name resolution.

## Root Cause Analysis

The root cause of the connectivity issues is the VPC configuration:

1. **Missing Routes**: The VPC routing table has no routes defined, so traffic doesn't know how to reach external destinations.

2. **Missing Public Gateways**: Only one subnet (nic8-subnet) has a public gateway attached, so only eth7 can reach the internet directly.

3. **DNS Resolution**: Without public gateways on other subnets, DNS resolution is only possible through eth7, which limits the effectiveness of load balancing for domain names.

## Recommendations

1. **Add Internet Route to VPC Routing Table**:
   - Add a route for 0.0.0.0/0 (all internet traffic) to the VPC routing table
   - This will allow traffic to be properly routed to external destinations

2. **Attach Public Gateways to All Subnets**:
   - Create public gateways for each zone if needed
   - Attach public gateways to all subnets
   - This will allow all interfaces to reach the internet directly

3. **Configure DNS Servers**:
   - Configure DNS servers on all interfaces
   - This will allow domain name resolution through any interface

4. **Monitor and Adjust Weights**:
   - Monitor traffic distribution across interfaces
   - Adjust weights based on performance metrics
   - Increase weights for faster interfaces (eth5, eth7)

## Implementation Plan

1. **Fix VPC Routing Table**:
   ```bash
   # Add internet route to VPC routing table
   ibmcloud is vpc-routing-table-route-create $VPC_ID $ROUTING_TABLE_ID --zone us-south-1 --destination 0.0.0.0/0 --action deliver --next-hop $GATEWAY_IP --name internet-route
   ```

2. **Create and Attach Public Gateways**:
   ```bash
   # Create public gateways for each zone
   for zone in us-south-1 us-south-2 us-south-3; do
     ibmcloud is public-gateway-create adapt-pgw-$zone $VPC_ID $zone
   done

   # Attach public gateways to all subnets
   for subnet in $(ibmcloud is subnets --output json | jq -r '.[] | select(.vpc.name=="adapt-vpc-dallas") | .id'); do
     zone=$(ibmcloud is subnet $subnet --output json | jq -r '.zone.name')
     pgw=$(ibmcloud is public-gateways --output json | jq -r ".[] | select(.vpc.name==\"adapt-vpc-dallas\" and .zone.name==\"$zone\") | .id")
     ibmcloud is subnet-public-gateway-attach $subnet $pgw
   done
   ```

3. **Configure DNS Servers**:
   ```bash
   # Configure DNS servers on all interfaces
   for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
     echo "nameserver 8.8.8.8" > /etc/netplan/99-$iface-dns.yaml
     echo "nameserver 1.1.1.1" >> /etc/netplan/99-$iface-dns.yaml
   done
   netplan apply
   ```

## Conclusion

The adapt server has been successfully configured with multipath routing and load balancing across 8 network interfaces. The current configuration is working correctly for specific IP addresses, but domain name resolution is limited to eth7 due to VPC configuration issues.

By implementing the recommended changes to the VPC configuration, we can enable full external connectivity across all interfaces and maximize the benefits of load balancing. This will improve throughput, reliability, and overall performance of the adapt server.

## Report Generated

- **Date**: March 27, 2025
- **Time**: 23:02 MST
- **Engineer**: Zorion (IBM Cloud Infrastructure Engineer)