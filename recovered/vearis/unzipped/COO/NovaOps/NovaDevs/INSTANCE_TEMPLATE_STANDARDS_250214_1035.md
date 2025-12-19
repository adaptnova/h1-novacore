# Nova Instance Template Standards
Date: February 14, 2025 10:35 MST
Author: V.I. (Vaeris Intelligence)
Status: ACTIVE

## Core Template Requirements

### 1. System Access
- OS Login enabled (`enable-oslogin: TRUE`)
- IAP tunneling support
- Full system access for Nova operations

### 2. Network Tags
Required tags for all instances:
- `allow-iap`: Enable Identity-Aware Proxy access
- `nova-net`: Nova network access
- `chrome-remote`: Remote desktop capability
- `vscode-remote`: VS Code remote development

### 3. Network Interfaces
Each instance should have:
- High-speed internal (8896 MTU) for Nova communication
- Standard external (1500 MTU) for downloads/updates

### 4. Current Templates

#### ML/AI Template (ethos-ml-template-v3)
```yaml
properties:
  machineType: a3-highgpu-8g
  metadata:
    enable-oslogin: TRUE
  tags:
    - allow-iap
    - nova-net
    - chrome-remote
    - vscode-remote
  accelerators:
    - count: 8
      type: nvidia-h100-80gb
  disks:
    - boot: true
      autoDelete: false
      type: hyperdisk-balanced
```

#### Development Template (to be created)
```yaml
properties:
  machineType: c3-highcpu-44
  metadata:
    enable-oslogin: TRUE
  tags:
    - allow-iap
    - nova-net
    - chrome-remote
    - vscode-remote
  disks:
    - boot: true
      autoDelete: false
      type: hyperdisk-balanced
```

### 5. System Limits
All instances should support:
- Large file descriptors (1048576)
- Unlimited processes
- Unlimited core dumps
- Unlimited memory locking

## Template Creation Guidelines

### 1. Base Configuration
```bash
# Basic template structure
gcloud compute instance-templates create [name] \
  --machine-type=[type] \
  --network-interface=network=[network],subnet=[subnet] \
  --tags=allow-iap,nova-net,chrome-remote,vscode-remote \
  --metadata=enable-oslogin=TRUE
```

### 2. ML/AI Configuration
```bash
# ML template with GPUs
gcloud compute instance-templates create [name] \
  --machine-type=a3-highgpu-8g \
  --accelerator=count=8,type=nvidia-h100-80gb \
  --network-interface=network=[network],subnet=[subnet] \
  --tags=allow-iap,nova-net,chrome-remote,vscode-remote \
  --metadata=enable-oslogin=TRUE
```

## Security Considerations

### 1. Access Control
- OS Login for user management
- IAP for secure tunneling
- No direct external SSH

### 2. Network Security
- Internal networks for Nova communication
- External networks for updates only
- Firewall rules through tags

### 3. Resource Management
- Non-preemptible for production
- Preemptible for development/testing
- Proper disk management

## Maintenance

### 1. Template Updates
- Version templates (v1, v2, etc.)
- Document changes
- Test before deployment
- Maintain backward compatibility

### 2. Instance Migration
- Create new instances from updated templates
- Verify functionality
- Migrate services
- Update documentation

Remember: These standards ensure consistent, secure, and efficient Nova operations across all instances.