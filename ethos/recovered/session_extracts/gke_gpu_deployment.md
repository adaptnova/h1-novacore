# GKE and Mixed GPU Deployment Plan

## Infrastructure Overview

### GKE Clusters
```
Primary Clusters (per region):
- 3x Large ML Clusters
  * 100 nodes each
  * Mixed GPU node pools
  * High memory configurations
  * Network-optimized

- 2x Research Clusters
  * 50 nodes each
  * Experimental workloads
  * Flexible configurations
  * Spot instances enabled

- 5x Service Clusters
  * 20 nodes each
  * Supporting services
  * Monitoring and logging
  * Pipeline orchestration
```

### GPU Node Pools

#### H100 Node Pools
```
Production Pool:
- Machine Type: a3-megagpu-8g
- Nodes per zone: 8
- Total GPUs: 192 (8 nodes × 8 GPUs × 3 zones)
- Use: Production training

Research Pool:
- Machine Type: a3-megagpu-8g
- Nodes per zone: 4
- Total GPUs: 96 (4 nodes × 8 GPUs × 3 zones)
- Use: Research workloads

Spot Pool:
- Machine Type: a3-highgpu-4g
- Nodes per zone: 4
- Total GPUs: 96 (4 nodes × 8 GPUs × 3 zones)
- Use: Cost-effective development
```

#### A100 Node Pools
```
Production Pool:
- Machine Type: a2-highgpu-16g
- Nodes per zone: 4
- Total GPUs: 192 (4 nodes × 16 GPUs × 3 zones)
- Use: Production inference

Research Pool:
- Machine Type: a2-highgpu-8g
- Nodes per zone: 4
- Total GPUs: 96 (4 nodes × 8 GPUs × 3 zones)
- Use: Model optimization

Spot Pool:
- Machine Type: a2-highgpu-4g
- Nodes per zone: 4
- Total GPUs: 48 (4 nodes × 4 GPUs × 3 zones)
- Use: Development and testing
```

## Deployment Steps

### 1. Network Setup
```bash
# Create VPC for GKE clusters
gcloud compute networks create ml-network \
    --subnet-mode=custom \
    --bgp-routing-mode=regional \
    --mtu=1500

# Create subnets
gcloud compute networks subnets create ml-subnet-us-central1 \
    --network=ml-network \
    --region=us-central1 \
    --range=10.0.0.0/20 \
    --secondary-range pod-range=10.4.0.0/14,svc-range=10.8.0.0/20 \
    --enable-private-ip-google-access
```

### 2. GKE Cluster Creation
```bash
# Create primary ML cluster
gcloud container clusters create ml-cluster-1 \
    --region=us-central1 \
    --network=ml-network \
    --subnetwork=ml-subnet-us-central1 \
    --enable-ip-alias \
    --cluster-secondary-range-name=pod-range \
    --services-secondary-range-name=svc-range \
    --enable-private-nodes \
    --master-ipv4-cidr=172.16.0.0/28 \
    --enable-master-global-access \
    --workload-pool=a-d-a-p-t.svc.id.goog \
    --enable-image-streaming \
    --enable-shielded-nodes \
    --enable-vertical-pod-autoscaling \
    --enable-autoscaling \
    --num-nodes=3 \
    --min-nodes=3 \
    --max-nodes=100 \
    --machine-type=n2-standard-32
```

### 3. GPU Node Pool Creation
```bash
# Create H100 production pool
gcloud container node-pools create h100-prod-pool \
    --cluster=ml-cluster-1 \
    --region=us-central1 \
    --machine-type=a3-megagpu-8g \
    --accelerator type=nvidia-h100-80gb,count=8 \
    --enable-autoscaling \
    --num-nodes=1 \
    --min-nodes=1 \
    --max-nodes=8 \
    --node-locations=us-central1-a,us-central1-b,us-central1-c

# Create A100 production pool
gcloud container node-pools create a100-prod-pool \
    --cluster=ml-cluster-1 \
    --region=us-central1 \
    --machine-type=a2-highgpu-16g \
    --accelerator type=nvidia-tesla-a100,count=16 \
    --enable-autoscaling \
    --num-nodes=1 \
    --min-nodes=1 \
    --max-nodes=4 \
    --node-locations=us-central1-a,us-central1-b,us-central1-c
```

### 4. Storage Configuration
```bash
# Create storage class for ML workloads
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ml-storage
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
EOF
```

### 5. GPU Operator Installation
```bash
# Add NVIDIA Helm repo
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Install GPU operator
helm install gpu-operator nvidia/gpu-operator \
    --namespace gpu-operator \
    --create-namespace \
    --set driver.enabled=false \
    --set toolkit.enabled=true \
    --set devicePlugin.enabled=true
```

### 6. Monitoring Setup
```bash
# Enable GKE monitoring
gcloud container clusters update ml-cluster-1 \
    --region=us-central1 \
    --enable-managed-prometheus \
    --enable-managed-grafana

# Install DCGM exporter
helm install dcgm-exporter nvidia/dcgm-exporter \
    --namespace gpu-operator
```

## Workload Management

### 1. Node Selectors
```yaml
# H100 workload example
apiVersion: v1
kind: Pod
metadata:
  name: h100-training
spec:
  nodeSelector:
    cloud.google.com/gke-accelerator: nvidia-h100-80gb
  containers:
  - name: ml-training
    image: gcr.io/a-d-a-p-t/ml-training:latest
    resources:
      limits:
        nvidia.com/gpu: 8
```

### 2. Priority Classes
```yaml
# Priority class for production workloads
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: production-critical
value: 1000000
globalDefault: false
description: "Critical production workloads"
```

### 3. Resource Quotas
```yaml
# Quota for research namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: research-quota
spec:
  hard:
    requests.nvidia.com/gpu: 32
    limits.nvidia.com/gpu: 32
```

## Monitoring and Maintenance

### 1. GPU Metrics Collection
- DCGM metrics for GPU utilization
- Custom metrics for training progress
- Workload-specific metrics
- Cost allocation tracking

### 2. Autoscaling Configuration
- Node pool autoscaling
- Vertical pod autoscaling
- Horizontal pod autoscaling
- Spot instance management

### 3. Cost Optimization
- Spot instance usage
- Resource quota management
- Idle resource cleanup
- Budget monitoring

## Security Measures

### 1. Network Security
- Private GKE clusters
- Network policies
- Service mesh integration
- Ingress/egress controls

### 2. Workload Security
- Pod security policies
- Runtime security
- Image scanning
- Secret management

### 3. Access Control
- IAM integration
- RBAC policies
- Audit logging
- Compliance monitoring

## Disaster Recovery

### 1. Backup Strategy
- Persistent volume snapshots
- Configuration backups
- State management
- Cross-region replication

### 2. Recovery Procedures
- Cluster restoration
- Workload migration
- Data recovery
- Service continuity

## Next Steps

1. Initial Deployment
- Set up network infrastructure
- Create first GKE cluster
- Configure GPU node pools
- Install required operators

2. Validation
- Test GPU workloads
- Verify monitoring
- Check autoscaling
- Validate security

3. Production Migration
- Move initial workloads
- Scale node pools
- Enable monitoring
- Document procedures
