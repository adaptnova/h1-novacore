# DataOps Servers

## Connection Details

### Primary Database Server
- **Server Name:** dataops-primary
- **IP Address:** 10.240.0.6
- **Username:** vertex
- **Password:** x
- **Specifications:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Network:** 1 NIC with 12 Gbps bandwidth
- **Bandwidth:**
  - Total bandwidth: 16 Gbps
  - Volume bandwidth: 4 Gbps
  - Network bandwidth: 12 Gbps
- **Volumes:**
  - Data volume: 100GB (XFS, mounted at /data)
  - Backup volume: 200GB (XFS, mounted at /backup)

### Vector Database Server
- **Server Name:** dataops-vector
- **IP Address:** 10.240.0.7
- **Username:** vertex
- **Password:** x
- **Specifications:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Network:** 1 NIC with 12 Gbps bandwidth
- **Bandwidth:**
  - Total bandwidth: 16 Gbps
  - Volume bandwidth: 4 Gbps
  - Network bandwidth: 12 Gbps
- **Volumes:**
  - Data volume: 80GB (XFS, mounted at /data)
  - Backup volume: 160GB (XFS, mounted at /backup)

### Time-Series Database Server
- **Server Name:** dataops-timeseries
- **IP Address:** 10.240.0.8
- **Username:** vertex
- **Password:** x
- **Specifications:** bx2-8x32 (8 vCPUs, 32GB RAM)
- **Network:** 1 NIC with 12 Gbps bandwidth
- **Bandwidth:**
  - Total bandwidth: 16 Gbps
  - Volume bandwidth: 4 Gbps
  - Network bandwidth: 12 Gbps
- **Volumes:**
  - Data volume: 60GB (XFS, mounted at /data)
  - Backup volume: 120GB (XFS, mounted at /backup)

## SSH Config

The SSH configuration file `dataops_config` has been created for these servers.

To connect, simply use:

```bash
ssh dataops-primary
ssh dataops-vector
ssh dataops-timeseries