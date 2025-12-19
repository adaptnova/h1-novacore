# GCP Resource Inventory
Version: 1.0.1
Created: 2025-02-26 20:21 MST
Updated: 2025-02-26 20:23 MST
Author: Atlas

## Active Instances

### Instance Overview
1. adapt (Previously dev)
   - External IP: 35.184.242.84
   - Status: WORKING
   - Access: ssh x@35.184.242.84
   - Source Location: /data/ax/NovaOps

2. nova (Previously jobber)
   - External IP: 35.224.20.50
   - Status: WORKING
   - Access: ssh x@35.224.20.50
   - Target Location: /data-nova/ax/NovaOps

3. dev (Previously rocky)
   - External IP: 104.154.33.3
   - Status: WORKING
   - Access: ssh x@104.154.33.3

4. ethos
   - External IP: 34.72.175.241
   - Status: WORKING
   - Access: ssh x@34.72.175.241
   - Disk Configuration:
     * Root (nvme0n1): 100GB (39% used)
     * LLMs (nvme0n2): 3TB mounted at /llms-ethos (2% used)
     * Data (nvme0n3): 500GB mounted at /data-ethos (1% used)
     * Logs (nvme0n4): 100GB mounted at /logs-ethos (1% used)

## Data Migration Plan
Source: adapt (/data/ax/NovaOps)
Target: nova (/data-nova/ax/NovaOps)
Size: ~70GB

### Migration Strategy
1. Multiple rsync streams for parallel transfer
2. Using archive mode with checksum verification
3. Preserving file structure, dates, permissions
4. Implementing partial transfer support
5. Excluding unnecessary files (.git, venv)

### Transfer Command Pattern
```bash
rsync --archive --verbose --progress --stats --partial --itemize-changes \
--ignore-existing -vvv \
--exclude='.git/' --exclude='*venv*/' --exclude='*_env/' \
--temp-dir='/data/temp1' \
-e 'ssh -o "ProxyCommand none" -o "StrictHostKeyChecking no" -o "Compression no" -o "ConnectTimeout 10"'
```

## Next Steps
1. Continue disk and filesystem analysis on remaining instances
2. Document current resource allocation
3. Map network connectivity
4. Establish monitoring baseline
5. Begin data migration execution

Signed: Atlas
Timestamp: 2025-02-26 20:23:22 MST