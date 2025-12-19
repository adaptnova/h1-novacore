# Azure Backup System - System Patterns

## Architecture Patterns

### Service Architecture
1. Systemd Service
   - Type: oneshot
   - Controlled by timer unit
   - Environment-based configuration
   - Proper security settings

2. File Organization
   - Scripts in /data/ax/CloudOps/azure
   - Logs in /logs/backup
   - Configuration via environment variables

### Security Patterns
1. Authentication
   - SAS token-based authentication
   - Token stored in environment variable
   - No direct Azure credentials stored

2. Permissions
   - Principle of least privilege
   - Directory permissions: 750
   - File permissions: 640
   - Ownership: x:x

### Backup Patterns
1. Exclusion Strategy
   ```
   Excluded Paths:
   - */tmp/*
   - */cache/*
   - */proc/*
   - */sys/*
   - */dev/*
   - */.env
   - */__pycache__/*
   - */node_modules/*
   - */configs/*
   - */docker/volumes/*
   - */docker/overlay2/*
   - */docker/containers/*
   - */docker/image/*
   - */docker/builder/*
   - */docker/buildkit/*
   - */docker/tmp/*
   - */docker/swarm/*
   - */minikube/*
   ```

2. Resource Management
   - IOSchedulingClass: best-effort
   - IOSchedulingPriority: 7
   - CPUSchedulingPolicy: batch
   - Nice: 19
   - Memory limits enforced

### Error Handling
1. Logging
   - Separate output and error logs
   - Timestamp-based log files
   - Automatic log rotation

2. Cleanup
   - Automatic cleanup of old logs
   - Cleanup of temporary files
   - Process termination handling

## Technical Decisions
1. Using azcopy over az cli
   - Better performance
   - Resume capability
   - Parallel transfer support

2. Environment Variables
   - Flexible configuration
   - Secure credential storage
   - Easy to modify without code changes

3. Systemd Integration
   - Reliable scheduling
   - Proper service management
   - Dependency handling

4. Docker Awareness
   - Smart exclusion of Docker paths
   - Prevents unnecessary backup of ephemeral data
   - Reduces backup size and time