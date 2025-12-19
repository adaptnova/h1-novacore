# Operations History

# CURRENT SERVER: ADAPT3

## 2025-03-28

### Mail Server Setup on Ethos Server (18:23 MST)
- Operation: Set up mail server on ethos server for a-d-a-p-t.ai domain
- Details:
  * Created open_mail_server_ports_ethos.sh script to open required ports
  * Created check_mail_ports.sh script to verify port status
  * Created configure_dns_records.sh script to configure DNS records
  * Created install_mail_server.sh script to install and configure mail server software
  * Created mail_server_setup_README.md with documentation
  * Opened the following ports:
    - Port 25 (TCP) - SMTP - Receiving mail from other mail servers
    - Port 465 (TCP) - SMTPS - Secure SMTP (legacy)
    - Port 587 (TCP) - Submission - Sending mail (with authentication)
    - Port 143 (TCP) - IMAP - Mail access (unencrypted)
    - Port 993 (TCP) - IMAPS - Secure IMAP mail access
    - Port 110 (TCP) - POP3 - Mail access (unencrypted)
    - Port 995 (TCP) - POP3S - Secure POP3 mail access
    - Port 4190 (TCP) - Sieve - Mail filtering
    - Port 80 (TCP) - HTTP - Web access and Let's Encrypt verification
    - Port 443 (TCP) - HTTPS - Secure web access
- Status: Completed
- Location: us-south-1
- Category: Mail Server Setup

### Opened Mail Server Ports on Ethos Server (17:16 MST)
- Operation: Opened required ports for the mail server on the ethos server
- Details:
  * Created open_mail_server_ports_ethos.sh script to open required ports
  * Added inbound rules to the existing security group (trekker-refill-quit-refueling)
  * Opened the following ports:
    - Port 25 (TCP) - SMTP - Receiving mail from other mail servers
    - Port 465 (TCP) - SMTPS - Secure SMTP (legacy)
    - Port 587 (TCP) - Submission - Sending mail (with authentication)
    - Port 143 (TCP) - IMAP - Mail access (unencrypted)
    - Port 993 (TCP) - IMAPS - Secure IMAP mail access
    - Port 110 (TCP) - POP3 - Mail access (unencrypted)
    - Port 995 (TCP) - POP3S - Secure POP3 mail access
    - Port 4190 (TCP) - Sieve - Mail filtering
    - Port 80 (TCP) - HTTP - Web access and Let's Encrypt verification
    - Port 443 (TCP) - HTTPS - Secure web access
  * Verified all rules were successfully added to the security group
- Status: Completed
- Location: us-south-1
- Category: Network Operations

## 2025-03-24

### Fixed Disk Migration to ethos (02:57 MST)
- Operation: Fixed disk migration from adapt3 to ethos
- Details:
  * Discovered that the snapshot was created but the wrong volume was attached to ethos
  * Found volume "ethos-llms" created from snapshot but not attached to ethos
  * Attached the correct volume to ethos as "llms-snapshot"
  * Mounted the volume at /llms-snapshot on ethos
  * Verified that all 451GB of data (44% used) was properly transferred
  * Added entry to /etc/fstab for persistence
- Status: Completed
- Location: us-south-1
- Category: Storage Management

### Reconfigured to RAID0 Array on adapt3 (02:07 MST)
- Operation: Reconfigured from RAID1 to RAID0 array using vdb and vdc, formatted as XFS, and mounted as /lssd
- Details:
  * Unmounted and stopped the previous RAID1 array
  * Created RAID0 array using /dev/vdb and /dev/vdc (each 1.4TB)
  * Formatted the array with XFS filesystem
  * Mounted the array at /lssd with 2.9TB usable space
  * Updated RAID configuration in /etc/mdadm/mdadm.conf
  * Verified write speed: 3.1 GB/s
- Status: Completed
- Location: us-south-2
- Category: Storage Management

