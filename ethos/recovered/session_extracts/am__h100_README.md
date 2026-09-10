# H100/A3 Setup and Management Tools

This repository contains tools and documentation for setting up and managing H100 GPUs and A3 instances on Google Cloud Platform.

## Available Tools

### 1. Analysis Tools

- `check_h100_availability.py`: Checks H100 accelerator type and A3 machine type availability across regions
- `check_mega_h100.py`: Specifically checks for H100 MEGA GPU availability
- `check_preemptible_h100.py`: Checks preemptible/spot instance availability
- `check_quotas.py`: General quota checking utility

### 2. Deployment Tools

- `deploy_h100_cluster.py`: Main deployment script for H100/A3 clusters
```bash
# Example usage:
python3 deploy_h100_cluster.py \
    --project=a-d-a-p-t \
    --region=us-central1 \
    --name=ml-cluster \
    --prod-instances=2 \
    --spot-instances=1
```

### 3. Documentation

- `h100_findings.md`: Current H100/A3 availability analysis
- `h100_quota_request.md`: Template for quota requests
- `h100_deployment_checklist.md`: Comprehensive deployment checklist

## Machine Types Available

### Production Instances
```
a3-megagpu-8g
- 208 vCPUs
- 1872GB RAM
- 8x NVIDIA H100 MEGA GPUs
```

### Development/Testing Instances
```
a3-highgpu-1g through a3-highgpu-4g
- Must use Spot VMs
- Varying CPU/RAM configurations
- Cost-effective for development
```

## Setup Process

1. Check Availability
```bash
# Check H100 availability in your region
python3 check_h100_availability.py

# Check specific quotas
python3 check_quotas.py
```

2. Request Quotas
- Use `h100_quota_request.md` as template
- Submit requests for each region
- Monitor quota request status

3. Prepare Environment
- Follow `h100_deployment_checklist.md`
- Set up networking
- Configure storage
- Set up monitoring

4. Deploy Cluster
```bash
# Deploy production cluster
python3 deploy_h100_cluster.py \
    --project=your-project \
    --region=us-central1 \
    --name=prod-cluster \
    --prod-instances=2

# Deploy development cluster
python3 deploy_h100_cluster.py \
    --project=your-project \
    --region=us-central1 \
    --name=dev-cluster \
    --spot-instances=2
```

## Important Limitations

1. Machine Type Restrictions
- A3 machines only available on Sapphire Rapids
- Cannot change machine type once created
- No Windows OS support

2. Storage Limitations
- No regional persistent disks
- Must use zonal persistent disks
- Local SSDs recommended for performance

3. Spot Instance Requirements
- a3-highgpu-1g through a3-highgpu-4g must use Spot VMs
- Plan for preemption
- Use appropriate termination scripts

## Best Practices

1. High Availability
- Deploy across multiple zones
- Use instance groups where possible
- Implement proper monitoring
- Set up automated recovery

2. Storage Strategy
- Use Local SSDs for performance
- Implement proper backup strategy
- Consider storage tiering
- Monitor storage performance

3. Cost Management
- Use spot instances where possible
- Monitor resource utilization
- Implement auto-scaling
- Set up budget alerts

4. Security
- Use service accounts
- Implement proper IAM roles
- Set up network security
- Monitor access patterns

## Monitoring

1. GPU Metrics
- GPU utilization
- Memory usage
- Temperature
- Power consumption

2. Instance Metrics
- CPU utilization
- Memory usage
- Network throughput
- Disk performance

3. Cost Metrics
- Spot instance costs
- Storage costs
- Network costs
- Overall budget

## Troubleshooting

1. Common Issues
- Quota limits
- GPU driver issues
- Network connectivity
- Storage performance

2. Debug Tools
- GPU driver logs
- System logs
- Network traces
- Performance metrics

## Support

For issues or questions:
1. Check documentation first
2. Review troubleshooting guide
3. Contact GCP support
4. File internal ticket

## Contributing

1. Code Contributions
- Follow Python style guide
- Include tests
- Update documentation
- Submit pull request

2. Documentation
- Keep findings up to date
- Document new features
- Update troubleshooting guide
- Share best practices
