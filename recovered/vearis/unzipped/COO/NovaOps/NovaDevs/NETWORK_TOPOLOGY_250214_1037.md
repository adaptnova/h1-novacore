# Nova Network Topology
Date: February 14, 2025 10:37 MST
Author: V.I. (Vaeris Intelligence)
Status: ACTIVE

## Ethos Server Network Configuration

### High-Speed Networks (8896 MTU)
1. Primary (nic0):
   - Network: nova-8896-1-primary
   - IP: 10.1.0.47
   - NAT IP: 34.71.236.1
   - Purpose: Primary ML model distribution

2. Secondary (nic1):
   - Network: nova-8896-2-secondary
   - IP: 10.2.0.29
   - NAT IP: 34.46.73.27
   - Purpose: Model training coordination

3. Tertiary (nic2):
   - Network: nova-8896-3-tertiary
   - IP: 10.3.0.27
   - NAT IP: 34.57.29.16
   - Purpose: Dataset distribution

4. Quaternary (nic3):
   - Network: nova-8896-4-quaternary
   - IP: 10.4.0.27
   - NAT IP: 34.56.88.177
   - Purpose: Training metrics collection

### External Networks (1500 MTU)
1. Primary (nic4):
   - Network: nova-1500-1-primary
   - IP: 10.151.0.41
   - NAT IP: 34.173.60.10
   - IPv6: 2600:2d00:4237:2144:a97:29:0:0
   - Purpose: Primary external access

2. Secondary (nic5):
   - Network: nova-1500-2-secondary
   - IP: 10.152.0.21
   - NAT IP: 34.67.23.228
   - IPv6: 2600:2d00:4001:72c1:a98:15:0:0
   - Purpose: Downloads and updates

3. Tertiary (nic6):
   - Network: nova-1500-3-tertiary
   - IP: 10.153.0.18
   - NAT IP: 35.222.205.28
   - IPv6: 2600:2d00:4235:5951:a99:12:0:0
   - Purpose: API access

4. Quaternary (nic7):
   - Network: nova-1500-4-quaternary
   - IP: 10.154.0.18
   - NAT IP: 34.133.80.187
   - IPv6: 2600:2d00:4008:61a6:a9a:12:0:0
   - Purpose: Monitoring and metrics

## Network Features

### Common Attributes
- Premium tier networking
- ONE_TO_ONE_NAT configuration
- IPV4_ONLY stack type (with IPv6 on 1500 MTU)
- Full external access through NAT

### Security
- IAP tunneling enabled
- Network tags:
  * allow-iap
  * chrome-remote
  * nova-net
  * vscode-remote

### Performance
- 8896 MTU for internal operations
- 1500 MTU for external connectivity
- Premium network tier for optimal performance

## Access Patterns

### Direct System Access
```bash
# Primary access through IAP
gcloud compute ssh ethos-a3-ml --zone=us-central1-a --tunnel-through-iap
```

### Network Testing
```bash
# Test connectivity to specific network
ping 10.1.0.47  # Primary high-speed
ping 10.151.0.41  # Primary external

# Monitor network performance
iftop -i nic0  # Monitor primary high-speed
iftop -i nic4  # Monitor primary external
```

## Network Usage Guidelines

### High-Speed Networks (8896 MTU)
- Use for ML model distribution
- Inter-service communication
- Dataset transfer
- Metrics collection

### External Networks (1500 MTU)
- Software downloads
- System updates
- API access
- External monitoring

Remember: All access must go through IAP tunnel for security.