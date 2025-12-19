# RabbitMQ Emergency Response Card

## CRITICAL ALERT

- Status: OFFLINE
- Priority: HIGH
- Impact: Nova ecosystem affected
- Action: IMMEDIATE RESPONSE REQUIRED

## Quick Response Commands

### 1. Status Check

```bash
# Service status
systemctl status rabbitmq-server

# Port check
netstat -tulpn | grep -E '5672|15672'

# Process check
ps aux | grep rabbitmq
```

### 2. Quick Recovery

```bash
# Restart service
systemctl restart rabbitmq-server

# Verify startup
systemctl status rabbitmq-server
rabbitmqctl status
```

### 3. Health Check

```bash
# Node health
rabbitmqctl node_health_check

# List queues
rabbitmqctl list_queues

# Check connections
rabbitmqctl list_connections
```

## Critical Paths

1. Service Path: /etc/rabbitmq
2. Logs: /var/log/rabbitmq
3. Data: /var/lib/rabbitmq

## Contact Points

- Team Lead: Cline
- System Location: [SYSTEM_HOSTNAME]
- Priority Channel: Team chat

## Success Criteria

- [ ] Service running
- [ ] Ports responding (5672, 15672)
- [ ] Queues accessible
- [ ] Nova connected
- [ ] Messages flowing

## Escalation Path

1. Attempt quick recovery
2. Check logs for errors
3. Verify system resources
4. Contact team lead if unresolved

Keep this card readily available.
Follow recovery steps in order.
Document all actions taken.
Report status changes immediately.
