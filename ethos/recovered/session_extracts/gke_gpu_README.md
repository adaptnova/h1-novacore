# GKE GPU Deployment Tools

This repository contains tools and configurations for deploying and managing GPU workloads on Google Kubernetes Engine (GKE).

## Tools Overview

### 1. Deployment Scripts
- `deploy_gke_gpu.py`: Automates GKE cluster creation with GPU node pools
- `apply_k8s_manifests.py`: Manages Kubernetes manifest deployment
```bash
# Create GKE cluster with GPU node pools
python3 deploy_gke_gpu.py \
    --project=a-d-a-p-t \
    --region=us-central1 \
    --cluster-name=ml-cluster-1

# Apply Kubernetes manifests
python3 apply_k8s_manifests.py \
    --manifest-file=k8s_gpu_manifests.yaml \
    --action=apply
```

### 2. Kubernetes Manifests
Located in `k8s_gpu_manifests.yaml`:
- Priority Classes
- Resource Quotas
- Storage Classes
- Example GPU Jobs
- Monitoring Configuration
- Network Policies

## GPU Node Pools

### H100 Configurations
```
Production Pool:
- Machine Type: a3-megagpu-8g
- GPUs per Node: 8x H100
- Nodes per Zone: 8
- Total GPUs: 192

Research Pool:
- Machine Type: a3-megagpu-8g
- GPUs per Node: 8x H100
- Nodes per Zone: 4
- Total GPUs: 96

Spot Pool:
- Machine Type: a3-highgpu-4g
- GPUs per Node: 8x H100
- Nodes per Zone: 4
- Total GPUs: 96
```

### A100 Configurations
```
Production Pool:
- Machine Type: a2-highgpu-16g
- GPUs per Node: 16x A100
- Nodes per Zone: 4
- Total GPUs: 192

Research Pool:
- Machine Type: a2-highgpu-8g
- GPUs per Node: 8x A100
- Nodes per Zone: 4
- Total GPUs: 96

Spot Pool:
- Machine Type: a2-highgpu-4g
- GPUs per Node: 4x A100
- Nodes per Zone: 4
- Total GPUs: 48
```

## Deployment Process

### 1. Prerequisites
- GCP project with required quotas
- gcloud CLI configured
- kubectl installed
- Python 3.7+

### 2. Network Setup
```bash
# Create VPC and subnets
gcloud compute networks create ml-network \
    --subnet-mode=custom \
    --bgp-routing-mode=regional

gcloud compute networks subnets create ml-subnet \
    --network=ml-network \
    --region=us-central1 \
    --range=10.0.0.0/20
```

### 3. Cluster Creation
```bash
# Deploy GKE cluster
python3 deploy_gke_gpu.py \
    --project=a-d-a-p-t \
    --region=us-central1 \
    --cluster-name=ml-cluster-1 \
    --network-name=ml-network \
    --subnet-name=ml-subnet
```

### 4. Kubernetes Setup
```bash
# Apply manifests
python3 apply_k8s_manifests.py \
    --manifest-file=k8s_gpu_manifests.yaml

# Verify deployment
python3 apply_k8s_manifests.py \
    --manifest-file=k8s_gpu_manifests.yaml \
    --action=verify
```

## Workload Management

### 1. Priority Classes
```yaml
production-critical: 1000000
research-high: 800000
development: 500000
```

### 2. Resource Quotas
```yaml
H100 Production:
- GPUs: 64
- CPU: 1000
- Memory: 4000Gi

H100 Research:
- GPUs: 32
- CPU: 500
- Memory: 2000Gi
```

### 3. Storage Classes
```yaml
ml-storage-extreme:
- Type: hyperdisk-extreme
- Replication: regional-pd
```

## Monitoring

### 1. GPU Metrics
- GPU utilization
- Memory usage
- Temperature
- Error counts

### 2. Alerts
- High GPU memory usage (>90%)
- GPU errors
- Node health
- Quota usage

## Security

### 1. Network Policies
- Isolated GPU workloads
- Monitoring access
- Storage access

### 2. Access Control
- Namespace isolation
- RBAC configuration
- Service accounts

## Maintenance

### 1. Node Updates
```bash
# Drain node for maintenance
kubectl drain <node-name> \
    --ignore-daemonsets \
    --delete-emptydir-data

# Update node pool
gcloud container node-pools upgrade <pool-name> \
    --cluster=ml-cluster-1 \
    --region=us-central1
```

### 2. Cleanup
```bash
# Remove all resources
python3 apply_k8s_manifests.py \
    --manifest-file=k8s_gpu_manifests.yaml \
    --action=cleanup

# Delete cluster
gcloud container clusters delete ml-cluster-1 \
    --region=us-central1
```

## Best Practices

1. Resource Management
- Use priority classes for workload prioritization
- Implement resource quotas per namespace
- Configure appropriate node selectors
- Use pod disruption budgets

2. Storage
- Use regional persistent disks for availability
- Configure appropriate storage classes
- Implement backup strategies
- Monitor storage performance

3. Networking
- Implement network policies
- Configure appropriate firewall rules
- Monitor network performance
- Use load balancing for services

4. Security
- Enable Workload Identity
- Use minimal service account permissions
- Implement network policies
- Regular security audits

5. Monitoring
- Configure GPU metrics collection
- Set up appropriate alerts
- Monitor quota usage
- Track costs

## Troubleshooting

1. GPU Issues
- Check NVIDIA driver installation
- Verify GPU allocation
- Monitor GPU metrics
- Check pod logs

2. Node Issues
- Check node conditions
- Verify capacity
- Monitor resource usage
- Check system logs

3. Workload Issues
- Check pod status
- Verify resource requests
- Check scheduling events
- Monitor performance

## Support

For issues or questions:
1. Check documentation
2. Review logs and metrics
3. Contact GCP support
4. File internal ticket
