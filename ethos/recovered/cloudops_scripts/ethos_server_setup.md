# Ethos Server Setup Documentation

## Server Information

| Property | Value |
|----------|-------|
| Server Name | ethos |
| Floating IP | 52.118.146.160 |
| Internal IP | 10.240.0.15 |
| Profile | gx3-48x240x2l40s |
| vCPUs | 48 |
| Memory | 240 GB |
| GPU | 2x NVIDIA L40S (48 GB) |
| OS | Debian 12.9 |
| SSH Key | ibm-admin |

## Storage Configuration

| Device | Size | Mount Point | Purpose |
|--------|------|-------------|---------|
| /dev/vdd | 50 GB | /data | Data storage |
| /dev/vde | 50 GB | /logs | Log storage |
| /dev/vdf | 1 TB | /llms | LLM storage |

## User Accounts

| Username | Password | Sudo Access |
|----------|----------|-------------|
| root | N/A (SSH key authentication) | N/A |
| ethos | x | Yes (NOPASSWD) |
| x | x | Yes (NOPASSWD) |

## SSH Access

### Using SSH Config

Add the contents of the `ethos_ssh_config` file to your `~/.ssh/config` file:

```bash
cat ethos_ssh_config >> ~/.ssh/config
```

Then you can connect to the server using:

```bash
# Connect as root
ssh ethos-root

# Connect as ethos user
ssh ethos

# Connect as x user
ssh ethos-x
```

### Direct SSH Command

```bash
# Connect as root
ssh -i /home/x/.ssh/ibm-admin_rsa root@52.118.146.160

# Connect as ethos user
ssh -i /home/x/.ssh/ibm-admin_rsa ethos@52.118.146.160

# Connect as x user
ssh -i /home/x/.ssh/ibm-admin_rsa x@52.118.146.160
```

## Setup Scripts

The following scripts were created to set up the server:

1. `install_packages.sh` - Installs necessary packages (xfsprogs)
2. `format_and_mount_disks.sh` - Formats and mounts the data, logs, and llms volumes
3. `create_users.sh` - Creates the ethos and x users with sudo NOPASSWD privileges
4. `check_network_interfaces.sh` - Checks if all network interfaces are attached

All these scripts have been executed on the server, and the setup is complete. The server has:
- XFS formatted volumes mounted at /data, /logs, and /llms
- Users "ethos" and "x" with sudo NOPASSWD privileges
- SSH key authentication configured for all users

## Network Interfaces

Currently, the server has 1 network interface (eth0). We attempted to add additional network interfaces, but encountered issues with the IBM Cloud CLI. This does not affect the functionality of the server, but you may want to add additional network interfaces through the IBM Cloud web console if needed.