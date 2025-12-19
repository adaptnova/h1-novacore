# GCP to IBM Cloud Migration Plan
**Version:** v1.0.0
**Created:** March 19, 2025 at 7:06 PM MST
**Author:** Synaptic

## Overview

This document outlines the plan for migrating data from Google Cloud Platform (GCP) to IBM Cloud. The migration will use rsync to transfer data from GCP instances to the adapt3 instance in IBM Cloud's us-south-2 region.

## Current Status

### IBM Cloud Target
- **Instance:** adapt3 in us-south-2 (Dallas)
- **IP Address:** 52.118.206.209
- **Data Volume:** /dev/vdf (1.5TB) mounted at /data-nova
- **Current Usage:** 1.1TB used (75%), 360GB available
- **Content:** Contains model files, application data, and various directories

### Required Migration

We need to migrate additional data from GCP to IBM Cloud as part of the platform migration away from GCP. Based on the current state of the adapt3 instance, we need to identify and transfer the remaining data from GCP.

## Disks to Rsync

### Primary Data Disks
1. **GCP 12TB Data Disk**
   - This large disk likely contains the majority of the remaining data that needs to be migrated
   - Will require multiple rsync operations due to the size
   - Need to prioritize critical data first

### Additional Disks
2. **Model Storage Disks**
   - Any disks containing ML models that haven't been transferred yet
   - Prioritize models currently in use by the platform

3. **Application Data Disks**
   - Disks containing application state, configurations, and user data
   - Ensure consistency by stopping applications before transfer

## Rsync Strategy

### Phase 1: Preparation
1. **Disk Identification**
   - Identify all GCP disks that need to be migrated
   - Document disk sizes, mount points, and content types
   - Prioritize disks based on importance and size

2. **Space Planning**
   - Assess available space on IBM Cloud volumes
   - Provision additional volumes if needed
   - Plan for temporary storage during migration

3. **Network Configuration**
   - Set up secure SSH connections between GCP and IBM Cloud
   - Configure firewall rules to allow rsync traffic
   - Test connectivity and transfer speeds

### Phase 2: Initial Transfer
1. **Critical Data Transfer**
   - Start with the most critical data from the 12TB disk
   - Use rsync with compression and delta-transfer algorithm
   - Monitor progress and performance

2. **Verification**
   - Verify data integrity after each transfer
   - Compare file counts, sizes, and checksums
   - Document any issues or discrepancies

### Phase 3: Incremental Updates
1. **Scheduled Syncs**
   - Set up regular incremental syncs for actively changing data
   - Use rsync's delta-transfer algorithm to minimize bandwidth usage
   - Document sync schedule and results

2. **Final Cutover**
   - Perform final sync immediately before service migration
   - Verify all data has been transferred successfully
   - Update application configurations to point to new data locations

## Rsync Commands

### Basic Transfer Command
```bash
rsync -avz --progress --stats \
    -e "ssh -i /path/to/ssh_key -o StrictHostKeyChecking=no" \
    gcp_user@gcp_instance:/path/to/source/ \
    /data-nova/destination/
```

### Large File Transfer
```bash
rsync -avz --progress --stats --partial --partial-dir=.rsync-partial \
    -e "ssh -i /path/to/ssh_key -o StrictHostKeyChecking=no" \
    gcp_user@gcp_instance:/path/to/source/ \
    /data-nova/destination/
```

### Bandwidth Limited Transfer
```bash
rsync -avz --progress --stats --bwlimit=50000 \
    -e "ssh -i /path/to/ssh_key -o StrictHostKeyChecking=no" \
    gcp_user@gcp_instance:/path/to/source/ \
    /data-nova/destination/
```

## Monitoring and Reporting

1. **Transfer Monitoring**
   - Use the rsync_monitor.sh script to track progress
   - Monitor system performance during transfers
   - Adjust transfer parameters based on performance

2. **Reporting**
   - Document all transfers in operations_history.md
   - Create daily progress reports
   - Track overall migration status

## Next Steps

1. **Identify GCP Instances**
   - Need to identify the specific GCP instances with the 12TB disk
   - Determine SSH access details for these instances

2. **Assess Disk Content**
   - Analyze the content of the 12TB disk
   - Determine which data has already been migrated
   - Prioritize remaining data for transfer

3. **Begin Transfer**
   - Start with a small test transfer to verify connectivity
   - Proceed with larger transfers based on priority
   - Monitor and adjust as needed

## Conclusion

This migration plan outlines the approach for transferring data from GCP to IBM Cloud. The focus is on the 12TB disk and any other critical data that hasn't been migrated yet. The plan will be updated as more information becomes available about the specific GCP instances and disks that need to be migrated.