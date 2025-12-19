#!/bin/bash

# AWS Backup Configuration - Test Version
# Created: 2025-01-24
# Version: 1.0.0

# Directory Structure
export CLOUDOPS_BASE="/data/cloudops"
export LOGS_BASE="/logs/cloudops"

# AWS Specific Paths
export AWS_BASE="${CLOUDOPS_BASE}/aws"
export AWS_LOGS="${AWS_LOGS}/aws"

# Backup Paths
export BACKUP_BASE="${AWS_BASE}/backups"
export BACKUP_LOGS="${AWS_LOGS}/backups"
export DISK_BACKUP_DIR="${BACKUP_BASE}/disks/data"
export TEMP_BACKUP_DIR="/data/tmp"  # Changed to /data/tmp as requested
export DISK_BACKUP_LOGS="${BACKUP_LOGS}/disks/data"

# AWS Credentials per interface
# ens3 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens3_profile
aws configure set aws_secret_access_key "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" --profile ens3_profile
aws configure set region "us-west-2" --profile ens3_profile

# ens4 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens4_profile
aws configure set aws_secret_access_key "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" --profile ens4_profile
aws configure set region "us-west-2" --profile ens4_profile

# ens5 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens5_profile
aws configure set aws_secret_access_key "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" --profile ens5_profile
aws configure set region "us-west-2" --profile ens5_profile

# ens6 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens6_profile
aws configure set aws_secret_access_key "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" --profile ens6_profile
aws configure set region "us-west-2" --profile ens6_profile

# ens7 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens7_profile
aws configure set aws_secret_access_key "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" --profile ens7_profile
aws configure set region "us-west-2" --profile ens7_profile

# ens8 profile
aws configure set aws_access_key_id "AKIAYUQGTD63FE2WLVHI" --profile ens8_profile
aws configure set aws_secret_access_key "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" --profile ens8_profile
aws configure set region "us-west-2" --profile ens8_profile

# Configure interface routing for AWS endpoints
for interface in ens3 ens4 ens5 ens6 ens7 ens8; do
    # Get interface IP
    ip=$(ip addr show $interface | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    if [ ! -z "$ip" ]; then
        # Add specific route for S3 endpoint through this interface
        ip route add ${BUCKET_NAME}.s3.us-west-2.amazonaws.com via $ip dev $interface 2>/dev/null || true
    fi
done

# Set default interface for fallback
export AWS_DEFAULT_PROFILE="ens3_profile"

# Configure AWS CLI for optimal multipart upload
export AWS_MAX_CONCURRENT_REQUESTS=20
export AWS_MULTIPART_CHUNKSIZE=100MB

# S3 Configuration
export BUCKET_NAME="hourly-backup-593793064886"
export BACKUP_RETENTION_DAYS=7
export STORAGE_CLASS="STANDARD_IA"
export S3_PREFIX="backups/disks/data"

# Source Configuration - Changed to backup entire /data disk
export SOURCE_DIR="/data/test_backup"  # For initial test
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
mkdir -p "${TEMP_BACKUP_DIR}"  # Create temp directory
for type in "${LOG_TYPES[@]}"; do
    mkdir -p "${DISK_BACKUP_LOGS}/${type}"
done

# Create backup metadata directory
mkdir -p "${DISK_BACKUP_DIR}/metadata"