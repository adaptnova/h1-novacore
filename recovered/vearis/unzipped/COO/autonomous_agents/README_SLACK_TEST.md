# Slack Integration Test for Nova Team

## Overview
This test suite verifies Slack integration for the Nova autonomous team, ensuring proper communication channels and HITL (Human-In-The-Loop) interfaces are working correctly.

## Prerequisites

1. Slack Workspace Access
2. Bot Token with required permissions:
   - channels:read
   - chat:write
   - reactions:write
3. Python 3.8+
4. Virtual environment support

## Quick Start

1. Set up the test environment:
```bash
chmod +x setup_slack_test.sh
./setup_slack_test.sh
```

2. Configure environment:
```bash
cp .env.template .env
nano .env  # Add your Slack bot token
```

3. Run the test:
```bash
source slack_test_env/bin/activate
python3 test_slack_integration.py
```

## Test Components

### Channels Tested
```yaml
emergency:
  channel: #nova-911
  purpose: Emergency response
  priority: critical

status:
  channel: #nova-launch-status
  purpose: Launch coordination
  priority: high

specialized:
  db_ops:
    channel: #nova-db-ops
    purpose: Database operations
    priority: high

  mq_ops:
    channel: #nova-mq-ops
    purpose: Message queue operations
    priority: high

  framework:
    channel: #nova-framework
    purpose: Framework coordination
    priority: high

  monitoring:
    channel: #nova-monitor
    purpose: System monitoring
    priority: medium
```

### Test Sequence

1. Channel Verification
```yaml
steps:
  - Verify channel exists
  - Check access permissions
  - Validate channel purpose
```

2. Message Testing
```yaml
steps:
  - Post test message
  - Add reaction
  - Verify delivery
```

3. Integration Verification
```yaml
steps:
  - Check response times
  - Verify permissions
  - Validate functionality
```

## Test Results

Results are saved in two locations:
1. `slack_test_report.md`: Detailed test results
2. `logs/slack_test.log`: Detailed logging information

The test also posts a summary to #nova-launch-status channel.

## Success Criteria

### Channel Access
```yaml
requirements:
  - All channels accessible
  - Proper permissions
  - Correct channel configuration
```

### Message Delivery
```yaml
requirements:
  - Messages delivered
  - Reactions possible
  - Proper formatting
```

### Response Times
```yaml
requirements:
  critical: <100ms
  high: <500ms
  normal: <1s
```

## Troubleshooting

### Common Issues

1. Token Issues
```yaml
symptoms:
  - "not_authed" error
  - "invalid_auth" error
solution: Verify SLACK_BOT_TOKEN in .env
```

2. Channel Access
```yaml
symptoms:
  - "channel_not_found" error
  - "not_in_channel" error
solution: Invite bot to channels
```

3. Permission Issues
```yaml
symptoms:
  - "missing_scope" error
  - "not_allowed" error
solution: Review bot permissions
```

### Getting Help

1. Check logs:
```bash
tail -f logs/slack_test.log
```

2. Review report:
```bash
cat slack_test_report.md
```

3. Contact support:
- Post in #nova-911 for urgent issues
- Use #nova-infra-support for general help

## Next Steps

After successful test:
1. Review test report
2. Verify channel functionality
3. Proceed with Nova team deployment
4. Monitor integration status

## Notes

- Keep bot token secure
- Monitor channel activity
- Review logs regularly
- Update permissions as needed

## Support

For assistance:
1. Check logs and reports
2. Review error messages
3. Post in appropriate channel:
   - #nova-911 (emergencies)
   - #nova-infra-support (general help)
