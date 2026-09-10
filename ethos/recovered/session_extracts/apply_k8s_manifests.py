#!/usr/bin/env python3

"""
Kubernetes GPU Manifests Management Script

Helps manage and apply Kubernetes manifests for GPU workloads in the correct order.
Handles namespace creation, priority classes, quotas, and workload deployment.

Author: Ethos
"""

import argparse
import subprocess
import sys
import time
import yaml
from typing import Dict, List, Optional
from datetime import datetime

class K8sManifestManager:
    """Manages Kubernetes manifests for GPU workloads."""
    
    def __init__(self, manifest_file: str):
        self.manifest_file = manifest_file
        self.manifests = self.load_manifests()
        
    def run_command(self, command: List[str]) -> Optional[str]:
        """Runs a kubectl command and returns the output."""
        try:
            result = subprocess.run(
                ["kubectl"] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}", file=sys.stderr)
            print(f"Error output: {e.stderr}", file=sys.stderr)
            return None
    
    def load_manifests(self) -> List[Dict]:
        """Loads manifests from YAML file."""
        try:
            with open(self.manifest_file, 'r') as f:
                return list(yaml.safe_load_all(f))
        except Exception as e:
            print(f"Error loading manifests: {e}", file=sys.stderr)
            return []
    
    def create_namespaces(self) -> bool:
        """Creates required namespaces."""
        namespaces = {
            "production": "Production workloads",
            "research": "Research workloads",
            "monitoring": "Monitoring and observability"
        }
        
        for ns, description in namespaces.items():
            print(f"\nCreating namespace {ns}...")
            manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": ns,
                    "labels": {
                        "name": ns
                    },
                    "annotations": {
                        "description": description
                    }
                }
            }
            
            if not self.apply_manifest(manifest):
                return False
        
        return True
    
    def apply_manifest(self, manifest: Dict) -> bool:
        """Applies a single manifest."""
        try:
            # Write manifest to temporary file
            with open('temp_manifest.yaml', 'w') as f:
                yaml.dump(manifest, f)
            
            # Apply manifest
            result = self.run_command(['apply', '-f', 'temp_manifest.yaml'])
            
            # Clean up
            subprocess.run(['rm', 'temp_manifest.yaml'])
            
            return result is not None
            
        except Exception as e:
            print(f"Error applying manifest: {e}", file=sys.stderr)
            return False
    
    def apply_manifests_by_kind(self, kind: str) -> bool:
        """Applies all manifests of a specific kind."""
        manifests = [m for m in self.manifests if m.get('kind') == kind]
        if not manifests:
            return True
        
        print(f"\nApplying {kind} manifests...")
        for manifest in manifests:
            if not self.apply_manifest(manifest):
                return False
        
        return True
    
    def deploy_all(self) -> bool:
        """Deploys all manifests in the correct order."""
        # Create namespaces first
        if not self.create_namespaces():
            return False
        
        # Order of deployment
        deployment_order = [
            "PriorityClass",
            "StorageClass",
            "ResourceQuota",
            "NetworkPolicy",
            "PodMonitoring",
            "AlertPolicy",
            "Job",
            "Deployment"
        ]
        
        for kind in deployment_order:
            if not self.apply_manifests_by_kind(kind):
                return False
        
        return True
    
    def verify_deployment(self) -> bool:
        """Verifies the deployment status."""
        print("\nVerifying deployment...")
        
        # Check namespaces
        if not self.run_command(['get', 'namespaces']):
            return False
        
        # Check priority classes
        if not self.run_command(['get', 'priorityclasses']):
            return False
        
        # Check quotas
        if not self.run_command(['get', 'resourcequotas', '--all-namespaces']):
            return False
        
        # Check deployments
        if not self.run_command(['get', 'deployments', '--all-namespaces']):
            return False
        
        return True
    
    def cleanup(self) -> bool:
        """Cleans up all deployed resources."""
        print("\nCleaning up resources...")
        
        cleanup_order = [
            "Deployment",
            "Job",
            "AlertPolicy",
            "PodMonitoring",
            "NetworkPolicy",
            "ResourceQuota",
            "StorageClass",
            "PriorityClass"
        ]
        
        for kind in cleanup_order:
            manifests = [m for m in self.manifests if m.get('kind') == kind]
            for manifest in manifests:
                name = manifest['metadata']['name']
                namespace = manifest['metadata'].get('namespace', 'default')
                self.run_command(['delete', kind.lower(), name, '-n', namespace])
        
        # Delete namespaces last
        namespaces = ["production", "research", "monitoring"]
        for ns in namespaces:
            self.run_command(['delete', 'namespace', ns])
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Manage Kubernetes GPU manifests"
    )
    parser.add_argument("--manifest-file", required=True,
                      help="Path to manifest YAML file")
    parser.add_argument("--action", choices=['apply', 'verify', 'cleanup'],
                      default='apply',
                      help="Action to perform")
    
    args = parser.parse_args()
    
    manager = K8sManifestManager(args.manifest_file)
    
    if args.action == 'apply':
        success = manager.deploy_all()
        if success:
            success = manager.verify_deployment()
    elif args.action == 'verify':
        success = manager.verify_deployment()
    else:  # cleanup
        success = manager.cleanup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
