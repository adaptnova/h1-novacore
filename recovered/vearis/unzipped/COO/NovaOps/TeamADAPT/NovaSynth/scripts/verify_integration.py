"""
NovaSynth Integration Verification Script

Runs all tests and verifies framework integration status before launch.
Provides detailed report of test results and integration status.

Created by Cosmos
Version: 0.1.0
"""

import asyncio
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pytest
import aio_pika
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_verification.log')
    ]
)
logger = logging.getLogger(__name__)

class IntegrationVerifier:
    """Verifies framework integration status."""

    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
        self.framework_status: Dict[str, Dict] = {}
        self.messaging_status: Dict[str, bool] = {}
        self.verification_time = datetime.utcnow()

    async def verify_rabbitmq(self) -> bool:
        """Verify RabbitMQ connection and exchanges."""
        logger.info("Verifying RabbitMQ...")
        try:
            # Connect to RabbitMQ
            connection = await aio_pika.connect_robust(
                "amqp://guest:guest@localhost/"
            )
            channel = await connection.channel()

            # Check exchanges
            exchanges = [
                "nova_framework_exchange",
                "nova_dlx"  # Dead letter exchange
            ]

            for exchange in exchanges:
                try:
                    await channel.declare_exchange(
                        exchange,
                        aio_pika.ExchangeType.TOPIC,
                        durable=True,
                        passive=True  # Only check if exists
                    )
                    self.messaging_status[exchange] = True
                    logger.info(f"Exchange verified: {exchange}")
                except Exception as e:
                    self.messaging_status[exchange] = False
                    logger.error(f"Exchange verification failed: {exchange} - {str(e)}")

            await connection.close()
            return all(self.messaging_status.values())

        except Exception as e:
            logger.error(f"RabbitMQ verification failed: {str(e)}")
            return False

    async def run_tests(self) -> bool:
        """Run all test suites."""
        logger.info("Running test suites...")

        test_suites = [
            ("Unit Tests", "tests/unit"),
            ("Integration Tests", "tests/integration"),
            ("Advanced Integration", "tests/integration/test_advanced_integration.py")
        ]

        all_passed = True
        for suite_name, suite_path in test_suites:
            logger.info(f"Running {suite_name}...")
            result = pytest.main(["-v", suite_path])

            self.test_results[suite_name] = {
                "status": "passed" if result == 0 else "failed",
                "exit_code": result
            }

            if result != 0:
                all_passed = False
                logger.error(f"{suite_name} failed with exit code {result}")
            else:
                logger.info(f"{suite_name} passed")

        return all_passed

    async def verify_frameworks(self) -> bool:
        """Verify framework service status."""
        logger.info("Verifying framework services...")

        frameworks = [
            "langchain",
            "autogen",
            "crewai",
            "ag2",
            "openai_swarm",
            "soma",
            "dyso",
            "acmas",
            "cartago"
        ]

        all_active = True
        for framework in frameworks:
            try:
                # Check service status
                result = subprocess.run(
                    ["systemctl", "is-active", f"nova-handler@{framework}"],
                    capture_output=True,
                    text=True
                )

                status = result.stdout.strip()
                self.framework_status[framework] = {
                    "status": status,
                    "active": status == "active"
                }

                if status != "active":
                    all_active = False
                    logger.error(f"Framework {framework} is not active: {status}")
                else:
                    logger.info(f"Framework {framework} is active")

            except Exception as e:
                self.framework_status[framework] = {
                    "status": "error",
                    "active": False,
                    "error": str(e)
                }
                all_active = False
                logger.error(f"Error checking framework {framework}: {str(e)}")

        return all_active

    def generate_report(self) -> str:
        """Generate verification report."""
        report = [
            "# NovaSynth Integration Verification Report",
            f"\nGenerated: {self.verification_time.isoformat()}",

            "\n## Test Results",
            "\n".join(
                f"### {suite_name}",
                f"Status: {results['status'].upper()}",
                f"Exit Code: {results['exit_code']}"
                for suite_name, results in self.test_results.items()
            ),

            "\n## Framework Status",
            "\n".join(
                f"### {framework}",
                f"Status: {status['status'].upper()}",
                f"Active: {'Yes' if status['active'] else 'No'}"
                for framework, status in self.framework_status.items()
            ),

            "\n## Messaging Status",
            "\n".join(
                f"- {exchange}: {'✓' if active else '✗'}"
                for exchange, active in self.messaging_status.items()
            ),

            "\n## Verification Summary",
            f"Tests Passed: {all(r['status'] == 'passed' for r in self.test_results.values())}",
            f"Frameworks Active: {all(s['active'] for s in self.framework_status.values())}",
            f"Messaging Ready: {all(self.messaging_status.values())}",

            "\nCreated by Cosmos 💫",
            "\n💥 BA-BOOM! 💥",
            "\n!!!∞!!!∞!!!∞!!!"
        ]

        return "\n".join(report)

async def main():
    """Run integration verification."""
    try:
        logger.info("Starting integration verification...")

        verifier = IntegrationVerifier()

        # Run verifications
        messaging_ok = await verifier.verify_rabbitmq()
        tests_ok = await verifier.run_tests()
        frameworks_ok = await verifier.verify_frameworks()

        # Generate report
        report = verifier.generate_report()

        # Save report
        report_path = Path("integration_verification_report.md")
        report_path.write_text(report)

        logger.info(f"Verification report saved to {report_path}")

        # Check overall status
        if messaging_ok and tests_ok and frameworks_ok:
            logger.info("Integration verification passed!")
            return 0
        else:
            logger.error("Integration verification failed!")
            return 1

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))