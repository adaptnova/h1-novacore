#!/usr/bin/env python3

import os
import sys
import logging
import json
import subprocess
from datetime import datetime
import time
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('launch_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class LaunchMonitor:
    def __init__(self):
        self.status = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S MST"),
            "components": {},
            "issues": [],
            "emergency_threshold": 3  # Number of critical issues before suggesting emergency mode
        }

        self.sender_info = {
            "name": "Nova Launch Monitor",
            "id": f"monitor_{socket.gethostname()}",
            "team": "Nova Integration"
        }

        self.critical_components = {
            "database": {
                "services": ["postgresql", "mongodb", "neo4j"],
                "weight": 2
            },
            "messaging": {
                "services": ["rabbitmq", "kafka"],
                "weight": 2
            },
            "llm": {
                "services": ["openai", "anthropic"],
                "weight": 1
            },
            "vector_store": {
                "services": ["chroma", "milvus"],
                "weight": 1
            },
            "hitl": {
                "services": ["slack", "command_gui"],
                "weight": 3
            }
        }

    def check_service(self, service):
        """Check individual service status"""
        try:
            # Use basic system commands to check service availability
            if service == "postgresql":
                result = subprocess.run(["pg_isready"], capture_output=True)
                return result.returncode == 0
            elif service == "mongodb":
                result = subprocess.run(["mongosh", "--eval", "db.runCommand({ping:1})"], capture_output=True)
                return result.returncode == 0
            elif service == "neo4j":
                result = subprocess.run(["neo4j", "status"], capture_output=True)
                return result.returncode == 0
            elif service in ["rabbitmq", "kafka"]:
                # Check port availability as basic test
                ports = {"rabbitmq": 5672, "kafka": 9092}
                result = subprocess.run(["nc", "-z", "localhost", str(ports[service])], capture_output=True)
                return result.returncode == 0
            elif service in ["openai", "anthropic"]:
                # Check API key presence
                return bool(os.getenv(f"{service.upper()}_API_KEY"))
            elif service in ["chroma", "milvus"]:
                # Check if services are running on their ports
                ports = {"chroma": 8000, "milvus": 19530}
                result = subprocess.run(["nc", "-z", "localhost", str(ports[service])], capture_output=True)
                return result.returncode == 0
            elif service == "slack":
                # Test Slack webhook
                webhook_url = os.getenv("SLACK_WEBHOOK_URL")
                if not webhook_url:
                    return False
                result = subprocess.run(["wget", "--spider", webhook_url], capture_output=True)
                return result.returncode == 0
            elif service == "command_gui":
                # Check if command GUI port is accessible
                result = subprocess.run(["nc", "-z", "localhost", "3001"], capture_output=True)
                return result.returncode == 0
            return False
        except Exception as e:
            logger.error(f"Error checking {service}: {str(e)}")
            return False

    def check_all_services(self):
        """Check all critical services"""
        issue_count = 0

        for component, config in self.critical_components.items():
            component_status = {
                "services": {},
                "status": "PENDING",
                "weight": config["weight"]
            }

            failed_services = []
            for service in config["services"]:
                service_ok = self.check_service(service)
                component_status["services"][service] = "READY" if service_ok else "ERROR"
                if not service_ok:
                    failed_services.append(service)
                    issue_count += config["weight"]

            if failed_services:
                component_status["status"] = "ERROR"
                self.status["issues"].append({
                    "component": component,
                    "failed_services": failed_services,
                    "weight": config["weight"]
                })
            else:
                component_status["status"] = "READY"

            self.status["components"][component] = component_status

        return issue_count

    def should_use_emergency_mode(self):
        """Determine if emergency mode should be activated"""
        issue_count = self.check_all_services()

        # Check if any critical components (weight >= 2) have failed
        critical_failures = any(
            issue["weight"] >= 2
            for issue in self.status["issues"]
        )

        # Check if total issues exceed threshold
        threshold_exceeded = issue_count >= self.status["emergency_threshold"]

        return critical_failures or threshold_exceeded

    def generate_report(self):
        """Generate status report"""
        report = [
            "# Launch Status Report",
            f"Time: {self.status['timestamp']}\n",
            f"From: {self.sender_info['name']} ({self.sender_info['id']})",
            f"To: Nova Integration Team\n"
        ]

        # Component Status
        report.append("## Component Status")
        for component, status in self.status["components"].items():
            report.append(f"\n### {component}")
            report.append("```yaml")
            report.append(json.dumps(status, indent=2))
            report.append("```")

        # Issues
        if self.status["issues"]:
            report.append("\n## Issues Detected")
            for issue in self.status["issues"]:
                report.append(f"\n- {issue['component']}")
                report.append(f"  Failed services: {', '.join(issue['failed_services'])}")
                report.append(f"  Impact weight: {issue['weight']}")

        # Recommendation
        report.append("\n## Recommendation")
        if self.should_use_emergency_mode():
            report.append("⚠️ SWITCH TO EMERGENCY MODE RECOMMENDED")
            report.append("\nRationale:")
            report.append("- Critical component failures detected")
            report.append(f"- Issue count exceeds threshold ({len(self.status['issues'])} issues)")
        else:
            report.append("✅ Continue with standard launch")
            report.append("\nAll critical systems operational")

        return "\n".join(report)

    def notify_status(self):
        """Send status update to Slack"""
        try:
            emergency_mode = self.should_use_emergency_mode()
            icon = "🚨" if emergency_mode else "✅"

            # Format message with proper headers
            message = {
                "text": (
                    f"{icon} Launch Status Update\n\n"
                    f"From: {self.sender_info['name']} ({self.sender_info['id']})\n"
                    f"To: @nova-team\n"
                    f"Team: {self.sender_info['team']}\n"
                    f"Time: {self.status['timestamp']}\n\n"
                    f"Status: {'SWITCH TO EMERGENCY MODE' if emergency_mode else 'PROCEED WITH STANDARD LAUNCH'}\n\n"
                    f"Issues: {len(self.status['issues'])}\n"
                    f"Critical Components: {sum(1 for c in self.status['components'].values() if c['status'] == 'READY')}/{len(self.critical_components)} ready\n\n"
                    f"See detailed report in launch_monitor.log"
                ),
                "metadata": {
                    "sender": self.sender_info,
                    "timestamp": self.status['timestamp'],
                    "priority": "high" if emergency_mode else "normal"
                }
            }

            subprocess.run([
                "wget",
                "--post-data=" + json.dumps(message),
                "--header=Content-Type: application/json",
                "https://hooks.slack.com/services/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",
                "-O", "/dev/null"
            ])

        except Exception as e:
            logger.error(f"Failed to send status notification: {str(e)}")

def main():
    try:
        monitor = LaunchMonitor()
        logger.info("Starting launch status monitoring...")

        # Check services and generate report
        monitor.check_all_services()
        report = monitor.generate_report()

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"launch_status_{timestamp}.md"
        with open(filename, 'w') as f:
            f.write(report)

        logger.info(f"Status report saved to {filename}")

        # Notify team
        monitor.notify_status()

        # Exit with status code
        emergency_mode = monitor.should_use_emergency_mode()
        if emergency_mode:
            logger.warning("Recommending switch to emergency mode")
            sys.exit(1)
        else:
            logger.info("Standard launch recommended")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Monitoring failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
