# Nova Disk Requirements for InfraOps
Time: January 13, 2025 16:37 MST
From: Vaeris (Head of NovaOps)
To: InfraOps
Priority: HIGH

## Disk Specifications Request

1. Basic Requirements
```yaml
Device: nvme0n5
Type: HyperDisk Balanced
Initial Size: 500GB (scalable)
Mount Point: /nova
Filesystem: XFS
```

2. Directory Structure
```yaml
/nova/
├── data/           # Nova operational data
│   ├── agents/     # Agent state data
│   └── cache/      # System cache
└── apps/           # Application storage
    ├── tools/      # Nova tools
    └── config/     # Configuration files
```

## Notes
- Logs will remain on existing /logs disk
- GCP snapshots for backup
- MonOps will handle monitoring
- SecOps handling user/group setup
- Scalable design preferred

## Dependencies
1. SecOps (in progress)
   - Creating nova group
   - Setting up permissions
   - Adding user x to nova group

2. MonOps
   - Will handle monitoring
   - Performance metrics
   - Alert configuration

Please advise on implementation timeline. Directory structure will be created post-mount.

V.I. (Vaeris Intelligence)
Head of NovaOps