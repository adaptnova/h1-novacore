#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('slack_test.log')
    ]
)
logger = logging.getLogger(__name__)

class SlackTester:
    def __init__(self, token: str):
        self.client = AsyncWebClient(token=token)
        self.channels = {
            "nova-911": {
                "purpose": "Emergency response",
                "priority": "critical"
            },
            "nova-launch-status": {
                "purpose": "Launch coordination",
                "priority": "high"
            },
            "nova-db-ops": {
                "purpose": "Database operations",
                "priority": "high"
            },
            "nova-mq-ops": {
                "purpose": "Message queue operations",
                "priority": "high"
            },
            "nova-framework": {
                "purpose": "Framework coordination",
                "priority": "high"
            },
            "nova-monitor": {
                "purpose": "System monitoring",
                "priority": "medium"
            }
        }

    async def test_channel(self, channel: str) -> dict:
        """Test posting to a specific channel"""
        try:
            # Post test message
            response = await self.client.chat_postMessage(
                channel=f"#{channel}",
                text=f"Nova Integration Test - {datetime.now().strftime('%H:%M:%S MST')}\nTesting channel connectivity for {self.channels[channel]['purpose']}\nPriority: {self.channels[channel]['priority']}"
            )

            # Verify message was sent
            if response["ok"]:
                # Try to add reaction to verify permissions
                await self.client.reactions_add(
                    channel=response["channel"],
                    timestamp=response["ts"],
                    name="white_check_mark"
                )

                return {
                    "status": "success",
                    "message_id": response["ts"],
                    "channel_id": response["channel"]
                }
            else:
                return {
                    "status": "failed",
                    "error": "Message not sent"
                }

        except SlackApiError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def verify_channel_exists(self, channel: str) -> bool:
        """Verify if channel exists"""
        try:
            response = await self.client.conversations_list()
            channels = response["channels"]
            return any(c["name"] == channel for c in channels)
        except SlackApiError as e:
            logger.error(f"Error checking channel {channel}: {str(e)}")
            return False

    async def test_all_channels(self) -> dict:
        """Test all Nova channels"""
        results = {}

        for channel in self.channels:
            logger.info(f"Testing channel: {channel}")

            # First verify channel exists
            exists = await self.verify_channel_exists(channel)
            if not exists:
                results[channel] = {
                    "status": "error",
                    "error": "Channel does not exist"
                }
                continue

            # Test posting to channel
            results[channel] = await self.test_channel(channel)

            # Add small delay between tests
            await asyncio.sleep(1)

        return results

    def generate_report(self, results: dict) -> str:
        """Generate test report"""
        report = [
            "# Slack Integration Test Report",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MST')}\n"
        ]

        # Add results for each channel
        for channel, result in results.items():
            report.append(f"## #{channel}")
            report.append(f"Purpose: {self.channels[channel]['purpose']}")
            report.append(f"Priority: {self.channels[channel]['priority']}")
            report.append("```yaml")
            if result["status"] == "success":
                report.append("Status: ✅ VERIFIED")
                report.append(f"Message ID: {result['message_id']}")
            else:
                report.append("Status: ❌ FAILED")
                report.append(f"Error: {result.get('error', 'Unknown error')}")
            report.append("```\n")

        # Add summary
        successful = sum(1 for r in results.values() if r["status"] == "success")
        total = len(self.channels)
        report.append("## Summary")
        report.append(f"Successful: {successful}/{total} channels")

        if successful < total:
            report.append("\n### Failed Channels")
            for channel, result in results.items():
                if result["status"] != "success":
                    report.append(f"- #{channel}: {result.get('error', 'Unknown error')}")

        return "\n".join(report)

async def main():
    # Get Slack token from environment
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        logger.error("SLACK_BOT_TOKEN environment variable not set")
        sys.exit(1)

    try:
        # Initialize tester
        tester = SlackTester(token)
        logger.info("Starting Slack integration tests...")

        # Run tests
        results = await tester.test_all_channels()

        # Generate and save report
        report = tester.generate_report(results)
        with open('slack_test_report.md', 'w') as f:
            f.write(report)

        logger.info("Test complete. Results saved to slack_test_report.md")

        # Post summary to launch status channel
        if any(r["status"] == "success" for r in results.values()):
            await tester.client.chat_postMessage(
                channel="#nova-launch-status",
                text=f"Slack Integration Test Complete\n```\n{report}\n```"
            )

        # Exit with appropriate status code
        success = all(r["status"] == "success" for r in results.values())
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
