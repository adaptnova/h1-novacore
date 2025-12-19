# NOVA COMMS GUI Deployment Guide

## High-Memory Instance Deployment (c3-highmem-176)

### Prerequisites
- System with 1,408GB memory
- Node.js 18+
- RabbitMQ Server
- Systemd

### Quick Deploy
```bash
# 1. Install service and configure memory
sudo ./scripts/install_service.sh

# 2. Verify memory allocation
sudo ./scripts/verify_memory.sh

# 3. Verify service status
sudo ./scripts/verify_service.sh
```

### Manual Steps (if needed)

1. Create nova user and group:
```bash
sudo useradd -r -s /bin/false nova
sudo groupadd nova
```

2. Create required directories:
```bash
sudo mkdir -p /etc/nova
sudo mkdir -p /data/ax/projects/active/nova_comms_gui/logs
sudo mkdir -p /data/ax/projects/active/nova_comms_gui/data
```

3. Set permissions:
```bash
sudo chown -R nova:nova /data/ax/projects/active/nova_comms_gui
sudo chmod 755 /data/ax/projects/active/nova_comms_gui
```

4. Install systemd service:
```bash
sudo cp nova-comms-gui.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/nova-comms-gui.service
sudo systemctl daemon-reload
```

5. Start and enable service:
```bash
sudo systemctl enable nova-comms-gui
sudo systemctl start nova-comms-gui
```

### Memory Configuration

```yaml
Memory Allocation:
  node_heap: 32GB
  rabbitmq: 64GB
  system_reserved: 16GB
  total: 112GB

Systemd Limits:
  MemoryHigh: 32GB
  MemoryMax: 64GB
```

### Verification

Check service status:
```bash
systemctl status nova-comms-gui
```

View logs:
```bash
journalctl -u nova-comms-gui -f
```

Monitor memory:
```bash
sudo ./scripts/verify_memory.sh
```

### Troubleshooting

1. If service fails to start:
```bash
journalctl -u nova-comms-gui -n 100 --no-pager
```

2. If memory verification fails:
```bash
# Check system memory
free -h

# Check Node.js memory
node -e "console.log(require('v8').getHeapStatistics())"

# Check RabbitMQ memory
rabbitmqctl status
```

3. If process needs restart:
```bash
sudo systemctl restart nova-comms-gui
```

### Important Notes

1. Memory Configuration:
   - Service is configured for high-memory instance
   - Memory limits are enforced through systemd
   - Auto-restart enabled for memory threshold breaches

2. Data Persistence:
   - Logs stored in `/data/ax/projects/active/nova_comms_gui/logs`
   - Data stored in `/data/ax/projects/active/nova_comms_gui/data`
   - RabbitMQ queues are durable

3. Security:
   - Service runs as nova user
   - Systemd hardening enabled
   - File permissions set to minimum required

### Contact

- Issues: #nova-comms-urgent
- Escalation: #infracore-urgent
- Emergency: CCA Direct Line

---
Last Updated: 2024-12-06 02:50 MST
