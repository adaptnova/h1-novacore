# Azure Backup System - Product Context

## Purpose
The Azure Backup System is designed to securely backup critical data from /data directory to Azure Blob Storage, ensuring data persistence and disaster recovery capabilities.

## Problems Solved
1. Data Protection: Ensures critical data is backed up to cloud storage
2. Space Optimization: Excludes unnecessary files (Docker volumes, configs) to save space
3. Security: Uses SAS tokens for secure access to Azure storage
4. Reliability: Handles large-scale data transfers with proper error handling

## Core Functionality
1. Automated backup using systemd timer
2. Secure file transfer using azcopy
3. Intelligent file exclusion for Docker and system files
4. Environment-based configuration
5. Proper logging and monitoring
6. Space optimization by excluding /data/configs (~686G saved)

## Key Features
- Secure authentication using SAS tokens
- Docker-aware exclusions
- Proper permission handling
- Efficient large file transfers
- Comprehensive logging
- Automated cleanup procedures