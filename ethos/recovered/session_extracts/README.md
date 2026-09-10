# ADAPT AI/ML Infrastructure Tools

Tools and documentation for managing GPU infrastructure on Google Cloud Platform, with a focus on H100 and A100 deployments.

## Overview

This repository contains tools for:
1. GPU quota management and tracking
2. GKE cluster deployment with GPU support
3. Kubernetes workload management
4. Infrastructure monitoring and maintenance

## Components

### Quota Management
- `check_h100_availability.py`: Check H100 GPU availability
- `track_quotas.py`: Track and manage quota requests
- `final_quota_request_2.2.0.md`: Latest quota request template

### GKE Deployment
- `deploy_gke_gpu.py`: Deploy GKE clusters with GPU support
- `k8s_gpu_manifests.yaml`: Kubernetes manifests for GPU workloads
- `apply_k8s_manifests.py`: Manage Kubernetes manifest deployment

### Documentation
- `gke_gpu_README.md`: GKE deployment guide
- `h100_findings.md`: H100 availability analysis
- `quota_changes_summary.md`: Quota request history

## Quick Start

1. Setup Environment
```bash
# Clone repository
git clone https://github.com/adapt/aiml-tools.git
cd aiml-tools

# Run setup script
chmod +x setup.sh
./setup.sh
```

2. Check GPU Availability
```bash
# Activate virtual environment
source aiml_env/bin/activate

# Check H100 availability
python3 check_h100_availability.py
```

3. Deploy GKE Cluster
```bash
# Deploy cluster with GPU node pools
python3 deploy_gke_gpu.py \
    --project=a-d-a-p-t \
    --region=us-central1 \
    --cluster-name=ml-cluster-1

# Apply Kubernetes manifests
python3 apply_k8s_manifests.py \
    --manifest-file=k8s_gpu_manifests.yaml
```

## Infrastructure Overview

### GPU Resources
```
H100 MEGA GPUs:
- 320 GPUs per region
- 40 a3-megagpu-8g instances
- 8 GPUs per instance

A100 GPUs:
- 256 GPUs per region
- 16 a2-highgpu-16g instances
- 16 GPUs per instance
```

### GKE Clusters
```
Production Clusters:
- 3 clusters per region
- Mixed GPU node pools
- High availability setup

Research Clusters:
- 2 clusters per region
- Experimental workloads
- Spot instance support
```

### Storage
```
HyperDisk ML:
- 30M IOPS total
- 240 TB capacity
- Regional replication

Local SSD:
- 180,000 GB total
- High-performance storage
- Per-instance allocation
```

## Deployment Process

1. Request Quotas
- Use `final_quota_request_2.2.0.md` template
- Track with `track_quotas.py`
- Monitor approval status

2. Setup Infrastructure
- Create VPC and subnets
- Deploy GKE clusters
- Configure GPU node pools

3. Deploy Workloads
- Apply Kubernetes manifests
- Configure monitoring
- Setup alerts

4. Monitor and Maintain
- Track GPU utilization
- Monitor costs
- Manage updates

## Best Practices

### Resource Management
- Use priority classes for workload prioritization
- Implement resource quotas per namespace
- Configure appropriate node selectors
- Use pod disruption budgets

### Cost Optimization
- Use spot instances for development
- Monitor resource utilization
- Implement autoscaling
- Track costs by namespace

### Security
- Enable Workload Identity
- Use minimal service account permissions
- Implement network policies
- Regular security audits

### Monitoring
- Configure GPU metrics collection
- Set up appropriate alerts
- Monitor quota usage
- Track performance metrics

## Development

### Requirements
- Python 3.7+
- gcloud CLI
- kubectl
- Dependencies in requirements.txt

### Setup Development Environment
```bash
# Create virtual environment
python3 -m venv aiml_env
source aiml_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For issues or questions:
1. Check documentation
2. Review existing issues
3. Submit new issue
4. Contact support team

## License

Copyright (c) 2024 ADAPT

All rights reserved.
