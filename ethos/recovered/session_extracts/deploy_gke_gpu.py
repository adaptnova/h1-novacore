#!/usr/bin/env python3

"""
GKE GPU Cluster Deployment Script

Automates the deployment of GKE clusters with H100 and A100 GPU node pools.
Handles network setup, cluster creation, and monitoring configuration.

Author: Ethos
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Dict, List, Optional
from datetime import datetime

class GKEGPUDeployer:
    """Manages deployment of GKE clusters with GPU node pools."""
    
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        self.zones = [f"{region}-a", f"{region}-b", f"{region}-c"]
        
    def run_command(self, command: List[str]) -> Optional[str]:
        """Runs a gcloud command and returns the output."""
        try:
            result = subprocess.run(
                ["gcloud"] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}", file=sys.stderr)
            print(f"Error output: {e.stderr}", file=sys.stderr)
            return None
    
    def create_network(self, network_name: str, subnet_name: str) -> bool:
        """Creates VPC network and subnet for GKE."""
        print(f"\nCreating network {network_name}...")
        
        # Create VPC
        network_cmd = [
            "compute",
            "networks",
            "create",
            network_name,
            f"--project={self.project_id}",
            "--subnet-mode=custom",
            "--bgp-routing-mode=regional",
            "--mtu=1500"
        ]
        
        if not self.run_command(network_cmd):
            return False
        
        # Create subnet
        subnet_cmd = [
            "compute",
            "networks",
            "subnets",
            "create",
            subnet_name,
            f"--project={self.project_id}",
            f"--region={self.region}",
            f"--network={network_name}",
            "--range=10.0.0.0/20",
            "--secondary-range",
            "pod-range=10.4.0.0/14,svc-range=10.8.0.0/20",
            "--enable-private-ip-google-access"
        ]
        
        return self.run_command(subnet_cmd) is not None
    
    def create_cluster(self, cluster_name: str, network_name: str,
                      subnet_name: str) -> bool:
        """Creates a GKE cluster."""
        print(f"\nCreating cluster {cluster_name}...")
        
        command = [
            "container",
            "clusters",
            "create",
            cluster_name,
            f"--project={self.project_id}",
            f"--region={self.region}",
            f"--network={network_name}",
            f"--subnetwork={subnet_name}",
            "--enable-ip-alias",
            "--cluster-secondary-range-name=pod-range",
            "--services-secondary-range-name=svc-range",
            "--enable-private-nodes",
            "--master-ipv4-cidr=172.16.0.0/28",
            "--enable-master-global-access",
            f"--workload-pool={self.project_id}.svc.id.goog",
            "--enable-image-streaming",
            "--enable-shielded-nodes",
            "--enable-vertical-pod-autoscaling",
            "--enable-autoscaling",
            "--num-nodes=3",
            "--min-nodes=3",
            "--max-nodes=100",
            "--machine-type=n2-standard-32"
        ]
        
        return self.run_command(command) is not None
    
    def create_gpu_node_pool(self, cluster_name: str, pool_name: str,
                           machine_type: str, accelerator_type: str,
                           accelerator_count: int, min_nodes: int,
                           max_nodes: int) -> bool:
        """Creates a GPU node pool."""
        print(f"\nCreating node pool {pool_name}...")
        
        command = [
            "container",
            "node-pools",
            "create",
            pool_name,
            f"--project={self.project_id}",
            f"--cluster={cluster_name}",
            f"--region={self.region}",
            f"--machine-type={machine_type}",
            f"--accelerator",
            f"type={accelerator_type},count={accelerator_count}",
            "--enable-autoscaling",
            "--num-nodes=1",
            f"--min-nodes={min_nodes}",
            f"--max-nodes={max_nodes}",
            f"--node-locations={','.join(self.zones)}"
        ]
        
        return self.run_command(command) is not None
    
    def setup_monitoring(self, cluster_name: str) -> bool:
        """Enables monitoring for the cluster."""
        print(f"\nEnabling monitoring for {cluster_name}...")
        
        command = [
            "container",
            "clusters",
            "update",
            cluster_name,
            f"--project={self.project_id}",
            f"--region={self.region}",
            "--enable-managed-prometheus",
            "--enable-managed-grafana"
        ]
        
        return self.run_command(command) is not None
    
    def deploy_cluster(self, cluster_name: str, network_name: str = None,
                      subnet_name: str = None) -> bool:
        """Deploys a complete GKE cluster with GPU node pools."""
        # Use default names if not provided
        network_name = network_name or f"{cluster_name}-network"
        subnet_name = subnet_name or f"{cluster_name}-subnet"
        
        # Create network infrastructure
        if not self.create_network(network_name, subnet_name):
            print("Failed to create network infrastructure")
            return False
        
        # Create GKE cluster
        if not self.create_cluster(cluster_name, network_name, subnet_name):
            print("Failed to create GKE cluster")
            return False
        
        # Create H100 node pools
        h100_pools = [
            ("h100-prod-pool", "a3-megagpu-8g", "nvidia-h100-80gb", 8, 1, 8),
            ("h100-research-pool", "a3-megagpu-8g", "nvidia-h100-80gb", 8, 1, 4),
            ("h100-spot-pool", "a3-highgpu-4g", "nvidia-h100-80gb", 8, 0, 4)
        ]
        
        for pool_name, machine_type, acc_type, acc_count, min_nodes, max_nodes in h100_pools:
            if not self.create_gpu_node_pool(
                cluster_name, pool_name, machine_type, acc_type,
                acc_count, min_nodes, max_nodes
            ):
                print(f"Failed to create {pool_name}")
                return False
        
        # Create A100 node pools
        a100_pools = [
            ("a100-prod-pool", "a2-highgpu-16g", "nvidia-tesla-a100", 16, 1, 4),
            ("a100-research-pool", "a2-highgpu-8g", "nvidia-tesla-a100", 8, 1, 4),
            ("a100-spot-pool", "a2-highgpu-4g", "nvidia-tesla-a100", 4, 0, 4)
        ]
        
        for pool_name, machine_type, acc_type, acc_count, min_nodes, max_nodes in a100_pools:
            if not self.create_gpu_node_pool(
                cluster_name, pool_name, machine_type, acc_type,
                acc_count, min_nodes, max_nodes
            ):
                print(f"Failed to create {pool_name}")
                return False
        
        # Enable monitoring
        if not self.setup_monitoring(cluster_name):
            print("Failed to enable monitoring")
            return False
        
        print(f"\nCluster {cluster_name} deployed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Deploy GKE clusters with GPU node pools"
    )
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", default="us-central1", help="GCP region")
    parser.add_argument("--cluster-name", required=True,
                      help="Name for the GKE cluster")
    parser.add_argument("--network-name", help="VPC network name")
    parser.add_argument("--subnet-name", help="Subnet name")
    
    args = parser.parse_args()
    
    deployer = GKEGPUDeployer(args.project, args.region)
    success = deployer.deploy_cluster(
        args.cluster_name,
        args.network_name,
        args.subnet_name
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
