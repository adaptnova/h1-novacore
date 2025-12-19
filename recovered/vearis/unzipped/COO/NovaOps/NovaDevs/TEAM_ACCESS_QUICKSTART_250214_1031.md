# Nova Team Access Quick-Start Guide
Date: February 14, 2025 10:34 MST
Author: V.I. (Vaeris Intelligence)
Status: ACTIVE

## System Access Overview

### 1. Direct System Access (Primary Method)
```bash
# Basic access pattern with IAP tunnel
gcloud compute ssh [instance-name] --zone=[zone] --tunnel-through-iap

# Example for Ethos server
gcloud compute ssh ethos-a3-ml --zone=us-central1-a --tunnel-through-iap
```

### 2. System Capabilities
- Full system access with sudo privileges
- Unlimited process creation
- Large file descriptor limits (1048576)
- Unlimited memory locking
- Direct hardware access
- GPU access (on ML instances)

### 3. Development Environment
- VS Code with remote capabilities
- Chrome Remote Desktop for GUI
- GNOME Desktop environment
- System monitoring tools (htop, iotop, iftop)
- Redis for team communication

## Initial Setup

### 1. Request Access
1. Provide GitHub username to admin
2. Receive IAM role assignment
3. Verify access with test connection

### 2. Environment Setup
```bash
# Clone environment setup script
git clone [repo-url]
cd [repo-dir]

# Make script executable
chmod +x scripts/setup_team_environment.sh

# Run setup script
./scripts/setup_team_environment.sh
```

### 3. Security Requirements
- Use strong SSH keys
- Enable 2FA for Google Cloud Console
- Keep access tokens secure
- Never share credentials
- Follow security best practices

## Server-Specific Access

### Ethos Server (ML/AI)
- Instance: `ethos-a3-ml` in `us-central1-a`
- Hardware: 8x H100-80GB GPUs
- Environment: CUDA 12.4, PyTorch
- Purpose: ML model training and inference

### Development Server
- Details to be provided
- Testing environment
- Staging deployment
- Development tools

## Common Operations

### 1. System Monitoring
```bash
# Check system resources
htop

# Monitor I/O operations
iotop

# Monitor network traffic
iftop

# Check GPU status (ML instances)
nvidia-smi
```

### 2. Redis Operations
```bash
# Check Redis status
sudo systemctl status redis-server

# Redis CLI
redis-cli

# Monitor Redis
redis-cli monitor
```

### 3. Development Tools
- VS Code Server: http://localhost:8080
- Chrome Remote Desktop
- GNOME Desktop environment
- System utilities

## Remote Development

### 1. VS Code Remote Setup
1. Install "Remote - SSH" extension
2. Configure SSH config:
   ```bash
   # Add to ~/.ssh/config
   Host ethos-ml
     HostName ethos-a3-ml
     ProxyCommand gcloud compute start-iap-tunnel ethos-a3-ml %p --zone=us-central1-a
     User [your-username]
   ```

### 2. Chrome Remote Desktop
1. Visit https://remotedesktop.google.com/headless
2. Follow setup prompts
3. Set access PIN
4. Connect through Chrome Remote Desktop

## Troubleshooting

### 1. System Issues
- Check system logs: `journalctl -xe`
- Monitor resources: `htop`
- Check disk space: `df -h`
- Verify services: `systemctl status [service]`

### 2. Access Problems
- Verify IAM permissions
- Check IAP tunnel status
- Ensure correct instance name/zone
- Verify SSH keys

### 3. Development Environment
- Check VS Code Server: `systemctl status code-server@$USER`
- Verify Redis: `redis-cli ping`
- Check desktop: `systemctl status gdm3`

## Support
- Technical issues: File GitHub issue
- Access problems: Contact admin
- General questions: Team chat

## Security Notes
- All access is logged
- Use IAP tunnel exclusively
- Keep credentials secure
- Report security concerns immediately
- Follow system security protocols

Remember: You have full system access - use it responsibly!