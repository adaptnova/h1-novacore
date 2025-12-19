# NOVA Agent Launch Guide

## Quick Start

```bash
# 1. Verify system
python scripts/verify_system.py

# 2. Launch NOVA system
python scripts/start_nova.py
```

## Prerequisites

### System Requirements
- CPU: c3-highcpu-88 (88 vCPUs)
- Memory: 128GB minimum
- Python: 3.11
- Disk Space: 100GB minimum in /data/ax/ax_novas

### Environment Variables
```bash
# Required environment variables in .env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
NOVA_ENVIRONMENT=development
NOVA_LOG_LEVEL=DEBUG
```

## Launch Process

### 1. System Verification
The system verification script checks:
- CPU resources
- Memory availability
- Python version
- Required directories
- Environment variables
- Python packages
- Process priorities

### 2. Agent Launch
The launch process follows this sequence:
1. Orchestrator NOVA (gpt-4)
2. Core Agents:
   - Architect NOVA (gpt-4)
   - Developer NOVA (claude-3-opus)
   - Research NOVA (gpt-4)
3. Support Agents:
   - Integration NOVA (claude-3-opus)
   - QA NOVA (gpt-4)
   - Security NOVA (claude-3-opus)
   - Data NOVA (gpt-4)
   - Infrastructure NOVA (claude-3-opus)
   - UI/UX NOVA (gpt-4)
   - Performance NOVA (claude-3-opus)

## Resource Allocation

### CPU Priority
- Orchestrator: 95
- Core Agents: 90
- Support Agents: 70-85

### Memory Allocation
- Orchestrator: 20GB
- Core Agents: 16GB
- Support Agents: 8-12GB

## Monitoring

### Check Agent Status
```bash
# List all agents
python -m nova.cli agents

# Monitor system
python -m nova.cli monitor
```

### Health Checks
```bash
# Check system health
python -m nova.cli status
```

## Troubleshooting

### Common Issues

1. **Insufficient Resources**
   ```bash
   # Check system resources
   python scripts/verify_system.py
   ```

2. **Environment Issues**
   ```bash
   # Verify environment
   python scripts/verify_system.py --env-only
   ```

3. **Agent Launch Failures**
   ```bash
   # Check agent logs
   tail -f /data/ax/ax_novas/data/logs/agent_*.log
   ```

### Recovery Steps

1. **Agent Failure**
   ```bash
   # Restart specific agent
   python -m nova.cli restart --agent-id=<id>
   ```

2. **System Recovery**
   ```bash
   # Full system restart
   python scripts/start_nova.py --recover
   ```

## Directory Structure

```
/data/ax/ax_novas/
├── data/
│   ├── logs/         # Agent logs
│   ├── memory/       # Memory store
│   ├── cache/        # System cache
│   ├── models/       # Model data
│   ├── metrics/      # System metrics
│   └── backups/      # Data backups
```

## Launch Verification

### Success Criteria
1. All 11 agents running
2. System health status: HEALTHY
3. Agent communication established
4. Memory system operational
5. Monitoring active

### Verification Commands
```bash
# Check running agents
python -m nova.cli agents

# Verify health
python -m nova.cli status

# Check metrics
python -m nova.cli metrics
```

## Post-Launch Steps

1. **Monitor Resource Usage**
   ```bash
   # Watch system metrics
   python -m nova.cli monitor --resource-usage
   ```

2. **Verify Agent Communication**
   ```bash
   # Test agent collaboration
   python -m nova.cli test-collaboration
   ```

3. **Check Memory System**
   ```bash
   # Verify memory operations
   python -m nova.cli test-memory
   ```

## Maintenance

### Regular Checks
1. Monitor resource usage
2. Check agent health
3. Review system logs
4. Verify memory usage

### Backup
```bash
# Create system backup
python scripts/backup.py

# Restore from backup
python scripts/restore.py --backup-dir=<path>
```

## Support

### Logs Location
- Agent Logs: `/data/ax/ax_novas/data/logs/agent_*.log`
- System Logs: `/data/ax/ax_novas/data/logs/system.log`
- Error Logs: `/data/ax/ax_novas/data/logs/error.log`

### Monitoring
- Metrics: `/data/ax/ax_novas/data/metrics/`
- Health Checks: Real-time via CLI
- Resource Usage: System monitoring

### Contact
For issues or questions:
1. Check logs first
2. Review error messages
3. Consult documentation
4. Contact system administrator
