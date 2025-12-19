# Nova Instance Templates (v2)
Date: February 14, 2025 07:35 MST
Author: V.I. (Vaeris Intelligence)
Status: ACTIVE

## Templates Overview

### 1. Vaeris Operations Template (vaeris-ops-template-v2)
- Purpose: Network Operations & Management
- Configuration:
  * Machine Type: c3-highcpu-44
  * Networks: Full Mesh Configuration
    - High-Speed Internal (8896 MTU):
      * nova-8896-1-primary
      * nova-8896-2-secondary
      * nova-8896-3-tertiary
      * nova-8896-4-quaternary
    - External Access (1500 MTU):
      * nova-1500-1-primary
      * nova-1500-2-secondary
      * nova-1500-3-tertiary
      * nova-1500-4-quaternary
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

### 2. Ethos ML Template (ethos-ml-template-v2)
- Purpose: AI/ML Workloads
- Configuration:
  * Machine Type: a3-highgpu-8g
  * Accelerator: 8x NVIDIA H100 80GB
  * Networks: Full Mesh Configuration
    - High-Speed Internal (8896 MTU):
      * nova-8896-1-primary
      * nova-8896-2-secondary
      * nova-8896-3-tertiary
      * nova-8896-4-quaternary
    - External Access (1500 MTU):
      * nova-1500-1-primary
      * nova-1500-2-secondary
      * nova-1500-3-tertiary
      * nova-1500-4-quaternary
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Maintenance Policy: TERMINATE
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

### 3. Adapt Infrastructure Template (adapt-infra-template-v2)
- Purpose: Core Infrastructure Services
- Configuration:
  * Machine Type: c3-highcpu-44
  * Networks: Full Mesh Configuration
    - High-Speed Internal (8896 MTU):
      * nova-8896-1-primary
      * nova-8896-2-secondary
      * nova-8896-3-tertiary
      * nova-8896-4-quaternary
    - External Access (1500 MTU):
      * nova-1500-1-primary
      * nova-1500-2-secondary
      * nova-1500-3-tertiary
      * nova-1500-4-quaternary
  * Storage:
    - Boot Disk: 200GB SSD
    - Type: pd-ssd
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

### 4. Development Workspace Template (dev-workspace-template-v2)
- Purpose: Development Environment
- Configuration:
  * Machine Type: c3-highcpu-44
  * Networks: Full Mesh Configuration
    - High-Speed Internal (8896 MTU):
      * nova-8896-1-primary
      * nova-8896-2-secondary
      * nova-8896-3-tertiary
      * nova-8896-4-quaternary
    - External Access (1500 MTU):
      * nova-1500-1-primary
      * nova-1500-2-secondary
      * nova-1500-3-tertiary
      * nova-1500-4-quaternary
  * Storage:
    - Boot Disk: 100GB SSD
    - Type: pd-ssd
  * Tags: allow-iap, nova-net, chrome-remote, vscode-remote
  * Preemptible: Yes
  * Metadata:
    - enable-oslogin: FALSE
    - block-project-ssh-keys: FALSE
    - enable-iap: TRUE

## Network Configuration
- All templates now include full mesh network topology
- Each instance has access to all 8 networks:
  * 4x High-speed internal networks (8896 MTU)
  * 4x External access networks (1500 MTU)
- Network tags configured for proper firewall rule application
- IAP access enabled across all networks

## Cost Optimization
- All templates use preemptible instances for development
- Production versions will be created with standard instances
- GPU instances configured for optimal cost/performance ratio
- Storage optimized per workload requirements

## Next Steps
1. Create production (non-preemptible) versions of templates
2. Test instance creation from v2 templates
3. Validate network connectivity across all interfaces
4. Document performance metrics

## Notes
- Previous v1 templates deprecated but preserved for reference
- Templates can be modified as needed
- Additional templates may be created for specific workloads
- Monitor resource quotas
- Keep templates updated with latest configurations