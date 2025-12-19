#!/usr/bin/env python3

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def test_slack_connection():
    # Get token from environment
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("Error: SLACK_BOT_TOKEN not found in environment")
        return False

    # Initialize client
    client = WebClient(token=token)

    try:
        # Test API call
        response = client.chat_postMessage(
            channel="#nova-launch-status",
            text="🔄 Quick Slack connection test from Nova Integration Team"
        )
        print("Success! Message sent to #nova-launch-status")
        print(f"Message timestamp: {response['ts']}")
        return True

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        return False

if __name__ == "__main__":
    print("Testing Slack connection...")
    success = test_slack_connection()
    print(f"\nTest {'succeeded' if success else 'failed'}")
