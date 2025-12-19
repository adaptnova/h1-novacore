# Ethos GPU Server Specification and Configuration

## Overview

The Ethos GPU server is a high-performance computing node designed for GPU-accelerated workloads within the Adapt Platform. This document provides detailed specifications and configuration guidelines for the deployment and optimization of the Ethos server.

## Hardware Specifications

### Server Profile

- **Profile:** gx3-48x240x2l40s
- **vCPUs:** 48
- **RAM:** 240GB
- **GPUs:** 2x NVIDIA L40S
- **Location:** IBM Cloud, us-south-2 zone, dataops-vpc

### GPU Specifications (NVIDIA L40S)

- **CUDA Cores:** 18,176 per GPU
- **Tensor Cores:** 568 per GPU
- **Memory:** 48GB GDDR6 per GPU
- **Memory Bandwidth:** 864 GB/s per GPU
- **FP32 Performance:** 36.2 TFLOPS per GPU
- **TensorFloat-32 Performance:** 145 TFLOPS per GPU
- **INT8 Performance:** 290 TOPS per GPU
- **PCIe Interface:** Gen4 x16

### Storage Configuration

- **Boot Volume:**
  - Size: 50GB
  - Type: NVMe SSD
  - IOPS: 5000
  - Filesystem: ext4

- **Data Volume:**
  - Size: 100GB (expandable via LVM)
  - Type: NVMe SSD
  - IOPS: 10000
  - Filesystem: XFS
  - Mount Point: /data
  - Mount Options: noatime,nodiratime,logbufs=8

- **Log Volume:**
  - Size: 20GB (expandable via LVM)
  - Type: NVMe SSD
  - IOPS: 2000
  - Filesystem: XFS
  - Mount Point: /var/log
  - Mount Options: noatime,nodiratime

### Network Configuration

- **Network Interface:** 10 Gbps
- **VPC:** dataops-vpc
- **Subnet:** dataops-subnet (10.240.64.0/24)
- **Security Group:** ethos-sg
- **Private IP:** To be assigned from subnet range

## Software Configuration

### Operating System

- **OS:** Ubuntu 22.04 LTS
- **Kernel:** 5.15 or later with NVIDIA driver compatibility
- **System Packages:**
  - build-essential
  - cmake
  - git
  - python3-dev
  - python3-pip
  - htop
  - iotop
  - iftop
  - nvtop

### GPU Software Stack

- **NVIDIA Driver:** 535.129.03 or later
- **CUDA Toolkit:** 12.2 or later
- **cuDNN:** 8.9.5 or later
- **TensorRT:** 8.6.1 or later
- **NCCL:** 2.18.3 or later
- **NVIDIA Container Toolkit:** Latest version

### Development Frameworks

- **PyTorch:** 2.1.0 or later
- **TensorFlow:** 2.14.0 or later
- **JAX:** Latest version
- **ONNX Runtime:** Latest version with GPU support
- **Triton Inference Server:** Latest version

### Container Runtime

- **Docker:** Latest version
- **NVIDIA Container Runtime:** Latest version
- **Docker Compose:** Latest version

### Monitoring Tools

- **NVIDIA DCGM:** Latest version
- **Prometheus Node Exporter:** Latest version
- **NVIDIA DCGM Exporter:** Latest version
- **Filebeat:** Latest version (for log forwarding)

## Security Configuration

### Security Group Rules (ethos-sg)

#### Inbound Rules
- Allow SSH (TCP 22) from management IPs only
- Allow internal VPC traffic from dataops-subnet
- Allow monitoring traffic (Prometheus, etc.)
- Allow NTP (UDP 123) for time synchronization

#### Outbound Rules
- Allow all outbound traffic

### User Access

- **System Users:**
  - synaptic (sudo privileges)
  - forge (sudo privileges)
  - x (sudo privileges)
  - vertex (sudo privileges)
  - Default password: "x" (to be changed on first login)
  - SSH key-based authentication enforced

### Filesystem Security

- **Boot Volume:**
  - noexec on /tmp
  - Secure mount options

- **Data Volume:**
  - Appropriate permissions for application data
  - Regular permission audits

## Performance Optimization

### GPU Optimization

- **NVIDIA Persistence Mode:** Enabled
- **GPU Clock Rates:** Maximum performance mode
- **GPU Power Limit:** Maximum (Default)
- **NUMA Affinity:** Optimized for GPU access
- **CPU Governor:** performance

