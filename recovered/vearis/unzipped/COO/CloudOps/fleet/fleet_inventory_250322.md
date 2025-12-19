# IBM Cloud Fleet Inventory (March 25, 2025)

## Virtual Server Instances

### Ethos Server

| Property | Value |
|----------|-------|
| Name | ethos |
| ID | 0717_08cb9a2b-efef-4bd4-af87-f4b79f5546c4 |
| Status | running |
| Profile | gx3-48x240x2l40s |
| vCPUs | 48 |
| Memory | 240 GB |
| GPU | 2x NVIDIA L40S (48 GB) |
| Zone | us-south-1 |
| VPC | adapt-vpc-dallas |
| Resource Group | adapt |
| Internal IP | 10.240.1.4 |
| Floating IP | 52.118.191.234 |
| Network Interfaces | 1 (primary) |
| Reservation | ethos-reservation |
| Reservation Affinity Policy | automatic |
| Created | March 22, 2025 13:10:00 |

### DataOps Primary

| Property | Value |
|----------|-------|
| Name | dataops-primary |
| ID | 0717_43d1b974-388d-41bd-809b-1b8938651a5a |
| Status | running |
| Profile | bx2-8x32 |
| vCPUs | 8 |
| Memory | 32 GB |
| Zone | us-south-1 |
| VPC | us-south-default-vpc |
| Resource Group | adapt |
| Internal IP | 10.240.0.6 |
| Floating IP | None |
| Network Interfaces | 1 (primary) |
| Reservation | dataops-primary-reservation (active) |
| Reservation Affinity Policy | automatic |
| Created | March 21, 2025 23:01:29 |

### DataOps Timeseries

| Property | Value |
|----------|-------|
| Name | dataops-timeseries |
| ID | 0717_98ebda7a-c8ca-4c0b-8628-10e8a9bb03c1 |
| Status | running |
| Profile | bx2-8x32 |
| vCPUs | 8 |
| Memory | 32 GB |
| Zone | us-south-1 |
| VPC | us-south-default-vpc |
| Resource Group | adapt |
| Internal IP | 10.240.0.17 |
| Floating IP | None |
| Network Interfaces | 1 (primary) |
| Reservation | dataops-timeseries-reservation (active) |
| Reservation Affinity Policy | automatic |
| Created | March 22, 2025 03:58:18 |

### DataOps Vector

| Property | Value |
|----------|-------|
| Name | dataops-vector |
| ID | 0717_58623fe2-7513-4930-884e-840ca7b954a0 |
| Status | running |
| Profile | bx2-8x32 |
| vCPUs | 8 |
| Memory | 32 GB |
| Zone | us-south-1 |
| VPC | us-south-default-vpc |
| Resource Group | adapt |
| Internal IP | 10.240.0.18 |
| Floating IP | None |
| Network Interfaces | 1 (primary) |
| Reservation | dataops-vector-reservation (active) |
| Reservation Affinity Policy | automatic |
| Created | March 22, 2025 04:07:37 |

## Storage Volumes

### Ethos Server Volumes

| Name | ID | Size | Type | Status | Attachment Name |
|------|----|----|------|--------|----------------|
| wanted-basilisk-gaffe-slicing | r006-d6974d5c-8f4e-48f4-b898-06ffa4bc845b | 50 GB | boot | attached | fidgeting-manicotti-safari-primarily |
| ethos-data-south1 | r006-7a2b3f47-a4f7-4c10-aa3c-5d0ec79f1b66 | 50 GB | data | attached | data |
| ethos-logs-south1 | r006-7798a5fd-0e9b-416f-b4f9-ad45fc87254d | 50 GB | data | attached | logs |
| ethos-llms-south1 | r006-7b09213a-6fea-45ae-8b86-7d55f23d43fd | 1 TB | data | attached | llms |

### adapt3 Server Volumes

| Name | ID | Size | Type | Status | Attachment Name |
|------|----|----|------|--------|----------------|
| harddisk-catalyze-dose-arrow | r006-d8bf7a41-eb4b-4724-a36a-d571fed941e7 | 100 GB | boot | attached | undertook-debunk-rarity-tannery |
| data-adapt | r006-9d0c6f44-d456-4722-8226-66192087347f | 1.5 TB | data | attached | data-adapt-attachment |
| adapt3-llms | r006-fd9e07de-f8c9-4e4d-bcfd-c3f2b5a0fe25 | 1 TB | data | attached | llms |
| adapt3-llms2 | r006-f607da87-e35d-4680-96c1-44b6b8c172c6 | 1 TB | data | attached | llms2 |
| RAID 0 Array (/dev/vdb + /dev/vdc) | - | 2.8 TB | data | attached | - |

### DataOps Primary Volumes

| Name | ID | Size | Type | Status | Attachment Name |
|------|----|----|------|--------|----------------|
| (boot volume) | - | 50 GB | boot | attached | - |
| dataops-primary-data | r006-37240241-ddc8-471d-b248-34e4976a681b | 50 GB | data | attached | data |
| dataops-primary-backup | r006-c4b96103-2773-4370-bd67-e80bc857ce97 | 50 GB | data | attached | backup |

### DataOps Timeseries Volumes

