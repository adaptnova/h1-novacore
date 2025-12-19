# IBM Cloud Data Migration Scripts

Created by Synaptic on March 19, 2025

## Overview

This repository contains scripts for efficient data migration between IBM Cloud and other platforms using rsync. The scripts are designed to work with the adapt3 instance in us-south-2 (Dallas) that has the data-adapt volume mounted at /data-nova.

## Current Setup

- **Instance**: adapt3 in us-south-2 (Dallas)
- **IP Address**: 52.118.206.209
- **Data Volume**: /dev/vdf (1.5TB) mounted at /data-nova
- **Usage**: 1.1TB used (75%), 360GB available
- **Content**: Contains model files, application data, and various directories

## Scripts

### 1. rsync_from_gcp.sh

A script to transfer data from Google Cloud Platform to IBM Cloud using rsync.

**Features:**
- Configurable source and destination paths
- Excludes unnecessary files and directories
- Detailed logging with timestamps
- Progress reporting
- SSH key authentication

**Usage:**
```bash
./rsync_from_gcp.sh
```

### 2. rsync_to_gcp.sh

A script to transfer data from IBM Cloud to Google Cloud Platform using rsync.

**Features:**
- Configurable source and destination paths
- Excludes unnecessary files and directories
- Detailed logging with timestamps
- Progress reporting
- SSH key authentication

**Usage:**
```bash
./rsync_to_gcp.sh
```

### 3. rsync_daemon_setup.sh

Sets up an rsync daemon for more efficient transfers, especially useful for large datasets.

**Features:**
- Automatic installation of rsync if not present
- Secure authentication with random password generation
- Systemd service configuration
- Detailed connection instructions
- Saves connection information for reference

**Usage:**
```bash
./rsync_daemon_setup.sh
```

### 4. rsync_monitor.sh

Monitors rsync progress and system performance during transfers.

**Features:**
- Real-time monitoring of CPU, memory, disk, and network usage
- Tracks rsync processes and transfer speeds
- CSV logging for later analysis
- Notifications when rsync starts or stops
- Configurable monitoring interval

**Usage:**
```bash
./rsync_monitor.sh
```

## Installation

1. The scripts have been copied to the adapt3 instance at `/root/rsync_scripts/`
2. They have been made executable with `chmod +x`
3. To use them, SSH into the adapt3 instance:

```bash
ssh -i /home/x/ibm-adapt_rsa root@52.118.206.209
cd /root/rsync_scripts
```

## Configuration

Before running the scripts, you should modify them to match your specific requirements:

1. In `rsync_from_gcp.sh` and `rsync_to_gcp.sh`:
   - Update `REMOTE_HOST` with the actual IP of your GCP instance
   - Verify `SOURCE_DIR` and `REMOTE_DIR` paths
   - Check the SSH key path

2. In `rsync_daemon_setup.sh`:
   - Adjust `MODULE_NAME` if needed
   - Verify `DATA_PATH` points to your data volume
   - Consider changing the port if 873 is blocked

3. In `rsync_monitor.sh`:
   - Set `INTERVAL` to your preferred monitoring frequency
   - Set `DURATION` if you want monitoring to stop after a certain time
   - Add an email address to `NOTIFY_EMAIL` if you want notifications

## Usage Examples

### Setting up rsync daemon and monitoring

```bash
# First, set up the rsync daemon
./rsync_daemon_setup.sh

# Then start monitoring in a separate terminal/screen session
./rsync_monitor.sh
```

### Transferring data from GCP to IBM Cloud

```bash
# Edit the script first to update the GCP instance IP
nano rsync_from_gcp.sh

# Then run the transfer
./rsync_from_gcp.sh
```

### Transferring data from IBM Cloud to GCP

```bash
# Edit the script first to update the GCP instance IP
nano rsync_to_gcp.sh

# Then run the transfer
./rsync_to_gcp.sh
```

## Notes

- The data volume on adapt3 contains approximately 1.1TB of data
- For large transfers, consider using screen or tmux to keep the transfer running if your SSH connection drops
- The rsync daemon provides better performance for large transfers compared to regular rsync over SSH

## Troubleshooting

If you encounter issues:

1. Check the rsync logs in `/root/rsync_logs/`
2. Verify network connectivity between the instances
3. Ensure the destination has enough disk space
4. Check that SSH keys are properly configured