### Created RAID1 Array on adapt3 (02:04 MST)
- Operation: Created RAID1 array from vdb and vdc, formatted as XFS, and mounted as /lssd
- Details:
  * Created RAID1 array using /dev/vdb and /dev/vdc (each 1.4TB)
  * Formatted the array with XFS filesystem
  * Mounted the array at /lssd
  * Added entry to /etc/fstab for persistence
  * Added RAID configuration to /etc/mdadm/mdadm.conf
  * Verified write speed: 3.2 GB/s
- Status: Replaced by RAID0
- Location: us-south-2
- Category: Storage Management

## 2025-03-24

### Formatted and Mounted Disks on ethos (01:57 MST)
- Operation: Formatted and mounted disks on ethos
- Details:
  * Installed xfsprogs package on ethos
  * Formatted 2TB disk (vdg) as XFS and mounted at /llms1
  * Formatted 50GB disks (vdd and vde) as XFS and mounted at /data and /logs
  * Added entries to /etc/fstab for persistence
  * Verified all mounts are working correctly
- Status: Completed
- Location: us-south-1
- Category: Storage Management

### Completed Disk Migration from adapt3 to ethos (00:34 MST)
- Operation: Completed disk migration from adapt3 to ethos
- Details:
  * Successfully executed IBM Cloud disk operations script
  * Created snapshot of /dev/vdg on adapt3
  * Created 1TB volume for ethos from snapshot
  * Created 2TB volume for ethos
  * Attached both volumes to ethos
  * Prepared format_and_mount_ethos_disks.sh script for formatting and mounting disks on ethos
- Status: Completed
- Location: us-south-1, us-south-2
- Category: Storage Management

## 2025-03-23

### Formatted and Mounted Small Disks on adapt3 (22:50 MST)
- Operation: Formatted and mounted small disks on adapt3
- Details:
  * Created format_and_mount_data_logs.sh script to format and mount small disks
  * Formatted /dev/vdd (368K) as ext4 and mounted at /data
  * Skipped formatting /dev/vde (44K) as it was too small
  * Added entry to /etc/fstab for /dev/vdd
- Status: Completed
- Location: us-south-2
- Category: Storage Management

### Prepared Disk Migration from adapt3 to ethos (22:44 MST)
- Operation: Prepared disk migration from adapt3 to ethos
- Details:
  * Created move_data_and_prepare_disks.sh script to move data from /dev/vdh to /dev/vdg
  * Created ibm_cloud_disk_operations.sh script to handle IBM Cloud disk operations
  * Created format_and_mount_ethos_disks.sh script to format and mount disks on ethos
  * Moved data from /dev/vdh (7.2GB) to /dev/vdg
  * Unmounted /dev/vdh in preparation for deletion
  * Prepared scripts for creating snapshot of /dev/vdg and adding disks to ethos
- Status: Completed
- Location: us-south-1, us-south-2
- Category: Storage Management

### Mounted and Checked Disk Usage on adapt3 (22:39 MST)
- Operation: Mounted /dev/vdg and /dev/vdh disks and checked their usage
- Details:
  * Created mount_and_check_disks.sh script to mount disks and check usage
  * Mounted /dev/vdg at /llms (1TB disk, 44% used - 451GB)
  * Mounted /dev/vdh at /llms2 (1TB disk, 1% used - 7.2GB)
  * Both disks were already formatted with XFS filesystem
- Status: Completed
- Location: us-south-2
- Category: Storage Management


### Set Up SSH Key Authentication Between Servers (21:23 MST)
- Operation: Set up SSH key authentication between adapt3 and other servers
- Details:
  * Created setup_ssh_between_servers.sh script to automate the process
  * Copied public key from adapt3 to all other servers
  * Added public key to authorized_keys for x user on all servers
  * Created x user on servers where it didn't exist
  * Verified SSH connections from adapt3 to all other servers
  * Updated ssh_x11_forwarding_status.md with SSH commands
- Status: Completed
- Location: us-south-1, us-south-2
- Category: System Configuration