| Name | ID | Size | Type | Status | Attachment Name |
|------|----|----|------|--------|----------------|
| (boot volume) | - | 50 GB | boot | attached | - |
| dataops-timeseries-data | r006-438388b7-0389-4cf0-80c6-bc74a4a440ef | 50 GB | data | attached | data |
| dataops-timeseries-backup | r006-3b430ae0-880e-49b8-83b3-74c5eeb79587 | 50 GB | data | attached | backup |

### DataOps Vector Volumes

| Name | ID | Size | Type | Status | Attachment Name |
|------|----|----|------|--------|----------------|
| (boot volume) | - | 50 GB | boot | attached | - |
| dataops-vector-data | r006-1d7ad177-be4c-4560-b8a9-84feeed4196a | 50 GB | data | attached | data |
| dataops-vector-backup | r006-8bdb0770-971a-47ca-84b9-1c32c0dfc22d | 50 GB | data | attached | backup |

## Network Interfaces

### Ethos Server

| Interface | Name | Type | Subnet | IP Address | Floating IP |
|-----------|------|------|--------|------------|-------------|
| eth0 | primary | primary | us-south-1-subnet | 10.240.1.4 | 52.118.191.234 |

### adapt3 Server

| Interface | Name | Type | Subnet | IP Address | Floating IP |
|-----------|------|------|--------|------------|-------------|
| eth0 | outpost-sitting-outskirts-animating | primary | us-south-2-default-subnet | 10.240.64.10 | 52.118.206.209 |
| eth1 | eth1-attachment | secondary | us-south-2-default-subnet | 10.240.64.5 | - |
| eth2 | eth2-attachment | secondary | us-south-2-default-subnet | 10.240.64.6 | - |
| eth3 | eth3-attachment | secondary | us-south-2-default-subnet | 10.240.64.7 | - |
| eth4 | eth4-attachment | secondary | us-south-2-default-subnet | 10.240.64.8 | - |
| eth5 | eth5-attachment | secondary | us-south-2-default-subnet | 10.240.64.9 | - |
| eth6 | eth6-attachment | secondary | us-south-2-default-subnet | 10.240.64.11 | - |

### DataOps Primary Server

| Interface | Name | Type | Subnet | IP Address | Floating IP |
|-----------|------|------|--------|------------|-------------|
| eth0 | primary | primary | us-south-1-subnet | 10.240.0.6 | - |

### DataOps Timeseries Server

| Interface | Name | Type | Subnet | IP Address | Floating IP |
|-----------|------|------|--------|------------|-------------|
| eth0 | primary | primary | us-south-1-subnet | 10.240.0.17 | - |

### DataOps Vector Server

| Interface | Name | Type | Subnet | IP Address | Floating IP |
|-----------|------|------|--------|------------|-------------|
| eth0 | primary | primary | us-south-1-subnet | 10.240.0.18 | - |

## Reservations

| Name | Status | Profile | Zone | Capacity | Term | Expiration Policy | Affinity Policy |
|------|--------|---------|------|----------|------|------------------|----------------|
| dataops-primary-reservation | active | bx2-8x32 | us-south-1 | 1 | 3 years | renew | automatic |
| dataops-timeseries-reservation | active | bx2-8x32 | us-south-1 | 1 | 3 years | renew | automatic |
| dataops-vector-reservation | active | bx2-8x32 | us-south-1 | 1 | 3 years | renew | automatic |

## Floating IPs

| Name | Address | Target | Status |
|------|---------|--------|--------|
| ethos-floating-ip-1742660058 | 52.118.191.234 | ethos (primary interface) | active |
| adapt3-floating-ip | 52.118.206.209 | adapt3 (primary interface) | active |

## Users

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

## SSH Keys

| Name | Location |
|------|----------|
| ibm-admin | /home/x/.ssh/ibm-admin_rsa |

## Mount Points

### Ethos Server

| Device | Mount Point | Filesystem | Size |
|--------|-------------|------------|------|
| /dev/vdd | /data | XFS | 50 GB |
| /dev/vde | /logs | XFS | 50 GB |
| /dev/vdf | /llms | XFS | 1 TB |

### adapt3 Server

| Device | Mount Point | Filesystem | Size |
|--------|-------------|------------|------|
| /dev/vdf | /data-nova | XFS | 1.5 TB |
| /dev/vdg | /llms | XFS | 1 TB |
| /dev/vdh | /llms2 | XFS | 1 TB |
| /dev/md0 (RAID 0: /dev/vdb + /dev/vdc) | /lssd | XFS | 2.8 TB |

### DataOps Servers

| Device | Mount Point | Filesystem | Size |
|--------|-------------|------------|------|
| /dev/vdd | /data | XFS | 50 GB |
| /dev/vde | /backup | XFS | 50 GB |

## Resource Quotas

| Resource | Quota | Used | Available |
|----------|-------|------|-----------|
| vCPUs | 200 | 72 | 128 |
| Memory | - | 336 GB | - |
| GPU | - | 2 | - |
| Storage | - | 1.45 TB | - |

## Notes

1. The Ethos server does not have a reservation due to vCPU quota limitations. A quota increase request is needed to create a reservation for the Ethos server.

2. All DataOps servers have active 3-year reservations with automatic affinity policy and renew expiration policy.

3. All servers have been recreated with the ibm-admin SSH key for secure access.

4. All servers have users with sudo NOPASSWD privileges for easy administration.

5. All data volumes have been formatted with XFS and mounted at appropriate mount points.