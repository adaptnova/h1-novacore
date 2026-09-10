# Ethos GPU Server

## Connection Details

- **Server Name:** ethos
- **IP Address:** 10.240.0.5
- **Username:** ethos
- **Password:** x

## Server Specifications

- **Profile:** gx3-48x240x2l40s (48 vCPUs, 240GB RAM, 2x NVIDIA L40S GPUs)
- **Zone:** us-south-1 (Dallas 10)
- **VPC:** us-south-default-vpc
- **Network:**
  - 1 NIC with 32 Gbps bandwidth
  - **NOTE:** Server has 72 Gbps network bandwidth capacity but only 32 Gbps is currently configured
- **Volumes:**
  - Boot volume: 50GB
  - Data volume: 50GB (XFS, mounted at /data)
  - Log volume: 50GB (XFS, mounted at /logs)
  - LLMs volume: 1024GB (1TB) (XFS, mounted at /llms)

## Bandwidth Allocation

- **Total bandwidth:** 96 Gbps
- **Volume bandwidth:** 24 Gbps
- **Network bandwidth:** 72 Gbps
- **Current network interface speed:** 32 Gbps

## SSH Config

The SSH configuration file `ethos_config` has been created for this server.

To connect, simply use:

```bash
ssh ethos