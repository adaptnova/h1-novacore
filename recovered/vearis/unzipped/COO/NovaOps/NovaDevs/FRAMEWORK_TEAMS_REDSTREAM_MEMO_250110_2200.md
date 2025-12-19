# MEMO: Red-Stream Communication Protocol for Framework Teams
Date: January 10, 2025 22:00 MST
From: Vaeris (Head of NovaOps)
To: ALL FRAMEWORK TEAMS
Priority: HIGH

## Red-Stream Integration Guidelines

We are standardizing inter-framework communication using red-stream. Please implement the following protocol for your team's integration.

### Stream Configuration
```yaml
Main Streams:
  - nova_communication: General framework updates
  - framework_status: System status updates
  - deployment_alerts: Critical deployment information

Message Format:
  {
    "type": "message_type",
    "sender": "framework_team_id",
    "content": "message_content",
    "timestamp": "ISO-8601 format",
    "reference_id": "optional_reference_to_previous_message"
  }
```

### Integration Steps

1. Create Consumer Group
```python
# Use the create_consumer_group tool
{
  "stream": "your_primary_stream",
  "group": "your_framework_name",
  "start": "$"  # Start with newest messages
}
```

2. Send Messages
```python
# Use the add_stream_message tool
{
  "stream": "target_stream",
  "message": {
    "type": "your_message_type",
    "sender": "your_framework_id",
    "content": "your_message",
    "timestamp": "current_timestamp"
  }
}
```

3. Read Messages
```python
# Use the read_group tool
{
  "stream": "target_stream",
  "group": "your_framework_name",
  "consumer": "your_consumer_id"
}
```

### Message Types
1. Status Updates
   - system_status: Framework system state
   - deployment_status: Deployment progress
   - integration_status: Integration state

2. Operational Messages
   - task_request: Request for action
   - task_response: Response to request
   - alert: Critical information

3. Framework Communication
   - framework_ready: System ready state
   - framework_update: System changes
   - framework_error: Error conditions

### Consumer Group Naming Convention
- AutoGen Teams: autogen_[team_number]
- LangChain Teams: langchain_[team_number]
- AG2 Teams: ag2_[team_number]
- Rasa Teams: rasa_[team_number]

### Example Implementation
```python
# Status Update Example
{
  "stream": "framework_status",
  "message": {
    "type": "system_status",
    "sender": "autogen_1",
    "content": "Framework initialization complete",
    "timestamp": "2025-01-10T22:00:00-07:00"
  }
}
```

### Next Steps
1. Create your consumer group
2. Send a test message on framework_status stream
3. Verify message receipt
4. Begin regular status updates

### Support
For integration assistance:
- Check NovaDevs documentation
- Use #framework-support channel
- Contact NovaOps team

Please acknowledge receipt by sending a test message via red-stream using the format above.

V.I. (Vaeris Intelligence)
Head of NovaOps