#!/usr/bin/env python3

"""
Quota Request Tracking and Management Tool

Helps track quota requests across versions and compare with current allocations.
Also assists in generating new quota request versions.

Author: Ethos
"""

import json
import subprocess
import sys
from typing import Dict, List, Optional
from datetime import datetime
import argparse

class QuotaTracker:
    """Tracks and manages quota requests across versions."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.versions = {
            "v1.0.0": {
                "description": "Initial Request",
                "date": "2024-01-01",
                "quotas": {
                    "NVIDIA_H100_80GB_GPUS": 144,
                    "A3_CPUS": 3744,
                    "PREEMPTIBLE_A3_CPUS": 3744
                }
            },
            "v2.0.0": {
                "description": "Comprehensive Request",
                "date": "2024-02-01",
                "quotas": {
                    "NVIDIA_H100_80GB_GPUS": 144,
                    "A3_CPUS": 3744,
                    "M3_CPUS": 1920,
                    "C4A_CPUS": 2160,
                    "PREEMPTIBLE_A3_CPUS": 3744,
                    "HYPERDISK_ML_IOPS": 8000000,
                    "NETWORK_BANDWIDTH_TBPS": 8.1
                }
            },
            "v2.1.0": {
                "description": "Enhanced Scale (1.5x)",
                "date": "2024-02-15",
                "quotas": {
                    "NVIDIA_H100_80GB_GPUS": 216,
                    "A3_CPUS": 5616,
                    "M3_CPUS": 2880,
                    "C4A_CPUS": 3240,
                    "PREEMPTIBLE_A3_CPUS": 5616,
                    "HYPERDISK_ML_IOPS": 22500000,
                    "NETWORK_BANDWIDTH_TBPS": 12.1
                }
            },
            "v2.2.0": {
                "description": "Advanced Research & GKE",
                "date": "2024-02-20",
                "quotas": {
                    "NVIDIA_H100_80GB_GPUS": 320,
                    "A3_CPUS": 8320,
                    "M3_CPUS": 3840,
                    "C4A_CPUS": 4320,
                    "PREEMPTIBLE_A3_CPUS": 8320,
                    "HYPERDISK_ML_IOPS": 30000000,
                    "NETWORK_BANDWIDTH_TBPS": 17.0,
                    "NVIDIA_A100_GPUS": 256,
                    "A2_CPUS": 2048,
                    "GKE_CPUS": 10000,
                    "GKE_GPUS": 500,
                    "LOCAL_SSD_TOTAL_GB": 180000
                }
            }
        }
    
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
    
    def get_current_quotas(self, region: str) -> Dict:
        """Gets current quota values for the specified region."""
        command = [
            "compute",
            "regions",
            "describe",
            region,
            f"--project={self.project_id}",
            "--format=json"
        ]
        
        output = self.run_command(command)
        if output:
            try:
                data = json.loads(output)
                quotas = {}
                for quota in data.get("quotas", []):
                    quotas[quota["metric"]] = {
                        "limit": quota.get("limit", 0),
                        "usage": quota.get("usage", 0)
                    }
                return quotas
            except json.JSONDecodeError:
                return {}
        return {}
    
    def compare_versions(self, version1: str, version2: str) -> Dict:
        """Compares quota values between two versions."""
        if version1 not in self.versions or version2 not in self.versions:
            return {}
        
        v1_quotas = self.versions[version1]["quotas"]
        v2_quotas = self.versions[version2]["quotas"]
        
        differences = {}
        all_metrics = set(v1_quotas.keys()) | set(v2_quotas.keys())
        
        for metric in all_metrics:
            v1_value = v1_quotas.get(metric, 0)
            v2_value = v2_quotas.get(metric, 0)
            if v1_value != v2_value:
                differences[metric] = {
                    "from": v1_value,
                    "to": v2_value,
                    "change": v2_value - v1_value,
                    "percent": ((v2_value - v1_value) / v1_value * 100) if v1_value else float('inf')
                }
        
        return differences
    
    def generate_next_version(self, base_version: str, multiplier: float = 1.0,
                            description: str = "") -> Dict:
        """Generates a new version based on multiplying an existing version."""
        if base_version not in self.versions:
            return {}
        
        base_quotas = self.versions[base_version]["quotas"]
        new_quotas = {
            metric: value * multiplier
            for metric, value in base_quotas.items()
        }
        
        # Get version components
        parts = base_version.split('.')
        new_version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        
        return {
            "version": new_version,
            "description": description or f"Generated from {base_version} (×{multiplier})",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "quotas": new_quotas
        }
    
    def save_version(self, version_data: Dict) -> None:
        """Saves a new version to the version history."""
        version = version_data.pop("version")
        self.versions[version] = version_data
    
    def generate_report(self, region: str = None) -> str:
        """Generates a report of quota versions and current values."""
        lines = ["# Quota Request Version Report\n"]
        
        # Add current quotas if region specified
        if region:
            current = self.get_current_quotas(region)
            lines.append(f"## Current Quotas ({region})")
            for metric, values in current.items():
                lines.append(f"- {metric}: {values['limit']} (using {values['usage']})")
            lines.append("")
        
        # Add version history
        lines.append("## Version History")
        for version, data in sorted(self.versions.items()):
            lines.append(f"\n### {version} - {data['description']}")
            lines.append(f"Date: {data['date']}")
            lines.append("Quotas:")
            for metric, value in data["quotas"].items():
                lines.append(f"- {metric}: {value}")
        
        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Track and manage quota requests")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--region", help="Region to check current quotas")
    parser.add_argument("--compare", nargs=2, metavar=("V1", "V2"),
                      help="Compare two versions")
    parser.add_argument("--generate", help="Generate new version from base")
    parser.add_argument("--multiplier", type=float, default=1.0,
                      help="Multiplier for new version")
    args = parser.parse_args()
    
    tracker = QuotaTracker(args.project)
    
    if args.compare:
        differences = tracker.compare_versions(args.compare[0], args.compare[1])
        print(f"\nComparing {args.compare[0]} to {args.compare[1]}:")
        for metric, diff in differences.items():
            print(f"{metric}:")
            print(f"  From: {diff['from']}")
            print(f"  To: {diff['to']}")
            print(f"  Change: {diff['change']:+}")
            print(f"  Percent: {diff['percent']:+.1f}%")
    
    elif args.generate:
        new_version = tracker.generate_next_version(
            args.generate,
            args.multiplier,
            f"Generated from {args.generate} (×{args.multiplier})"
        )
        print("\nGenerated new version:")
        print(json.dumps(new_version, indent=2))
    
    else:
        report = tracker.generate_report(args.region)
        print(report)

if __name__ == "__main__":
    main()
