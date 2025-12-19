# Nova Disk Setup Plan
Time: January 13, 2025 16:13 MST
Priority: HIGH

## Selected Drive
```yaml
Device: /dev/nvme0n2
Capacity: ~1.5TB
Model: nvme_card-pd
Status: Available
```

## Setup Commands

1. Create Partition Table
```bash
# Create new GPT partition table
sudo parted /dev/nvme0n2 mklabel gpt

# Create single partition
sudo parted /dev/nvme0n2 mkpart primary 0% 100%
```

2. Format Filesystem
```bash
# Format as XFS for better performance
sudo mkfs.xfs /dev/nvme0n2p1
```

3. Create Mount Point
```bash
# Create directory
sudo mkdir -p /nova

# Add to fstab for persistent mounting
echo '/dev/nvme0n2p1    /nova    xfs    defaults,noatime    0    2' | sudo tee -a /etc/fstab

# Mount the filesystem
sudo mount /nova
```

4. Create Directory Structure
```bash
# Create main directories
sudo mkdir -p /nova/{data,logs,backup,apps}/{redis,agents,system}

# Create specific subdirectories
sudo mkdir -p /nova/data/agents/{langchain,system,integration}
sudo mkdir -p /nova/logs/agents/{performance,errors,activity}
sudo mkdir -p /nova/apps/tools/{monitoring,deployment,management}

# Set permissions
sudo chown -R nova:nova /nova
sudo chmod -R 755 /nova
```

## Partition Layout
```yaml
/nova/: 1.5TB total
  ├── data/: 600GB
  │   ├── redis/: 200GB
  │   ├── agents/: 300GB
  │   └── cache/: 100GB
  │
  ├── logs/: 400GB
  │   ├── redis/: 100GB
  │   ├── agents/: 200GB
  │   └── system/: 100GB
  │
  ├── backup/: 300GB
  │   ├── daily/: 200GB
  │   └── states/: 100GB
  │
  └── apps/: 200GB
      ├── redis/: 50GB
      ├── tools/: 100GB
      └── config/: 50GB
```

## Performance Settings
```bash
# Set noatime to reduce write operations
sudo mount -o remount,noatime /nova

# Enable TRIM for SSD optimization
sudo systemctl enable fstrim.timer
sudo systemctl start fstrim.timer

# Set I/O scheduler to none for NVMe
echo 'none' | sudo tee /sys/block/nvme0n2/queue/scheduler
```

## Monitoring Setup
```bash
# Install monitoring tools
sudo apt-get install -y smartmontools nvme-cli

# Set up SMART monitoring
sudo smartctl -a /dev/nvme0n2

# Enable SMART monitoring service
sudo systemctl enable smartd
sudo systemctl start smartd
```

## Verification Steps
1. Check mount
```bash
df -h /nova
```

2. Verify performance
```bash
sudo fio --filename=/nova/test --direct=1 --rw=randrw --bs=4k --ioengine=libaio --iodepth=256 --runtime=10 --numjobs=4 --time_based --group_reporting --name=iops-test --eta-newline=1 --readonly
```

3. Check directory structure
```bash
tree -L 3 /nova
```

## Expected Timeline
- Disk setup: 2 minutes
- Directory creation: 1 minute
- Permission setup: 1 minute
- Performance tuning: 1 minute
- Verification: 5 minutes
Total: 10 minutes

Ready to proceed with disk setup on your approval.

V.I. (Vaeris Intelligence)
Head of NovaOps