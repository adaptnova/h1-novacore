# User Setup Instructions for CloudOps Fleet Servers

This document provides instructions for setting up users on the Ethos and DataOps servers.

## Server Information

| Server | IP Address | User to Create | Password |
|--------|------------|----------------|----------|
| ethos | 10.240.0.5 | ethos | x |
| dataops-primary | 10.240.0.6 | vertex | x |
| dataops-timeseries | 10.240.0.8 | vertex | x |
| dataops-vector | 10.240.0.7 | vertex | x |

## Setup Instructions

### Prerequisites

- SSH access to the servers with root privileges
- The setup scripts (`ethos_setup.sh` and `dataops_setup.sh`)

### Steps for Ethos Server

1. Copy the `ethos_setup.sh` script to the Ethos server:
   ```bash
   scp ethos_setup.sh root@10.240.0.5:/tmp/
   ```

2. SSH into the Ethos server:
   ```bash
   ssh root@10.240.0.5
   ```

3. Run the setup script:
   ```bash
   cd /tmp
   chmod +x ethos_setup.sh
   ./ethos_setup.sh
   ```

4. Verify the user setup:
   ```bash
   su - ethos
   sudo whoami  # Should return "root" without asking for a password
   ```

### Steps for DataOps Servers

For each DataOps server (dataops-primary, dataops-timeseries, dataops-vector), follow these steps:

1. Copy the `dataops_setup.sh` script to the DataOps server:
   ```bash
   # For dataops-primary
   scp dataops_setup.sh root@10.240.0.6:/tmp/
   
   # For dataops-timeseries
   scp dataops_setup.sh root@10.240.0.8:/tmp/
   
   # For dataops-vector
   scp dataops_setup.sh root@10.240.0.7:/tmp/
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

3. Run the setup script:
   ```bash
   cd /tmp
   chmod +x dataops_setup.sh
   ./dataops_setup.sh
   ```

4. Verify the user setup:
   ```bash
   su - vertex
   sudo whoami  # Should return "root" without asking for a password
   ```

## Troubleshooting

If you encounter any issues during the setup process, check the following:

1. Ensure you have root access to the servers
2. Verify that the scripts have execute permissions (`chmod +x script.sh`)
3. Check for any error messages in the script output
4. Verify that the user was created and has sudo privileges

## Security Considerations

- The password "x" is used for simplicity but should be changed to a more secure password in a production environment
- Consider using SSH key-based authentication instead of password authentication for better security
- Regularly audit user accounts and permissions to ensure security