# RabbitMQ Recovery Procedures

## CRITICAL ALERT STATUS

Date: 2024-03-15
Priority: HIGH
Service Status: OFFLINE

## Immediate Recovery Steps

### 1. Service Verification

```bash
# Check service status
systemctl status rabbitmq-server

# Check process
ps aux | grep rabbitmq

# Check ports
netstat -tulpn | grep -E '5672|15672'
```

### 2. System Resources

```bash
# Check memory
free -h

# Check disk space
df -h /var/lib/rabbitmq

# Check system load
uptime
```

### 3. Service Restart

```bash
# Stop service
systemctl stop rabbitmq-server

# Wait for cleanup
sleep 10

# Start service
systemctl start rabbitmq-server

# Check status
systemctl status rabbitmq-server
```

### 4. Network Verification

```bash
# Check local ports
ss -tulpn | grep -E '5672|15672'

# Test connectivity
telnet localhost 5672
telnet localhost 15672

# Check DNS
nslookup [SYSTEM_HOSTNAME]
```

## Post-Recovery Verification

### 1. Exchange Configuration

```bash
# List exchanges
rabbitmqctl list_exchanges

# Verify bindings
rabbitmqctl list_bindings
```

### 2. Queue Status

```bash
# List queues
rabbitmqctl list_queues

# Check consumers
rabbitmqctl list_consumers
```

### 3. Nova Integration

```bash
# Check connections
rabbitmqctl list_connections

# Verify channels
rabbitmqctl list_channels

# Test message flow
rabbitmqctl list_queues name messages_ready messages_unacknowledged
```

## Monitoring Steps

### 1. Log Analysis

```bash
# Check system logs
tail -f /var/log/rabbitmq/rabbit@[SYSTEM_HOSTNAME].log

# Check error logs
tail -f /var/log/rabbitmq/rabbit@[SYSTEM_HOSTNAME]-sasl.log
```

### 2. Performance Metrics

```bash
# Check memory usage
rabbitmqctl status | grep memory

# Check file descriptors
rabbitmqctl status | grep file_descriptors

# Check process limits
rabbitmqctl status | grep limit
```

### 3. Cluster Health

```bash
# Check cluster status
rabbitmqctl cluster_status

# Check node health
rabbitmqctl node_health_check
```

## Recovery Validation

### Required Checks

- [ ] Service running
- [ ] Ports responding
- [ ] Exchanges configured
- [ ] Queues accessible
- [ ] Bindings correct
- [ ] Messages flowing
- [ ] Nova connected
- [ ] Logs clean

### Integration Points

- [ ] Database connections
- [ ] API endpoints
- [ ] Client applications
- [ ] Monitoring systems

## Contact Points

### Primary

- RabbitMQ Team Lead: Cline
- System Location: [SYSTEM_HOSTNAME]

### Paths

- Service: /etc/rabbitmq
- Logs: /var/log/rabbitmq
- Data: /var/lib/rabbitmq

## Documentation Updates

### Required Updates

- [ ] Status memos
- [ ] Configuration docs
- [ ] Monitoring alerts
- [ ] Team notifications

### Post-Recovery Report

- Root cause analysis
- Recovery timeline
- Impact assessment
- Prevention measures

## Prevention Measures

### Monitoring

1. Set up enhanced monitoring
2. Configure additional alerts
3. Review thresholds
4. Update check frequency

### Automation

1. Create auto-recovery scripts
2. Implement health checks
3. Set up failover
4. Configure backups

Keep this document handy during recovery operations.
Follow steps in order.
Document all actions taken.
Update procedures based on findings.
