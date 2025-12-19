# SSH Connection Guide for IBM Cloud Fleet

## Ethos Server

### Connection Details

| Property | Value |
|----------|-------|
| Server Name | ethos |
| Floating IP | 52.118.146.160 |
| Internal IP | 10.240.0.15 |
| SSH Key | ibm-admin_rsa |

### SSH Commands

```bash
# Connect as root
ssh -i /home/x/.ssh/ibm-admin_rsa root@52.118.146.160

# Connect as ethos user
ssh -i /home/x/.ssh/ibm-admin_rsa ethos@52.118.146.160

# Connect as x user
ssh -i /home/x/.ssh/ibm-admin_rsa x@52.118.146.160
```

### Using SSH Config

If you've added the SSH config entries, you can use these shortcuts:

```bash
# Connect as root
ssh ethos-root

# Connect as ethos user
ssh ethos

# Connect as x user
ssh ethos-x
```

## DataOps Servers

### DataOps Primary

| Property | Value |
|----------|-------|
| Server Name | dataops-primary |
| Internal IP | 10.240.0.6 |
| SSH Key | ibm-admin_rsa |

### SSH Commands

```bash
# Connect as root
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.0.6

# Connect as vertex user
ssh -i /home/x/.ssh/ibm-admin_rsa vertex@10.240.0.6

# Connect as x user
ssh -i /home/x/.ssh/ibm-admin_rsa x@10.240.0.6
```

### Using SSH Config

If you've added the SSH config entries, you can use these shortcuts:

```bash
# Connect as root
ssh dataops-primary-root

# Connect as vertex user
ssh dataops-primary

# Connect as x user
ssh dataops-primary-x
```

### DataOps Timeseries

| Property | Value |
|----------|-------|
| Server Name | dataops-timeseries |
| Internal IP | 10.240.0.17 |
| SSH Key | ibm-admin_rsa |

### SSH Commands

```bash
# Connect as root
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.0.17

# Connect as vertex user
ssh -i /home/x/.ssh/ibm-admin_rsa vertex@10.240.0.17

# Connect as x user
ssh -i /home/x/.ssh/ibm-admin_rsa x@10.240.0.17
```

### Using SSH Config

If you've added the SSH config entries, you can use these shortcuts:

```bash
# Connect as root
ssh dataops-timeseries-root

# Connect as vertex user
ssh dataops-timeseries

# Connect as x user
ssh dataops-timeseries-x
```

### DataOps Vector

| Property | Value |
|----------|-------|
| Server Name | dataops-vector |
| Internal IP | 10.240.0.18 |
| SSH Key | ibm-admin_rsa |

### SSH Commands

```bash
# Connect as root
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.0.18

# Connect as vertex user
ssh -i /home/x/.ssh/ibm-admin_rsa vertex@10.240.0.18

# Connect as x user
ssh -i /home/x/.ssh/ibm-admin_rsa x@10.240.0.18
```

### Using SSH Config

If you've added the SSH config entries, you can use these shortcuts:

```bash
# Connect as root
ssh dataops-vector-root

# Connect as vertex user
ssh dataops-vector

# Connect as x user
ssh dataops-vector-x
```

## User Information

### Ethos Server

| Username | Password | Sudo Access |
|----------|----------|-------------|
| root | N/A (SSH key authentication) | N/A |
| ethos | x | Yes (NOPASSWD) |
| x | x | Yes (NOPASSWD) |

### DataOps Servers

| Username | Password | Sudo Access |
|----------|----------|-------------|
| root | N/A (SSH key authentication) | N/A |
| vertex | x | Yes (NOPASSWD) |
| x | x | Yes (NOPASSWD) |

## SSH Key Location

The SSH key is located at:

```
/home/x/.ssh/ibm-admin_rsa
```

Make sure the permissions are set correctly:

```bash
chmod 600 /home/x/.ssh/ibm-admin_rsa