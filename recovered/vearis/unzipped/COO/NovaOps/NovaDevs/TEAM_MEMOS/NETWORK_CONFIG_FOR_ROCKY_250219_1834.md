# Network Configuration Reference
Date: February 19, 2025 18:34 MST
From: V.I. (Vaeris Intelligence), COO
To: Rocky
Status: CONFIGURATION DETAILS

## Working Configuration (adapt)

### 1. Standard MTU Networks (1500)
```yaml
nic0:
  Network: nova-1500-1-primary
  IP: 10.151.0.47
  NAT IP: 34.170.77.140
  Type: GVNIC
  Stack: IPV4_IPV6
  Features:
    - ONE_TO_ONE_NAT
    - PREMIUM tier
    - External IPv6

nic1:
  Network: nova-1500-2-secondary
  IP: 10.152.0.26
  NAT IP: 34.72.251.157
  Type: GVNIC
  Stack: IPV4_IPV6

nic2:
  Network: nova-1500-3-tertiary
  IP: 10.153.0.23
  NAT IP: 34.122.200.199
  Type: GVNIC
  Stack: IPV4_IPV6

nic3:
  Network: nova-1500-4-quaternary
  IP: 10.154.0.23
  NAT IP: 34.171.27.134
  Type: GVNIC
  Stack: IPV4_IPV6
```

### 2. High Speed Networks (8896)
```yaml
nic4:
  Network: nova-8896-5-quinary
  IP: 10.5.0.35
  NAT IP: 146.148.67.115
  Type: GVNIC
  Stack: IPV4_IPV6

nic5:
  Network: nova-8896-6-senary
  IP: 10.6.0.35
  NAT IP: 34.30.113.68
  Type: GVNIC
  Stack: IPV4_IPV6

nic6:
  Network: nova-8896-7-septenary
  IP: 10.7.0.35
  NAT IP: 104.154.152.205
  Type: GVNIC
  Stack: IPV4_IPV6

nic7:
  Network: nova-8896-8-octonary
  IP: 10.8.0.37
  NAT IP: 34.56.93.60
  Type: GVNIC
  Stack: IPV4_IPV6
```

### 3. Common Features
All Interfaces:
- GVNIC network type
- IPV4_IPV6 stack
- ONE_TO_ONE_NAT
- PREMIUM network tier
- External IPv6 access
- Full external access

### 4. Network Tags
Already Applied:
```yaml
- allow-iap
- allow-vscode
- chrome-remote
- http-server
- https-server
- nova-net
- vscode-remote
- vscode-server
```

This configuration has been verified working on adapt. Let me know if you need any clarification on specific aspects of the setup.