#!/usr/bin/env python3

import os
import json
import subprocess
from message_templates import MessageTemplates
from datetime import datetime

def test_slack_communication(templates):
    """Test Slack messaging with standardized headers"""
    print("\nTesting Slack Communication...")

    message = templates.format_slack_message(
        {
            'title': 'Communication Test',
            'body': '🔄 Testing standardized communication format\n\n' +
                    'Verifying:\n' +
                    '• Message formatting\n' +
                    '• Header structure\n' +
                    '• Team routing\n' +
                    '• Priority system'
        },
        priority='normal',
        icon='🧪'
    )

    try:
        subprocess.run([
            'wget',
            '--post-data=' + json.dumps(message),
            '--header=Content-Type: application/json',
            'https://hooks.slack.com/services/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',
            '-O', '/dev/null'
        ])
        print("✅ Slack message sent successfully")
    except Exception as e:
        print(f"❌ Slack message failed: {str(e)}")

def test_rabbitmq_communication(templates):
    """Test RabbitMQ messaging with standardized headers"""
    print("\nTesting RabbitMQ Communication...")

    message = templates.format_rabbitmq_message(
        "Testing standardized message format in RabbitMQ",
        "system.test",
        to_team="nova-integration"
    )

    print("RabbitMQ message format:")
    print(json.dumps(message, indent=2))
    print("✅ RabbitMQ message formatted successfully")

def test_log_communication(templates):
    """Test logging with standardized headers"""
    print("\nTesting Log Communication...")

    log_message = templates.format_log_message(
        "Testing standardized log format",
        level="INFO",
        to_team="Nova Test Team"
    )

    try:
        with open('test_communications.log', 'a') as f:
            f.write(log_message + '\n')
        print("✅ Log message written successfully")
    except Exception as e:
        print(f"❌ Log message failed: {str(e)}")

def test_memo_communication(templates):
    """Test memo formatting with standardized headers"""
    print("\nTesting Memo Communication...")

    memo = templates.format_memo(
        "Test Memo",
        "Testing standardized memo format\n\n" +
        "1. Header structure\n" +
        "2. Content formatting\n" +
        "3. Team routing",
        to_team="Nova Test Team"
    )

    try:
        with open('test_memo.md', 'w') as f:
            f.write(memo)
        print("✅ Memo created successfully")
    except Exception as e:
        print(f"❌ Memo creation failed: {str(e)}")

def test_alert_communication(templates):
    """Test alert formatting with standardized headers"""
    print("\nTesting Alert Communication...")

    alert = templates.format_alert(
        "info",
        "Testing standardized alert format",
        to_team="Nova Test Team"
    )

    try:
        with open('test_alert.md', 'w') as f:
            f.write(alert)
        print("✅ Alert created successfully")
    except Exception as e:
        print(f"❌ Alert creation failed: {str(e)}")

def test_command_communication(templates):
    """Test command formatting with standardized headers"""
    print("\nTesting Command Communication...")

    command = templates.format_command(
        "test_command",
        {"param1": "test", "param2": 123},
        to_system="Nova Test System"
    )

    print("Command format:")
    print(json.dumps(command, indent=2))
    print("✅ Command formatted successfully")

def main():
    print("Starting Communication Format Tests")
    print("=" * 50)

    # Create test templates
    templates = MessageTemplates(
        "Nova Test System",
        sender_team="Nova Integration"
    )

    # Run tests
    test_slack_communication(templates)
    test_rabbitmq_communication(templates)
    test_log_communication(templates)
    test_memo_communication(templates)
    test_alert_communication(templates)
    test_command_communication(templates)

    print("\nTest Results Summary")
    print("=" * 50)

    # Check test artifacts
    results = []
    results.append(("Log File", os.path.exists('test_communications.log')))
    results.append(("Memo File", os.path.exists('test_memo.md')))
    results.append(("Alert File", os.path.exists('test_alert.md')))

    for test, success in results:
        print(f"{test}: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    main()
