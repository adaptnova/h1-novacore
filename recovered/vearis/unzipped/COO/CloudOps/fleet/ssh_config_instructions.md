# SSH Configuration Instructions for CloudOps Fleet Servers

This document provides instructions for setting up SSH configuration to easily access the Ethos and DataOps servers.

## Prerequisites

- The users must be set up on the servers as described in `user_setup_instructions.md`
- SSH key pair (public and private keys) must be generated on your local machine
- The public key must be added to the authorized_keys file for each user on each server

## SSH Key Generation

If you don't already have an SSH key pair, you can generate one using the following command:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Follow the prompts to complete the key generation process. By default, the keys will be saved in `~/.ssh/id_rsa` (private key) and `~/.ssh/id_rsa.pub` (public key).

## Adding Public Key to Servers

For each server, you need to add your public key to the authorized_keys file for the respective user:

### For Ethos Server

```bash
# Copy your public key to the server
ssh-copy-id ethos@10.240.0.5

# Or manually add it
cat ~/.ssh/id_rsa.pub | ssh ethos@10.240.0.5 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### For DataOps Servers

```bash
# For dataops-primary
ssh-copy-id vertex@10.240.0.6

# For dataops-timeseries
ssh-copy-id vertex@10.240.0.8

# For dataops-vector
ssh-copy-id vertex@10.240.0.7

# Or manually add it to each server
cat ~/.ssh/id_rsa.pub | ssh vertex@10.240.0.6 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
cat ~/.ssh/id_rsa.pub | ssh vertex@10.240.0.8 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
cat ~/.ssh/id_rsa.pub | ssh vertex@10.240.0.7 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## SSH Config Setup

1. Copy the provided `ssh_config` file to your SSH configuration:

```bash
# Backup existing config if needed
cp ~/.ssh/config ~/.ssh/config.backup

# Add the new config (append or create new)
cat ssh_config >> ~/.ssh/config
```

2. Set the correct permissions for the SSH config file:

```bash
chmod 600 ~/.ssh/config
```

## Using the SSH Configuration

Once the SSH configuration is set up, you can easily connect to the servers using their aliases:

```bash
# Connect to Ethos server
ssh ethos

# Connect to DataOps servers
ssh dataops-primary
ssh dataops-timeseries
ssh dataops-vector
```

## Verifying Connectivity

To verify that the SSH configuration is working correctly, try connecting to each server:

```bash
# Test connection to Ethos server
ssh ethos "hostname && whoami"

# Test connection to DataOps servers
ssh dataops-primary "hostname && whoami"
ssh dataops-timeseries "hostname && whoami"
ssh dataops-vector "hostname && whoami"
```

## Troubleshooting

If you encounter any issues with the SSH configuration, check the following:

1. Ensure the users are set up correctly on the servers
2. Verify that your public key is added to the authorized_keys file for each user
3. Check the permissions on the SSH files:
   - `~/.ssh` directory should have permissions 700
   - `~/.ssh/authorized_keys` should have permissions 600
   - `~/.ssh/config` should have permissions 600
   - `~/.ssh/id_rsa` (private key) should have permissions 600
4. Try connecting with verbose output to see detailed information:
   ```bash
   ssh -v ethos
   ```

## Security Considerations

- Keep your private key secure and never share it
- Consider using a passphrase for your SSH key for added security
- Regularly rotate SSH keys as part of your security practices
- Consider using SSH certificates for more advanced security