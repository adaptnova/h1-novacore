# System Symlink Documentation

## Current Symlinks [2025-01-22]

### Log Management Symlinks
```bash
# Journal Logs
Source: /var/log/journal -> /logs/journal
Purpose: System journal logs storage
Size: ~801M (initial)
Permissions: system

# MCP Server Logs
Source: /var/log/mcp-servers -> /logs/mcp-servers
Purpose: MCP server logs storage
Size: ~70M (initial)
Permissions: root:x

# APT Cache
Source: /var/cache/apt -> /logs/apt
Purpose: Package management cache
Size: Variable
Permissions: root:root
```

### Docker Storage Symlink
```bash
Source: /var/lib/docker -> /data/var/lib/docker
Purpose: Docker container and image storage
Size: Variable (multiple GB)
Permissions: root:root
Location: /data partition (1.5TB volume)
```

## Mount Points

### Data Volume
```bash
Device: /dev/nvme0n2
Mount: /data
Type: ext4
Size: 1.5T
Used: 1.2T
Available: 222G
```

### Logs Volume
```bash
Device: /dev/nvme0n3
Mount: /logs
Type: xfs
Size: 100G
Used: 14G
Available: 87G
```

## Verification Commands

### Check Symlinks
```bash
ls -la /var/log/journal
ls -la /var/log/mcp-servers
ls -la /var/cache/apt
ls -la /var/lib/docker
```

### Check Mount Points
```bash
df -h /data /logs
mount | grep -E '/logs|/data'
```

## Maintenance Notes

1. Log Rotation
   - System logs are automatically rotated
   - Located on dedicated /logs volume
   - Managed through systemd-journald

2. Docker Storage
   - Container and image data on /data volume
   - Provides larger storage capacity
   - Separate from system volume

3. Best Practices
   - Always maintain symlinks when updating systems
   - Monitor disk usage on both volumes
   - Keep permissions consistent
   - Regular cleanup of old logs