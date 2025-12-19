# NovaComms GUI - Component Rename Update

FROM: NovaComms GUI Team
TO: All Teams
TIME: 2024-12-15 14:50 MST
PRIORITY: MEDIUM

## Component Rename: Chase Command → Chase Comms

We have renamed the Chase integration components to better reflect their communication-focused nature:

### Updated Components

```yaml
files:
  services:
    - src/services/ChaseCommsService.js # Renamed from ChaseCommandService.js
  components:
    - src/components/layout/ChaseCommsPanel.js # Renamed from ChaseCommandPanel.js
  config:
    - Updated RabbitMQ configuration in src/config/rabbitmq.js
```

### RabbitMQ Changes

```yaml
exchanges:
  old: nova.command
  new: nova.comms

queues:
  old: nova.command.chase
  new: nova.comms.chase

routing_keys:
  old: chase.command
  new: chase.comms
```

### Message Types

```yaml
old_types:
  - chase.command.status
  - chase.command.action
  - chase.command.priority

new_types:
  - chase.comms.status
  - chase.comms.update
  - chase.comms.priority
```

## Required Actions

### RabbitMQ Team

- [ ] Update exchange configuration
- [ ] Migrate queue settings
- [ ] Verify routing keys
- [ ] Confirm message flow

### Backend Team

- [ ] Update message type handling
- [ ] Verify communication patterns
- [ ] Test message routing

### NovaOps Team

- [ ] Update monitoring rules
- [ ] Adjust alert configurations
- [ ] Verify metrics collection

## Integration Testing

The integration test script has been updated to reflect these changes. Testing will verify:

- Message routing through new exchange
- Queue binding functionality
- Message type handling
- Priority levels
- Dead letter handling

## Files to Remove

The following files are deprecated and should be removed after successful testing:

```
src/services/ChaseCommandService.js
src/components/layout/ChaseCommandPanel.js
```

## Timeline

- Component Updates: Complete
- Integration Testing: 15:00-15:30 MST
- File Cleanup: After successful testing
- Launch: 16:15 MST (unchanged)

No changes to the launch schedule or overall functionality. This is purely a naming update for clarity and consistency.

Please acknowledge receipt and update your systems accordingly.

/NovaComms GUI Team