### Storage Optimization

- **I/O Scheduler:** none (for NVMe)
- **Readahead:** 4096 sectors
- **XFS Mount Options:**
  - noatime
  - nodiratime
  - logbufs=8
  - allocsize=64k

### Memory Optimization

- **Swappiness:** 10
- **Transparent Hugepages:** madvise
- **NUMA Policy:** Optimized for GPU workloads

### Network Optimization

- **TCP Settings:**
  - net.core.rmem_max=16777216
  - net.core.wmem_max=16777216
  - net.ipv4.tcp_rmem=4096 87380 16777216
  - net.ipv4.tcp_wmem=4096 65536 16777216
  - net.ipv4.tcp_congestion_control=bbr

## Monitoring Configuration

### System Metrics

- **CPU Utilization:** Per core and overall
- **Memory Usage:** Total, free, cached, buffers
- **Disk I/O:** IOPS, throughput, latency
- **Network:** Bandwidth, packets, errors
- **Temperature:** CPU and system

### GPU Metrics

- **GPU Utilization:** Compute and memory
- **GPU Memory:** Used, free, allocation rate
- **GPU Power:** Consumption, efficiency
- **GPU Temperature:** Core temperature
- **GPU Processes:** Running processes, memory usage

### Log Monitoring

- **System Logs:** Standard syslog configuration
- **Application Logs:** Configured for specific applications
- **GPU Driver Logs:** NVIDIA driver logs
- **Container Logs:** Docker and application container logs

## Backup and Recovery

### Snapshot Strategy

- **Boot Volume:** Daily snapshots with 7-day retention
- **Data Volume:** Hourly snapshots with 2-day retention
- **Log Volume:** Daily snapshots with 3-day retention

### Backup Procedures

- **Configuration Backup:** Daily backup of configuration files
- **Application State:** Application-specific backup procedures
- **User Data:** Regular backup of user home directories

## Deployment Checklist

1. **Pre-deployment Verification**
   - Confirm L40S GPU availability in the zone
   - Verify network connectivity
   - Ensure security group creation permissions

2. **Initial Deployment**
   - Create security group with required rules
   - Create storage volumes with specified IOPS
   - Deploy server with correct profile
   - Attach volumes and configure networking

3. **Base Configuration**
   - Update operating system
   - Configure storage (format and mount volumes)
   - Set up LVM for future expansion
   - Configure system optimization parameters

4. **GPU Setup**
   - Install NVIDIA drivers
   - Install CUDA toolkit and libraries
   - Verify GPU functionality with nvidia-smi
   - Run GPU benchmarks to validate performance

5. **Software Installation**
   - Install development frameworks
   - Configure container runtime
   - Set up monitoring tools
   - Configure log forwarding

6. **Security Configuration**
   - Create user accounts
   - Configure SSH access
   - Apply security hardening
   - Test security controls

7. **Performance Testing**
   - Run GPU performance benchmarks
   - Test storage I/O performance
   - Validate network performance
   - Ensure monitoring is capturing all metrics

8. **Documentation**
   - Document final configuration
   - Create runbooks for common operations
   - Document performance baseline

## Maintenance Procedures

### Regular Maintenance

- **Driver Updates:** Quarterly or as needed
- **OS Updates:** Monthly security patches
- **Performance Tuning:** Quarterly review and optimization
- **Disk Space Management:** Weekly review of usage trends

### Emergency Procedures

- **GPU Failure:** Troubleshooting and replacement procedures
- **Performance Degradation:** Investigation and resolution steps
- **System Recovery:** Procedures for various failure scenarios

## Integration with Project Tapestry

The Ethos GPU server will be integrated with Project Tapestry in Q2 2025, which will enhance its capabilities with:

- Advanced NIC optimization for improved GPU data transfer
- Optimized network paths for distributed GPU workloads
- Enhanced VM configuration for GPU performance

## Conclusion

The Ethos GPU server represents a critical component of the Adapt Platform, providing high-performance GPU computing capabilities. By following the specifications and configuration guidelines in this document, the server will be optimized for maximum performance, reliability, and security.

The priority deployment of this server ensures that GPU resources are available early in the implementation process, allowing for immediate use while the rest of the infrastructure is being deployed.