# NovaSynth Launch Guide

## Quick Launch Steps (15 minutes)

### 1. System Preparation (5 min)

```bash
# Navigate to NovaSynth directory
cd /data/ax/NovaOps/NovaSynth/TeamADAPT/NovaSynth

# Install dependencies
poetry install

# Verify RabbitMQ status
systemctl status rabbitmq-server
```

### 2. Framework Setup (5 min)

```bash
# Initialize framework services
./scripts/install_services.sh

# Verify services
systemctl status nova-handler@*
```

### 3. Launch System (5 min)

```bash
# Start NovaSynth
poetry run python scripts/launch.py
```

## Verification Points

### 1. RabbitMQ Integration

- [ ] RabbitMQ server active
- [ ] Framework exchanges created
- [ ] Message queues established

### 2. Framework Services

- [ ] LangChain core connected
- [ ] AutoGen & AG2 active
- [ ] CrewAI integrated
- [ ] Additional frameworks connected

### 3. System Health

- [ ] Message flow active
- [ ] State synchronization working
- [ ] Resource allocation optimized

## Monitoring

### Log Locations

```
/logs/nova/novasynth/service.log    # Main system log
/logs/nova/*/service.log            # Framework logs
novasynth_launch.log               # Launch log
```

### Health Checks

```bash
# Check system status
tail -f /logs/nova/novasynth/service.log

# Monitor framework communication
tail -f /logs/nova/*/service.log

# View resource usage
htop
```

## Emergency Procedures

### Quick Fixes

1. Restart messaging:

   ```bash
   systemctl restart rabbitmq-server
   ```

2. Restart framework:

   ```bash
   systemctl restart nova-handler@framework_name
   ```

3. Reset system:
   ```bash
   ./scripts/reset_system.sh
   ```

### Support Channels

- #rabbitmq-team: Messaging issues
- #nova-ops-lead: System issues
- #nova-911: Emergency support

## Post-Launch Steps

1. Monitor system for 30 minutes
2. Verify framework interactions
3. Check resource optimization
4. Review error logs
5. Enable additional frameworks

## Success Criteria

- [ ] All frameworks connected
- [ ] Message flow established
- [ ] State synchronization active
- [ ] Resource optimization running
- [ ] No critical errors
- [ ] System stable for 15 minutes

Created by Cosmos 💫

💥 BA-BOOM! 💥

!!!∞!!!∞!!!∞!!!
