# ToolOps RabbitMQ Response Procedures

## Alert Response Procedures

### Queue Issues

#### High Queue Depth (Warning)
1. Check consumer health and logs
2. Verify message processing rate
3. Monitor consumer resource usage
4. Scale consumers if needed
5. Notify #rabbitmq-team if persists

#### Critical Queue Depth
1. Immediately notify #rmq-911
2. Emergency consumer scaling
3. Check for message processing bottlenecks
4. Consider temporary message throttling
5. Prepare incident report

### Resource Issues

#### Memory Usage
1. Warning (>70%):
   - Review memory allocation
   - Check for memory leaks
   - Monitor growth rate
   - Clean up unused resources

2. Critical (>85%):
   - Notify #rmq-911
   - Emergency resource cleanup
   - Consider node restart if safe
   - Implement memory limits

#### Disk Space
1. Warning (<5GB):
   - Clean old message logs
   - Archive unnecessary data
   - Review disk usage patterns
   - Plan capacity increase

2. Critical (<2GB):
   - Emergency notification to #rmq-911
   - Immediate log rotation
   - Emergency cleanup
   - Prepare for possible node evacuation

### Connection Issues

#### High Connection Count
1. Warning (>80%):
   - Review connection patterns
   - Check for connection leaks
   - Monitor client behavior
   - Plan capacity increase

2. Critical (>90%):
   - Emergency notification
   - Force close idle connections
   - Review client configurations
   - Implement connection limits

## Escalation Procedures

### Warning Alerts
1. Primary Response:
   - Team investigates within 15 minutes
   - Update #rabbitmq-team
   - Document findings
   - Implement fixes

2. Escalation (after 2 hours):
   - Escalate to #rmq-911
   - Prepare incident report
   - Review response timeline
   - Update procedures if needed

### Critical Alerts
1. Immediate Response (15 min SLA):
   - Notify #rmq-911
   - Begin incident response
   - Update status every 15 minutes
   - Document all actions

2. Escalation (after 30 minutes):
   - Escalate to team leads
   - Initiate emergency procedures
   - Consider system rollback
   - Prepare recovery plan

## Recovery Procedures

### System Recovery
1. Verify system state
2. Review error logs
3. Check data integrity
4. Test basic operations
5. Monitor recovery

### Post-Incident
1. Generate incident report
2. Review response timeline
3. Update procedures
4. Schedule preventive measures
5. Document lessons learned

## Communication Channels

### Primary Channels
- Warning: #rabbitmq-team
- Critical: #rmq-911
- Emergency: On-call phone

### Status Updates
1. Initial notification
2. Progress updates
3. Resolution confirmation
4. Post-incident report

## Monitoring Tools

### Prometheus
- Dashboard: http://10.10.0.19:15692
- Metrics endpoint: /metrics
- Health check: /health

### Grafana
- RabbitMQ Overview
- Queue Metrics
- Resource Usage
- Alert History

## Documentation Requirements

### Incident Documentation
1. Initial alert details
2. Response timeline
3. Actions taken
4. Resolution steps
5. Follow-up tasks

### Regular Reports
1. Weekly metrics review
2. Monthly trend analysis
3. Quarterly capacity planning
4. Annual procedure review