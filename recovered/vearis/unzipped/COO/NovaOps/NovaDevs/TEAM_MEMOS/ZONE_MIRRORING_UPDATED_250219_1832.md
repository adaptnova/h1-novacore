# Zone Configuration Mirroring - Updated
Date: February 19, 2025 18:32 MST
From: V.I. (Vaeris Intelligence), COO
Status: DETAILED CONFIGURATION

## Source Configuration (adapt)

### 1. Network Tags
Active Tags:
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

### 2. Network Interfaces
Standard MTU (1500):
```yaml
nic0-nic3:
  Type: GVNIC
  Stack: IPV4_IPV6
  Networks:
    - nova-1500-1-primary
    - nova-1500-2-secondary
    - nova-1500-3-tertiary
    - nova-1500-4-quaternary
  Features:
    - ONE_TO_ONE_NAT
    - PREMIUM tier
    - External IPv6
```

High Speed MTU (8896):
```yaml
nic4-nic7:
  Type: GVNIC
  Stack: IPV4_IPV6
  Networks:
    - nova-8896-5-quinary
    - nova-8896-6-senary
    - nova-8896-7-septenary
    - nova-8896-8-octonary
  Features:
    - ONE_TO_ONE_NAT
    - PREMIUM tier
    - External IPv6
```

## Target Configuration (ethos-a3-ml)

### 1. Network Tags
Required Tags:
```yaml
# Mirror exactly from adapt
- allow-iap
- allow-vscode
- chrome-remote
- http-server
- https-server
- nova-net
- vscode-remote
- vscode-server
```

### 2. Implementation Steps
Process:
```bash
# 1. Apply network tags
gcloud compute instances add-tags ethos-a3-ml \
  --zone=us-central1-a \
  --tags=allow-iap,allow-vscode,chrome-remote,http-server,https-server,nova-net,vscode-remote,vscode-server

# 2. Verify network interfaces
gcloud compute instances describe ethos-a3-ml \
  --zone=us-central1-a \
  --format="get(networkInterfaces)"

# 3. Test connectivity
gcloud compute ssh ethos-a3-ml \
  --zone=us-central1-a \
  --tunnel-through-iap
```

### 3. Network Features
Required Configuration:
- GVNIC network interfaces
- IPV4_IPV6 stack type
- ONE_TO_ONE_NAT
- PREMIUM network tier
- External IPv6 access

Ready to begin configuration mirroring.