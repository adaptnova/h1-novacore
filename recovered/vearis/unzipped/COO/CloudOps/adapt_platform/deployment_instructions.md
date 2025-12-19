# Deployment Instructions for IBM Cloud Infrastructure

## Prerequisites

Before beginning the deployment, ensure you have the following:

1. **IBM Cloud CLI** installed and configured
2. **IBM Cloud account** with appropriate permissions
3. **SSH key** uploaded to IBM Cloud
4. **Quota** available for the required resources

## Deployment Process

The deployment is divided into two phases:

1. Deploy the ethos GPU server first
2. After confirming GPU server functionality, deploy the remaining infrastructure

### Phase 1: Deploy the ethos GPU Server

1. **Login to IBM Cloud CLI**
   ```bash
   ibmcloud login
   ```

2. **Target the appropriate resource group and region**
   ```bash
   ibmcloud target -g adapt -r us-south
   ```

3. **Run the GPU server deployment script**
   ```bash
   cd /data-nova/ax/COO/CloudOps
   ./adapt_platform/deploy_ethos_gpu.sh
   ```

4. **Monitor the deployment progress**
   The script will provide real-time updates on the deployment status.

5. **Verify GPU functionality**
   Once the server is deployed, SSH to the server and run:
   ```bash
   nvidia-smi
   ```
   This should display information about the NVIDIA GPUs.

### Phase 2: Deploy the Remaining Infrastructure

1. **Ensure the ethos GPU server is running**
   Verify the server status in the IBM Cloud console or using:
   ```bash
   ibmcloud is instance ethos
   ```

2. **Run the remaining infrastructure deployment script**
   ```bash
   cd /data-nova/ax/COO/CloudOps
   ./adapt_platform/deploy_remaining_infrastructure.sh
   ```

3. **Monitor the deployment progress**
   The script will provide real-time updates on the deployment status.

4. **Verify all servers are running**
   Check the status of all servers:
   ```bash
   ibmcloud is instances
   ```

## Deployment Scripts

The deployment scripts are designed to automate the entire process:

- **deploy_ethos_gpu.sh**: Deploys the ethos GPU server with the following steps:
  - Creates security group with appropriate rules
  - Creates storage volumes with specified IOPS
  - Deploys the server with the gx3-48x240x2l40s profile
  - Configures the server with NVIDIA drivers and CUDA
  - Sets up monitoring and optimization

- **deploy_remaining_infrastructure.sh**: Deploys the remaining servers with the following steps:
  - Creates security groups for database and logging servers
  - Creates storage volumes for all servers
  - Deploys the database servers (primary, graph, timeseries)
  - Deploys the logging server
  - Provides instructions for renaming adapt3 to adapt

## Troubleshooting

If you encounter issues during deployment:

1. **Check IBM Cloud status**
   Verify that the IBM Cloud services are operational.

2. **Verify resource availability**
   Ensure that the required resources (especially GPU) are available in the selected region.

3. **Check script logs**
   The deployment scripts provide detailed output that can help identify issues.

4. **Verify network connectivity**
   Ensure that the VPC and subnet are properly configured.

5. **Check security group rules**
   Verify that the security group rules allow the necessary traffic.

## Post-Deployment Tasks

After successful deployment:

1. **Configure monitoring**
   Set up monitoring dashboards in Grafana.

2. **Configure log forwarding**
   Ensure all servers are forwarding logs to the logging server.

3. **Create backup schedules**
   Configure regular snapshots for all volumes.

4. **Document final configuration**
   Update documentation with the actual server details.

5. **Prepare for Project Tapestry integration**
   Begin planning for the integration with Project Tapestry in Q2 2025.

## Contact Information

For assistance with deployment issues, contact:

- **Cloud Operations Team**: cloudops@nova.ai
- **Infrastructure Support**: infrastructure@nova.ai