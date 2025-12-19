# GDRIVE BACKUP Project Context

## Purpose
To provide automated, continuous backup of critical GCP server data to OneDrive storage using rsync and systemd services.

## Problems Solved
- Ensures data persistence and disaster recovery
- Provides real-time backup of critical data
- Minimizes data loss risk through continuous synchronization
- Enables easy data recovery through cloud storage

## Expected Operation
1. Monitor specified directories (starting with /data/ax) for changes
2. Automatically sync changes to OneDrive storage
3. Run as a persistent systemd service
4. Provide logging and monitoring capabilities
5. Handle failures gracefully with automatic restarts

## Key Requirements
- Real-time backup using rsync
- Event-driven synchronization for efficiency
- Systemd service for persistent operation
- Proper logging and monitoring
- Error handling and recovery