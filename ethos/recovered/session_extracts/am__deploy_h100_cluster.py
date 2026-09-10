#!/usr/bin/env python3

"""
H100/A3 Cluster Deployment Script

Automates the deployment of H100 instances on Google Cloud Platform.
Handles both production and spot instances with proper configuration.

Author: Ethos
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Dict, List, Optional
from datetime import datetime

class H100ClusterDeployer:
    """Manages deployment of H100/A3 clusters."""
    
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
    
    def create_network(self, network_name: str) -> bool:
        """Creates a VPC network for the H100 cluster."""
        print(f"\nCreating network {network_name}...")
        
        command = [
            "compute",
            "networks",
            "create",
            network_name,
            f"--project={self.project_id}",
            "--subnet-mode=custom"
        ]
        
        return self.run_command(command) is not None
    
    def create_subnet(self, network_name: str, subnet_name: str, zone: str, 
                     cidr_range: str) -> bool:
        """Creates a subnet in the specified zone."""
        print(f"\nCreating subnet {subnet_name} in {zone}...")
        
        command = [
            "compute",
            "networks",
            "subnets",
            "create",
            subnet_name,
            f"--project={self.project_id}",
            f"--network={network_name}",
            f"--region={self.region}",
            f"--range={cidr_range}"
        ]
        
        return self.run_command(command) is not None
    
    def create_firewall_rules(self, network_name: str) -> bool:
        """Creates necessary firewall rules."""
        print("\nCreating firewall rules...")
        
        # Allow internal communication
        internal_rule = [
            "compute",
            "firewall-rules",
            "create",
            f"{network_name}-allow-internal",
            f"--project={self.project_id}",
            f"--network={network_name}",
            "--allow=tcp,udp,icmp",
            "--source-ranges=10.0.0.0/8"
        ]
        
        # Allow SSH access
        ssh_rule = [
            "compute",
            "firewall-rules",
            "create",
            f"{network_name}-allow-ssh",
            f"--project={self.project_id}",
            f"--network={network_name}",
            "--allow=tcp:22",
            "--source-ranges=0.0.0.0/0"
        ]
        
        return (self.run_command(internal_rule) is not None and 
                self.run_command(ssh_rule) is not None)
    
    def create_instance(self, name: str, zone: str, machine_type: str,
                       network_name: str, subnet_name: str, 
                       is_spot: bool = False) -> bool:
        """Creates an H100 instance."""
        print(f"\nCreating instance {name} in {zone}...")
        
        command = [
            "compute",
            "instances",
            "create",
            name,
            f"--project={self.project_id}",
            f"--zone={zone}",
            f"--machine-type={machine_type}",
            "--maintenance-policy=TERMINATE",
            "--image-family=debian-11",
            "--image-project=debian-cloud",
            "--boot-disk-size=200GB",
            "--boot-disk-type=pd-ssd",
            "--local-ssd=interface=NVME",
            "--local-ssd=interface=NVME",
            "--local-ssd=interface=NVME",
            "--local-ssd=interface=NVME",
            f"--network={network_name}",
            f"--subnet={subnet_name}",
            "--metadata=startup-script=#! /bin/bash\n"
            "apt-get update\n"
            "apt-get install -y build-essential\n"
            "curl -O https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/cuda-keyring_1.0-1_all.deb\n"
            "dpkg -i cuda-keyring_1.0-1_all.deb\n"
            "apt-get update\n"
            "apt-get install -y cuda-drivers"
        ]
        
        if is_spot:
            command.extend([
                "--provisioning-model=SPOT",
                "--instance-termination-action=STOP"
            ])
        
        return self.run_command(command) is not None
    
    def deploy_production_cluster(self, base_name: str, machine_type: str,
                                instances_per_zone: int) -> bool:
        """Deploys a production cluster across zones."""
        print("\nDeploying production cluster...")
        
        # Create network infrastructure
        network_name = f"{base_name}-network"
        if not self.create_network(network_name):
            return False
        
        # Create subnets in each zone
        for i, zone in enumerate(self.zones):
            subnet_name = f"{base_name}-subnet-{zone[-1]}"
            cidr_range = f"10.{i}.0.0/16"
            if not self.create_subnet(network_name, subnet_name, zone, cidr_range):
                return False
        
        # Create firewall rules
        if not self.create_firewall_rules(network_name):
            return False
        
        # Create instances in each zone
        for zone in self.zones:
            subnet_name = f"{base_name}-subnet-{zone[-1]}"
            for i in range(instances_per_zone):
                instance_name = f"{base_name}-{zone[-1]}-{i}"
                if not self.create_instance(instance_name, zone, machine_type,
                                         network_name, subnet_name):
                    return False
        
        return True
    
    def deploy_spot_cluster(self, base_name: str, machine_type: str,
                          instances_per_zone: int) -> bool:
        """Deploys a spot instance cluster."""
        print("\nDeploying spot cluster...")
        
        network_name = f"{base_name}-network"
        
        # Create instances in each zone
        for zone in self.zones:
            subnet_name = f"{base_name}-subnet-{zone[-1]}"
            for i in range(instances_per_zone):
                instance_name = f"{base_name}-spot-{zone[-1]}-{i}"
                if not self.create_instance(instance_name, zone, machine_type,
                                         network_name, subnet_name, is_spot=True):
                    return False
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Deploy H100/A3 clusters on GCP")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", default="us-central1", help="GCP region")
    parser.add_argument("--name", required=True, help="Base name for resources")
    parser.add_argument("--prod-instances", type=int, default=2,
                      help="Number of production instances per zone")
    parser.add_argument("--spot-instances", type=int, default=1,
                      help="Number of spot instances per zone")
    args = parser.parse_args()
    
    deployer = H100ClusterDeployer(args.project, args.region)
    
    # Deploy production cluster with a3-megagpu-8g
    if args.prod_instances > 0:
        success = deployer.deploy_production_cluster(
            args.name,
            "a3-megagpu-8g",
            args.prod_instances
        )
        if not success:
            print("Failed to deploy production cluster")
            return 1
    
    # Deploy spot cluster with a3-highgpu-4g
    if args.spot_instances > 0:
        success = deployer.deploy_spot_cluster(
            args.name,
            "a3-highgpu-4g",
            args.spot_instances
        )
        if not success:
            print("Failed to deploy spot cluster")
            return 1
    
    print("\nDeployment completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
