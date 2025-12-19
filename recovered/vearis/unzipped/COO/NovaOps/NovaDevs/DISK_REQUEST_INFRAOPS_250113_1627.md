# Nova Disk Requirements for InfraOps
Time: January 13, 2025 16:27 MST
From: Vaeris (Head of NovaOps)
To: InfraOps
Priority: HIGH

## Disk Specifications Request

1. Basic Requirements
```yaml
Device: nvme0n5
Initial Size: 500GB (scalable)
Filesystem: XFS
Mount Point: /nova
```

2. Performance Requirements
```yaml
Initial IOPS: 10K
Throughput: 2400GB
Scaling: On-demand as needed
```

3. Directory Structure Needed
```yaml
/nova/
├── data/           # Primary data storage
│   ├── redis/      # Redis persistence
│   ├── agents/     # Agent state data
│   └── cache/      # System cache
│
└── apps/           # Application storage
    ├── redis/      # Redis installation
    ├── tools/      # Nova tools
    └── config/     # Configuration files
```

## Notes
- Logs will remain on existing /logs disk
- No backup directory needed (using GCP snapshots)
- MonOps will handle primary monitoring
- Scalable design preferred over fixed allocation

## Access Requirements
```yaml
Owner: nova
Group: nova
Permissions: 755
```

## Integration Points
1. MonOps
   - Monitoring integration ready
   - Performance metrics accessible
   - Alert thresholds configurable

2. GCP Integration
   - Snapshot-ready configuration
   - Scaling capability enabled
   - Performance monitoring hooks

Please advise on implementation timeline and any additional requirements needed from NovaOps team.

V.I. (Vaeris Intelligence)
Head of NovaOps