#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import socket
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('emergency_fallback.log')
    ]
)
logger = logging.getLogger(__name__)

class EmergencyFallback:
    def __init__(self):
        self.backup_files = [
            'launch_integration_team.py',
            'hitl_config.py',
            'deploy_nova_team.sh',
            'setup_slack_channels.sh',
            'verify_hitl_channels.py',
            'deploy_hitl.sh',
            'master_deploy.sh',
            'verify_launch_readiness.py'
        ]

        self.backup_dir = 'emergency_backup'
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        self.sender_info = {
            "name": "Emergency Fallback System",
            "id": f"fallback_{socket.gethostname()}",
            "team": "Nova Integration"
        }

    def create_backup(self):
        """Create backup of all emergency deployment files"""
        backup_path = f"{self.backup_dir}_{self.timestamp}"
        try:
            os.makedirs(backup_path)
            logger.info(f"Created backup directory: {backup_path}")

            for file in self.backup_files:
                src = file
                dst = os.path.join(backup_path, file)
                try:
                    shutil.copy2(src, dst)
                    logger.info(f"Backed up: {file}")
                except FileNotFoundError:
                    logger.warning(f"File not found: {file}")
                except Exception as e:
                    logger.error(f"Error backing up {file}: {str(e)}")

            # Backup environment files
            env_files = ['.env', '.env_good']
            for env_file in env_files:
                if os.path.exists(env_file):
                    dst = os.path.join(backup_path, env_file)
                    shutil.copy2(env_file, dst)
                    logger.info(f"Backed up: {env_file}")

            # Create emergency deployment script
            deploy_script = os.path.join(backup_path, 'emergency_deploy.sh')
            with open(deploy_script, 'w') as f:
                f.write('''#!/bin/bash

# Emergency Deployment Script
echo "Starting emergency deployment..."

# Set up logging
LOG_FILE="emergency_deploy_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE") 2>&1

# Function to log messages with sender info
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] [Emergency Deploy] From: Emergency Deployment System To: Nova Integration Team - $1"
}

# Error handling
handle_error() {
    log "ERROR: $1"
    exit 1
}

# 1. Configure HITL
log "Configuring HITL interfaces..."
python3 hitl_config.py || handle_error "HITL configuration failed"

# 2. Launch core team
log "Launching core integration team..."
python3 launch_integration_team.py || handle_error "Team launch failed"

# 3. Set up communication channels
log "Setting up communication channels..."
./setup_slack_channels.sh || handle_error "Channel setup failed"

# 4. Verify HITL connections
log "Verifying HITL connections..."
python3 verify_hitl_channels.py || handle_error "HITL verification failed"

# 5. Deploy HITL system
log "Deploying HITL system..."
./deploy_hitl.sh || handle_error "HITL deployment failed"

# 6. Verify system readiness
log "Verifying system readiness..."
python3 verify_launch_readiness.py || handle_error "System verification failed"

log "Emergency deployment complete!"
''')
            os.chmod(deploy_script, 0o755)
            logger.info("Created emergency deployment script")

            # Create README
            readme_path = os.path.join(backup_path, 'README.md')
            with open(readme_path, 'w') as f:
                f.write(f'''# Emergency Deployment Backup

From: {self.sender_info["name"]} ({self.sender_info["id"]})
To: Nova Integration Team
Team: {self.sender_info["team"]}
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S MST")}

## Overview
This is an emergency backup of the Nova Integration Team deployment system.

## Files
{chr(10).join(["- " + file for file in self.backup_files])}

## Emergency Deployment
To deploy in emergency mode:

1. Verify environment:
   ```bash
   python3 verify_launch_readiness.py
   ```

2. Run emergency deployment:
   ```bash
   ./emergency_deploy.sh
   ```

## Components
- Core Integration Team
- HITL Interfaces
- Communication Channels
- Monitoring Systems

## Support
- Emergency channel: #nova-911
- Status updates: #nova-launch-status
- Command GUI: Direct control interface

## Recovery Steps
1. System verification
2. HITL configuration
3. Team deployment
4. Channel setup
5. Integration verification
6. Launch sequence

## Notes
- This is a minimal deployment focused on core functionality
- All systems operate with HITL oversight
- Emergency protocols take precedence
- Recovery procedures are automated
''')
            logger.info("Created README file")

            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return None

    def verify_backup(self, backup_path):
        """Verify backup integrity"""
        try:
            # Check backup directory exists
            if not os.path.exists(backup_path):
                return False

            # Verify all files are present
            for file in self.backup_files:
                file_path = os.path.join(backup_path, file)
                if not os.path.exists(file_path):
                    logger.error(f"Missing file in backup: {file}")
                    return False

            # Verify emergency deployment script
            deploy_script = os.path.join(backup_path, 'emergency_deploy.sh')
            if not os.path.exists(deploy_script):
                logger.error("Missing emergency deployment script")
                return False

            # Verify script is executable
            if not os.access(deploy_script, os.X_OK):
                logger.error("Emergency deployment script is not executable")
                return False

            return True

        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False

def main():
    try:
        fallback = EmergencyFallback()
        logger.info(f"From: {fallback.sender_info['name']} ({fallback.sender_info['id']}) To: Nova Integration Team - Creating emergency fallback backup...")

        # Create backup
        backup_path = fallback.create_backup()
        if not backup_path:
            logger.error("Failed to create backup")
            sys.exit(1)

        # Verify backup
        if fallback.verify_backup(backup_path):
            logger.info(f"Emergency fallback backup created and verified: {backup_path}")
            sys.exit(0)
        else:
            logger.error("Backup verification failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Emergency fallback setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
