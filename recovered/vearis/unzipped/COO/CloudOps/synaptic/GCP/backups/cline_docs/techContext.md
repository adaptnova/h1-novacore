# Technical Implementation Notes

## Backup System Status

### Current Setup
- Using rclone with Google Drive for cloud backup
- Service account authentication configured
- Systemd service for continuous operation

### Known Issues
- Bandwidth limitations affecting sync speed (~1 MiB/s)
- Need networking team to investigate bandwidth constraints
- Initial sync of /data/ax (~4.7 GiB) estimated at >1 hour at current speeds

### Next Steps
1. Await networking team's bandwidth optimization
2. Consider implementing:
   - Bandwidth scheduling
   - Incremental backup strategy
   - Compression options
   - Chunked transfer approach

### Configuration
- Source: /data/ax
- Destination: gdrive:/backups/ax
- Using service account authentication
- Event-driven monitoring implemented
# Technical Context

## Technologies Used

### Core Technologies
- rsync: File synchronization tool
- inotify-tools: File system monitoring
- systemd: Service management
- OneDrive: Cloud storage destination

### Development Environment
- Linux-based system
- Bash scripting
- System service management
- Cloud storage integration

## Technical Requirements

### System Dependencies
- rsync
- inotify-tools
- rclone (for OneDrive mounting)
- systemd

### Configuration Requirements
1. OneDrive Authentication
   - Rclone configuration
   - Mount point setup
   - Access permissions

2. System Permissions
   - Read access to source directories
   - Write access to OneDrive mount
   - Service execution permissions

## Development Setup

### Installation Steps
1. Install required packages
   ```bash
   sudo apt update
   sudo apt install -y rsync inotify-tools rclone
   ```

2. Configure OneDrive
   ```bash
   rclone config
   # Set up OneDrive remote
   ```

3. Create mount point
   ```bash
   sudo mkdir -p /mnt/onedrive
   ```

### Service Configuration
- Systemd service file location: /etc/systemd/system/
- Backup script location: /usr/local/bin/
- Log directory: /var/log/

## Technical Constraints
- Network bandwidth requirements
- Storage capacity limitations
- File system monitoring limits
- Service restart policies