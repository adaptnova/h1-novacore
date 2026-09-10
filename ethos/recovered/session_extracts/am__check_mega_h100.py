#!/usr/bin/env python3

"""
GCP H100 MEGA GPU Quota Check Script

Uses exact filter parameters from console:
- Value: >0
- Dimensions: us-
- Type: Quota
- Name: Preemptible NVIDIA H100 MEGA GPUs

Author: Ethos
"""

import json
import subprocess
import sys
from typing import Dict, List, Optional
from datetime import datetime

# US regions to check
US_REGIONS = [
    "us-central1",
    "us-east1",
    "us-east4",
    "us-east5",
    "us-south1",
    "us-west1",
    "us-west2",
    "us-west3",
    "us-west4"
]

class MegaH100QuotaChecker:
    """Checks H100 MEGA GPU quotas across regions."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.results = {}
    
    def run_gcloud_command(self, command: List[str]) -> Optional[str]:
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
    
    def check_region_quotas(self, region: str):
        """Checks H100 MEGA GPU quotas for a specific region."""
        print(f"\nChecking H100 MEGA GPU quotas in {region}...")
        
        # Use exact filter parameters from console
        command = [
            "compute",
            "regions",
            "describe",
            region,
            f"--project={self.project_id}",
            "--format=json(quotas[?metric='PREEMPTIBLE_NVIDIA_H100_MEGA_GPUS'])"
        ]
        
        output = self.run_gcloud_command(command)
        if output:
            try:
                data = json.loads(output)
                quotas = data.get("quotas", [])
                
                mega_quotas = {}
                for quota in quotas:
                    metric = quota.get("metric", "")
                    if "H100_MEGA" in metric:
                        mega_quotas[metric] = {
                            "limit": quota.get("limit", 0),
                            "usage": quota.get("usage", 0)
                        }
                
                self.results[region] = mega_quotas
                
                # Print current quotas
                if mega_quotas:
                    for metric, data in mega_quotas.items():
                        usage_pct = (data["usage"] / data["limit"] * 100) if data["limit"] > 0 else 0
                        print(f"{metric}: {data['usage']}/{data['limit']} ({usage_pct:.1f}%)")
                else:
                    print("No H100 MEGA GPU quotas found")
            
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for region {region}: {e}", file=sys.stderr)
    
    def check_all_regions(self):
        """Checks H100 MEGA GPU quotas across all US regions."""
        for region in US_REGIONS:
            self.check_region_quotas(region)
    
    def save_results(self, filename: str):
        """Saves results to a JSON file."""
        output = {
            "timestamp": datetime.now().isoformat(),
            "project_id": self.project_id,
            "quotas": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def generate_summary(self) -> str:
        """Generates a human-readable summary of H100 MEGA GPU quotas."""
        summary = []
        summary.append("# H100 MEGA GPU Quota Summary")
        summary.append(f"\nProject: {self.project_id}")
        summary.append(f"Generated: {datetime.now().isoformat()}\n")
        
        for region in self.results:
            summary.append(f"\n## {region}")
            quotas = self.results[region]
            if quotas:
                for metric, data in quotas.items():
                    usage_pct = (data["usage"] / data["limit"] * 100) if data["limit"] > 0 else 0
                    summary.append(f"\n{metric}:")
                    summary.append(f"- Limit: {data['limit']}")
                    summary.append(f"- Usage: {data['usage']} ({usage_pct:.1f}%)")
            else:
                summary.append("\nNo H100 MEGA GPU quotas found")
        
        return "\n".join(summary)
    
    def save_summary(self, filename: str):
        """Saves the summary to a markdown file."""
        summary = self.generate_summary()
        with open(filename, 'w') as f:
            f.write(summary)
        
        print(f"Summary saved to {filename}")

def main():
    """Main function to run H100 MEGA GPU quota checks."""
    project_id = "a-d-a-p-t"
    checker = MegaH100QuotaChecker(project_id)
    
    print("Starting H100 MEGA GPU quota check across US regions...")
    checker.check_all_regions()
    
    # Save detailed results
    checker.save_results("mega_h100_quota_details.json")
    
    # Save human-readable summary
    checker.save_summary("mega_h100_quota_summary.md")
    
    print("\nH100 MEGA GPU quota check complete!")

if __name__ == "__main__":
    main()