### Validated SSH X11 Forwarding on All Servers (21:03 MST)
- Operation: Validated SSH X11 forwarding functionality on all servers
- Details:
  * Created validate_ssh_x11.sh script to check X11 forwarding configuration
  * Created test_x11_forwarding.sh script to test running X11 applications
  * Created comprehensive_x11_fix.sh script to fix X11 forwarding issues
  * Verified X11 forwarding working on ethos, dataops-timeseries, and adapt3 servers
  * Identified issues with X11 forwarding on dataops-vector server
  * Created ssh_x11_forwarding_status.md report documenting current status
- Status: Completed (with noted issues on dataops-vector)
- Location: us-south-1, us-south-2
- Category: System Configuration

### Installed Desktop Packages on All Servers (19:34 MST)
- Operation: Installed VS Code, GNOME desktop, Chrome, Chrome Remote Desktop, and Slack on all servers
- Details:
  * Created install_desktop_packages.sh script to install all required packages
  * Created deploy_desktop_packages.sh script to deploy and execute the installation script on all servers
  * Successfully installed packages on dataops-vector, dataops-timeseries, and ethos servers
  * Installed Slack on adapt3 server
  * Some servers had package repository issues but installation completed successfully
- Status: Completed
- Location: us-south-1, us-south-2
- Category: Software Installation

## 2025-03-22

### Added Network Interfaces to adapt3 Server (21:06 MST)
- Operation: Added 6 additional network interfaces to the adapt3 server
- Details:
  * Added eth1 through eth6 network interfaces
  * Used network attachments API
  * Each interface has its own reserved IP address
  * Total of 7 network interfaces (1 primary + 6 secondary)
- Status: Completed
- Location: us-south-2
- Category: Network Operations

### Attached Volumes to Ethos Server (13:20 MST)
- Operation: Attached data volumes to the ethos server
- Details:
  * Attached ethos-data-south1 as "data"
  * Attached ethos-logs-south1 as "logs"
  * Attached ethos-llms-south1 as "llms"
- Status: Completed
- Location: us-south-1
- Category: Disk Operations

### Added 1TB Disk to adapt3 and Mounted as /llms2 (10:35 MST)
- Operation: Added a new 1TB disk to adapt3 server and mounted it as /llms2
- Details:
  * Created volume adapt3-llms2 (1TB) in us-south-2
  * Attached volume to adapt3 server
  * Formatted disk as XFS filesystem
  * Mounted disk at /llms2 (without adding to fstab)
- Status: Completed
- Location: us-south-2
- Category: Disk Operations

### Created RAID 0 Array on adapt3 and Mounted as /lssd (07:17 MST)
- Operation: Created a RAID 0 array with two 1.4TB disks and mounted it as /lssd
- Details:
  * Used /dev/vdb and /dev/vdc to create RAID 0 array
  * Formatted RAID array as XFS filesystem
  * Mounted RAID array at /lssd (without adding to fstab)
- Status: Completed
- Location: us-south-2
- Category: Disk Operations

### Formatted and Mounted 1TB Disk as /llms on adapt3 (07:14 MST)
- Operation: Formatted and mounted a 1TB disk as /llms on adapt3 server
- Details:
  * Formatted /dev/vdg as XFS filesystem
  * Mounted disk at /llms (without adding to fstab)
- Status: Completed
- Location: us-south-2
- Category: Disk Operations

### Created Ethos Server Reservation (09:05 MST)
- Operation: Created a reservation for the Ethos server
- Details:
  * Created reservation ethos-reservation for profile gx3-48x240x2l40s in us-south-1
  * Set affinity policy to automatic
  * Set expiration policy to renew
  * Term: three_year
- Status: Completed
- Location: us-south-1
- Category: VM Operations

### Attempted to Recreate Ethos Server with Reservation (09:09 MST)
- Operation: Attempted to recreate the Ethos server with the reservation
- Details:
  * Detached data volumes from original Ethos server
  * Deleted original Ethos server
  * Attempted to create new Ethos server with reservation
  * Encountered vCPU quota limitation (200 vCPU quota)
- Status: Failed
- Location: us-south-1
- Category: VM Operations
