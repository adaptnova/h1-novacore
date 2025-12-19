# SSH Key Setup Instructions

This document provides instructions for adding the newly generated SSH key to the existing servers.

## Prerequisites

- SSH access to the servers with an existing SSH key (e.g., "chase-key")
- The `add_ssh_key.sh` script

## Server Information

| Server | IP Address | Floating IP |
|--------|------------|-------------|
| ethos | 10.240.0.5 | 150.240.71.35 |
| dataops-primary | 10.240.0.6 | - |
| dataops-timeseries | 10.240.0.8 | - |
| dataops-vector | 10.240.0.7 | - |

## Steps for Adding SSH Key to Servers

### For Ethos Server

1. Copy the `add_ssh_key.sh` script to the Ethos server:
   ```bash
   scp -i /path/to/chase-key add_ssh_key.sh root@150.240.71.35:/tmp/
   ```

2. SSH into the Ethos server:
   ```bash
   ssh -i /path/to/chase-key root@150.240.71.35
   ```

3. Run the script:
   ```bash
   cd /tmp
   chmod +x add_ssh_key.sh
   ./add_ssh_key.sh
   ```

4. Verify that the SSH key was added:
   ```bash
   cat /root/.ssh/authorized_keys
   ```

### For DataOps Servers

For each DataOps server, you'll need to SSH to the server using its internal IP address from the Ethos server or another server that has access to the internal network.

1. From the Ethos server, copy the `add_ssh_key.sh` script to the DataOps server:
   ```bash
   # For dataops-primary
   scp /tmp/add_ssh_key.sh root@10.240.0.6:/tmp/
   
   # For dataops-timeseries
   scp /tmp/add_ssh_key.sh root@10.240.0.8:/tmp/
   
   # For dataops-vector
   scp /tmp/add_ssh_key.sh root@10.240.0.7:/tmp/
   ```

2. SSH into the DataOps server:
   ```bash
   # For dataops-primary
   ssh root@10.240.0.6
   
   # For dataops-timeseries
   ssh root@10.240.0.8
   
   # For dataops-vector
   ssh root@10.240.0.7
   ```

3. Run the script:
   ```bash
   cd /tmp
   chmod +x add_ssh_key.sh
   ./add_ssh_key.sh
   ```

4. Verify that the SSH key was added:
   ```bash
   cat /root/.ssh/authorized_keys
   ```

## Verifying SSH Access with New Key

After adding the SSH key to all servers, you can verify that you can SSH to the servers using the new key:

```bash
# For Ethos server
ssh -i ./id_rsa root@150.240.71.35

# For DataOps servers (from a server with access to the internal network)
ssh -i ./id_rsa root@10.240.0.6
ssh -i ./id_rsa root@10.240.0.8
ssh -i ./id_rsa root@10.240.0.7
```

## Troubleshooting

If you encounter any issues during the SSH key setup process, check the following:

1. Ensure that the `add_ssh_key.sh` script has execute permissions (`chmod +x add_ssh_key.sh`)
2. Verify that the SSH key is correctly formatted in the script
3. Check for any error messages in the script output
4. Verify that the authorized_keys file has the correct permissions (600)
5. Verify that the .ssh directory has the correct permissions (700)