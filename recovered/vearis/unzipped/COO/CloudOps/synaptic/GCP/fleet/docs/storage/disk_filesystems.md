# GCP Fleet Disk and Filesystem Documentation
Version: 1.0.0
Created: 2025-02-26 20:24 MST
Author: Atlas

## Instance Storage Configurations

### ethos (34.72.175.241)
1. Root Filesystem
   - Device: /dev/nvme0n1p1
   - Size: 100GB
   - Usage: 39% (36GB used, 59GB available)
   - Mount: /
   - Purpose: System and application files

2. LLMs Storage
   - Device: /dev/nvme0n2
   - Size: 3TB
   - Usage: 2% (54GB used, 3.0TB available)
   - Mount: /llms-ethos
   - Purpose: Large Language Model storage and processing

3. Data Storage
   - Device: /dev/nvme0n3
   - Size: 500GB
   - Usage: 1% (3.6GB used, 497GB available)
   - Mount: /data-ethos
   - Purpose: Application data and processing

4. Logs Storage
   - Device: /dev/nvme0n4
   - Size: 100GB
   - Usage: 1% (746MB used, 100GB available)
   - Mount: /logs-ethos
   - Purpose: System and application logs

### System Memory Configuration
- RAM: 693GB Physical Memory
- Swap: Not configured
- tmpfs: 139GB allocated for /run

## Filesystem Standards
1. Dedicated mount points for specific functions:
   - /llms-* : Language model storage
   - /data-* : Application data
   - /logs-* : System logging

2. Monitoring Thresholds:
   - Warning: 80% usage
   - Critical: 90% usage
   - Emergency: 95% usage

## Next Steps
1. Document remaining instance configurations
2. Establish backup policies
3. Configure monitoring alerts
4. Implement capacity planning

Signed: Atlas
Timestamp: 2025-02-26 20:24:06 MST