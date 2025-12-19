# Nova Instance Templates
Date: February 14, 2025 07:31 MST
Author: V.I. (Vaeris Intelligence)
Status: ACTIVE

## Templates Overview

### 1. Vaeris Operations Template (vaeris-ops-template)
- Purpose: Network Operations & Management
- Configuration:
  * Machine Type: c3-highcpu-44
  * Networks:
    - nova-8896-1-primary (High-speed internal)
    - nova-1500-1-primary (External access)
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

### 2. Ethos ML Template (ethos-ml-template)
- Purpose: AI/ML Workloads
- Configuration:
  * Machine Type: a2-highgpu-1g
  * Accelerator: 1x NVIDIA Tesla A100
  * Networks:
    - nova-8896-1-primary (High-speed internal)
    - nova-1500-1-primary (External access)
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Maintenance Policy: TERMINATE
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

## Network Configuration
All templates include:
- Dual-network setup for both high-speed internal (8896 MTU) and external (1500 MTU) connectivity
- IAP access enabled
- Full network tag set for proper firewall rule application

## Cost Optimization
- All templates use preemptible instances for development
- Production versions will be created with standard instances
- GPU instances configured for optimal cost/performance ratio

## Next Steps
1. Create adapt-infra-template for core infrastructure
2. Create dev-workspace-template for development environment
3. Test instance creation from templates
4. Document performance metrics

## Notes
- Templates can be modified as needed
- Additional templates may be created for specific workloads
- Monitor resource quotas
- Keep templates updated with latest configurations