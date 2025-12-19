# System Architecture and Patterns

## Core Components

### 1. Backup Service
- Systemd service for persistent operation
- Event-driven monitoring using inotify
- Rsync for efficient file synchronization
- Logging and monitoring integration

### 2. Architecture Patterns
- Event-driven architecture for real-time backup
- Microservice design for backup component
- Modular script structure for maintainability
- Stateless operation with persistent logging

## Technical Decisions

### 1. Using Rsync
- Efficient delta transfers
- Built-in compression
- Reliable file synchronization
- Extensive logging capabilities

### 2. Event-Driven Approach
- Using inotify for real-time change detection
- Reduces unnecessary scanning
- Minimizes resource usage
- Improves backup latency

### 3. Systemd Integration
- Native Linux service management
- Automatic restart capabilities
- Dependency management
- Logging integration with journald

## System Flow
1. inotify monitors source directory
2. File changes trigger rsync operation
3. Rsync performs incremental backup
4. System logs operation status
5. Monitoring reports backup health

## Integration Points
- Source Directory: /data/ax
- Destination: OneDrive mounted location
- System Logging: journald
- Monitoring: System metrics and status