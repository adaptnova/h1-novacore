# Public IP Assignment Documentation

## Overview

This document describes the process of assigning public IPs directly to all network interfaces on the adapt server. This approach eliminates the need for NAT and simplifies the configuration.

## Implementation Details

### Date and Time
- **Date**: 2025-03-26
- **Time**: 22:18:48 MST

### Server Information
- **Server Name**: adapt
- **Server ID**: 0717_ee285094-0683-4f21-a573-ae87022853e9
- **Private IP**: 10.240.1.6

### Changes Made

1. **Backup Creation**
   - Created backup of current network configuration
   - Backup location: ./backups/20250326_221712
   - Includes: interfaces, routes, iptables rules, sysctl settings

2. **Floating IP Assignment**
   - Assigned floating IPs to all network interfaces
   - Details:
     - shortage-overcast-panda-keep: 52.118.187.172 (adapt-floating-ip)
     - bunt-comic-sixth-wrongness: 52.118.145.162 (dataops-primary)
     - unmanaged-cyclist-providing-crux: 150.240.66.13 (dataops-timeseries)
     - washday-await-corsage-obscurity: 52.116.131.63 (dataops-vector)
     - activate-hazelnut-garage-automaker: 52.118.191.234 (ethos-floating-ip-1742660058)
     - pgw-b1c7a2f0-0911-11f0-8f69-a725ab1e392f: 150.240.165.95 (pgw-b1c7a2f0-0911-11f0-8f69-a725ab1e392f)

## Rollback Plan

A rollback script has been created to revert the changes if necessary:

```
./backups/20250326_221712/rollback.sh
```

The rollback script will:
1. Unassign all floating IPs from the interfaces
2. Restore the original iptables rules
3. Restore the original sysctl settings

## Verification

The following tests were performed to verify the changes:

1. **Connectivity Tests**
   - Ping tests to all assigned floating IPs
   - External connectivity tests from each interface

2. **Speed Tests**
   - Download tests from multiple sources
   - Tests performed across all interfaces
   - Results saved to speed test report

## Conclusion

The adapt server now has public IPs assigned directly to all network interfaces, eliminating the need for NAT and simplifying the configuration. This approach provides direct external connectivity for all interfaces.

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.1 | 2025-03-26 | Zorion | Initial implementation with IBM Cloud login |
