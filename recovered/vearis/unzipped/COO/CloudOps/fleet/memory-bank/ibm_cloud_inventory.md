# IBM Cloud Inventory

This file documents the IBM Cloud assets inventory for the CloudOps Fleet project.
2025-03-22 01:38:00 - Initial inventory collection.

## VPC Instances

| Name | ID | Status |
|------|----|----|
| adapt-vpc-dallas | r006-98954759-7e96-4116-841d-ac63a601a939 | available |
| dataops-vpc-new | r006-a6e2b4f0-87bb-442e-8557-5aee2f3fdc5f | available |
| tapestry-net-01-primary | r006-3161b5ca-be9e-447b-af51-4ac2d84181e1 | available |
| tapestry-net-02-secondary | r006-b75e8482-fdd6-48a8-be84-5ced8539e12a | available |
| tapestry-net-03-tertiary | r006-42661fc8-c861-40f2-b264-2a872d6475bd | available |
| tapestry-net-04-quaternary | r006-09b88e92-fbc3-4fc7-9434-433e1eadc57a | available |
| tapestry-net-05-quinary | r006-692a2f12-6ec4-444a-9429-332774c22b2e | available |
| tapestry-net-12-duodenary | r006-bbd087e2-6b31-4c1c-bca6-b4c00e5701ee | available |
| us-south-default-vpc | r006-273e9e7d-9da9-4df2-8f93-c935d34b6a00 | available |

## Virtual Server Instances

| Name | ID | Status | IP Address | VPC | Zone |
|------|----|----|------------|-----|------|
| ethos | 0717_03ed7300-9111-4cd8-82c9-f6d5f5d10224 | running | 10.240.0.5 | us-south-default-vpc | us-south-1 |
| dataops-primary | 0717_43d1b974-388d-41bd-809b-1b8938651a5a | running | 10.240.0.6 | us-south-default-vpc | us-south-1 |
| dataops-timeseries | 0717_2f6509b5-7ea3-4989-921f-e976e044818e | running | 10.240.0.8 | us-south-default-vpc | us-south-1 |
| dataops-vector | 0717_d4d79516-0459-4e07-9135-12e15c690375 | running | 10.240.0.7 | us-south-default-vpc | us-south-1 |
| adapt3 | 0727_e882df50-8824-4c5a-b025-86a8bfda0672 | running | 10.240.64.10 | us-south-default-vpc | us-south-2 |

## Target Servers Details

### Ethos Server
- **Name**: ethos
- **ID**: 0717_03ed7300-9111-4cd8-82c9-f6d5f5d10224
- **Status**: running
- **IP Address**: 10.240.0.5
- **VPC**: us-south-default-vpc
- **Zone**: us-south-1
- **Profile**: gx3-48x240x2l40s (48 vCPUs, 240GB RAM, 2 NVIDIA L40S GPUs)
- **Image**: ibm-debian-12-9-minimal-amd64-1
- **Network Interfaces**:
  - eth0: 10.240.0.5 (primary)
  - eth1: 10.240.0.9
  - eth2: 10.240.0.11
  - eth3: 10.240.0.13
- **Volumes**:
  - Boot volume: slippery-stain-penalty-grimacing
  - Data volume: ethos-data-south1
  - Logs volume: ethos-logs-south1
  - LLMs volume: ethos-llms-south1

### DataOps Primary Server
- **Name**: dataops-primary
- **ID**: 0717_43d1b974-388d-41bd-809b-1b8938651a5a
- **Status**: running
- **IP Address**: 10.240.0.6
- **VPC**: us-south-default-vpc
- **Zone**: us-south-1
- **Profile**: bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image**: ibm-debian-12-9-minimal-amd64-1
- **Network Interfaces**:
  - Primary: 10.240.0.6
- **Volumes**:
  - Boot volume: lullaby-selected-easiness-implicit
  - Data volume: dataops-primary-data
  - Backup volume: dataops-primary-backup

### DataOps Timeseries Server
- **Name**: dataops-timeseries
- **ID**: 0717_2f6509b5-7ea3-4989-921f-e976e044818e
- **Status**: running
- **IP Address**: 10.240.0.8
- **VPC**: us-south-default-vpc
- **Zone**: us-south-1
- **Profile**: bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image**: ibm-debian-12-9-minimal-amd64-1

### DataOps Vector Server
- **Name**: dataops-vector
- **ID**: 0717_d4d79516-0459-4e07-9135-12e15c690375
- **Status**: running
- **IP Address**: 10.240.0.7
- **VPC**: us-south-default-vpc
- **Zone**: us-south-1
- **Profile**: bx2-8x32 (8 vCPUs, 32GB RAM)
- **Image**: ibm-debian-12-9-minimal-amd64-1