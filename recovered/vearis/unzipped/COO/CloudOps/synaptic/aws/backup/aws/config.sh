#!/bin/bash

# AWS Backup Configuration
# Created: 2025-01-24
# Version: 1.0.0

# Directory Structure
export CLOUDOPS_BASE="/data/cloudops"
export LOGS_BASE="/logs/cloudops"

# AWS Specific Paths
export AWS_BASE="${CLOUDOPS_BASE}/aws"
export AWS_LOGS="${LOGS_BASE}/aws"

# Backup Paths
export BACKUP_BASE="${AWS_BASE}/backups"
export BACKUP_LOGS="${AWS_LOGS}/backups"
export DISK_BACKUP_DIR="${BACKUP_BASE}/disks/data"
export TEMP_BACKUP_DIR="/data/backup_temp"  # Direct path to temp directory
export DISK_BACKUP_LOGS="${BACKUP_LOGS}/disks/data"

# AWS Credentials per interface
# eth0 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile eth0_profile
aws configure set aws_secret_access_key "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" --profile eth0_profile
aws configure set region "us-west-2" --profile eth0_profile

# eth1 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile eth1_profile
aws configure set aws_secret_access_key "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" --profile eth1_profile
aws configure set region "us-west-2" --profile eth1_profile

# eth2 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile eth2_profile
aws configure set aws_secret_access_key "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" --profile eth2_profile
aws configure set region "us-west-2" --profile eth2_profile

# eth3 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile eth3_profile
aws configure set aws_secret_access_key "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" --profile eth3_profile
aws configure set region "us-west-2" --profile eth3_profile

# Configure interface routing for AWS endpoints
for interface in eth0 eth1 eth2 eth3; do
    # Get interface IP
    ip=$(ip addr show $interface | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    if [ ! -z "$ip" ]; then
        # Add specific route for S3 endpoint through this interface
        ip route add ${BUCKET_NAME}.s3.us-west-2.amazonaws.com via $ip dev $interface 2>/dev/null || true
    fi
done

# Set default interface for fallback
export AWS_DEFAULT_PROFILE="eth0_profile"

# Configure AWS CLI for optimal multipart upload
export AWS_MAX_CONCURRENT_REQUESTS=20
export AWS_MULTIPART_CHUNKSIZE=100MB

# S3 Configuration
export BUCKET_NAME="hourly-backup-593793064886"
export BACKUP_RETENTION_DAYS=7
export STORAGE_CLASS="STANDARD_IA"
export S3_PREFIX="backups/disks/data"

# Source Configuration - Changed to backup entire /data disk
export SOURCE_DIR="/data"  # Full /data backup
export EXCLUDE_PATTERNS=(
    # System and temp files
    "*.tmp"
    "*.log"
    ".git/*"
    "node_modules/*"
    "*.pyc"
    # System directories
    "proc/*"
    "sys/*"
    "dev/*"
    "run/*"
    "tmp/*"
    "__pycache__/*"
    "venv/*"
    # Exclude backup temp and logs
    "backup_temp/*"
    "cloudops/aws/backups/*"
    "logs/cloudops/*"
)

# Logging Configuration
export LOG_TYPES=(
    "info"
    "error"
    "debug"
    "audit"
)

# Create required directories
for type in "${LOG_TYPES[@]}"; do
    mkdir -p "${DISK_BACKUP_LOGS}/${type}"
done

# Create backup metadata directory
mkdir -p "${DISK_BACKUP_DIR}/metadata"
mkdir -p "${TEMP_BACKUP_DIR}"  # Create temp directory