# CloudOps Fleet - IBM Cloud Infrastructure Management

This repository contains scripts and documentation for managing IBM Cloud infrastructure for the CloudOps Fleet project.

## Project Overview

The CloudOps Fleet project aims to manage IBM Cloud infrastructure efficiently and securely. It involves inventory management, user access control, and SSH configuration for server access.

## Repository Structure

### Scripts

- `setup_users.sh`: Main script to set up users on all servers (requires direct SSH access)
- `ethos_setup.sh`: Script to set up the "ethos" user on the Ethos server
- `dataops_setup.sh`: Script to set up the "vertex" user on DataOps servers
- `verify_connectivity.sh`: Script to verify connectivity to all servers after setup

### Configuration

- `ssh_config`: SSH configuration file for easy access to all servers

### Documentation

- `user_setup_instructions.md`: Instructions for setting up users on the servers
- `ssh_config_instructions.md`: Instructions for setting up SSH configuration
- `memory-bank/`: Directory containing project documentation and context
  - `productContext.md`: High-level overview of the project
  - `activeContext.md`: Current status, recent changes, and open questions
  - `progress.md`: Task tracking
  - `decisionLog.md`: Record of architectural and implementation decisions
  - `systemPatterns.md`: Documentation of recurring patterns and standards
  - `ibm_cloud_inventory.md`: Inventory of IBM Cloud assets

## Server Information

| Server | IP Address | OS | Profile |
|--------|------------|-------|--------|
| ethos | 10.240.0.5 | Debian 12.9 | gx3-48x240x2l40s |
| dataops-primary | 10.240.0.6 | Debian 12.9 | bx2-8x32 |
| dataops-timeseries | 10.240.0.8 | Debian 12.9 | bx2-8x32 |
| dataops-vector | 10.240.0.7 | Debian 12.9 | bx2-8x32 |

## Implementation Plan

1. **IBM Cloud Asset Inventory** ✓
   - Inventory of all IBM Cloud assets
   - Identification of target servers

2. **User Setup**
   - Create user "ethos" with password "x" on Ethos server (with sudo and NOPASSWD)
   - Create user "vertex" with password "x" on 3 DataOps servers (with sudo and NOPASSWD)

3. **SSH Configuration**
   - SSH key management
   - SSH config creation for each server

4. **Connectivity Verification**
   - Test SSH access to all servers with new users
   - Verify sudo privileges are working correctly
   - Confirm all required functionality is operational

5. **Documentation**
   - Update Memory Bank with all details
   - Document final implementation results

## Usage

1. **User Setup**:
   ```bash
   # For Ethos server
   scp ethos_setup.sh root@10.240.0.5:/tmp/
   ssh root@10.240.0.5 "cd /tmp && chmod +x ethos_setup.sh && ./ethos_setup.sh"
   
   # For DataOps servers
   scp dataops_setup.sh root@10.240.0.6:/tmp/
   ssh root@10.240.0.6 "cd /tmp && chmod +x dataops_setup.sh && ./dataops_setup.sh"
   # Repeat for other DataOps servers
   ```

2. **SSH Configuration**:
   ```bash
   # Add the SSH config to your ~/.ssh/config file
   cat ssh_config >> ~/.ssh/config
   chmod 600 ~/.ssh/config
   ```

3. **Connectivity Verification**:
   ```bash
   # Verify connectivity to all servers
   ./verify_connectivity.sh
   ```

## Security Considerations

- The password "x" is used for simplicity but should be changed to a more secure password in a production environment
- Consider using SSH key-based authentication instead of password authentication for better security
- Regularly audit user accounts and permissions to ensure security

## Author

Zorion (IBM Cloud Strategist & Provisioning Engineer)