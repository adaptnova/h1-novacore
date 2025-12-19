# Zone Configuration Mirroring
Date: February 19, 2025 18:28 MST
From: V.I. (Vaeris Intelligence), COO
Status: ANALYSIS

## Working Configuration (adapt/dev)

### 1. Network Structure
adapt-zone:
```yaml
Internal Network:
  CIDR: 10.1.0.0/16
  NAT: 34.71.236.0/24
  Purpose: Model adaptation
  Tags:
    - allow-iap
    - nova-net
    - vscode-remote
```

dev-zone:
```yaml
Internal Network:
  CIDR: 10.2.0.0/16
  NAT: 34.46.73.0/24
  Purpose: Development
  Tags:
    - allow-iap
    - nova-net
    - vscode-remote
```

### 2. Target Configuration
ethos-zone:
```yaml
Internal Network:
  CIDR: 10.3.0.0/16
  NAT: 34.57.29.0/24
  Purpose: ML operations
  Tags: [MIRROR FROM ADAPT]
    - allow-iap
    - nova-net
    - vscode-remote
```

ml-zone:
```yaml
Internal Network:
  CIDR: 10.4.0.0/16
  NAT: 34.56.88.0/24
  Purpose: Training
  Tags: [MIRROR FROM DEV]
    - allow-iap
    - nova-net
    - vscode-remote
```

### 3. Implementation Steps
Process:
1. Clone network tags
2. Mirror IAP configuration
3. Apply security rules
4. Test connectivity

### 4. Command Examples
```bash
# List current tags on adapt instance
gcloud compute instances describe adapt-instance \
  --zone=us-central1-a \
  --format="get(tags.items)"

# Apply same tags to ethos instance
gcloud compute instances add-tags ethos-a3-ml \
  --zone=us-central1-a \
  --tags=allow-iap,nova-net,vscode-remote

# Verify IAP access
gcloud compute ssh ethos-a3-ml \
  --zone=us-central1-a \
  --tunnel-through-iap
```

## Security Considerations

### 1. Network Access
Preserve:
- IAP tunneling
- Security tags
- Network rules
- Access patterns

### 2. Service Account
Requirements:
- Maintain permissions
- Preserve access levels
- Keep configurations
- Mirror settings

Ready to begin configuration mirroring.