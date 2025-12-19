# 🛠️ Mini-Agent Memory System - Admin Guide

## **System Administration & Maintenance**

---

## 🔍 **System Overview**

### **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                   Mini-Agent Core                           │
│                  (Python Interface)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              Multi-Database Layer                           │
│                                                         │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  DragonflyDB  │  │ Redis Cluster│  │   PostgreSQL    │ │
│  │   (Primary)   │  │  (Backup)    │  │  (Structured)   │ │
│  │               │  │              │  │                 │ │
│  │ Port 18000    │  │ 18010-18012  │  │  18030-18032    │ │
│  │ Knowledge     │  │ Sessions     │  │ Analytics       │ │
│  └───────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow**

1. **User Interaction** → Mini-Agent Core
2. **Core** → Knowledge Extraction
3. **Extraction** → Multiple Database Storage
4. **Retrieval** → Context Building
5. **Response** → User with Enhanced Context

---

## 🚀 **Installation & Setup**

### **Prerequisites**

```bash
# Check TeamADAPT services
systemctl is-active dragonfly-cluster-node1 dragonfly-cluster-node2 dragonfly-cluster-node3
systemctl is-active redis-cluster-node1 redis-cluster-node2 redis-cluster-node3
systemctl is-active postgresql

# Check ports
nc -z localhost 18000 18001 18002 18010 18011 18012 18030 18031 18032
```

### **Initial Setup**

```bash
# Run initialization script
cd /adaptai/aa-tools/database
chmod +x initialize_memory_system.sh
./initialize_memory_system.sh

# Verify setup
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats
```

### **Configuration Files**

```bash
# Main config
/adaptai/aa-tools/database/mini_agent_core.py
# - Redis/DragonflyDB connections
# - Knowledge extraction settings
# - Session management

# Memory config
/adaptai/aa-tools/database/mini_agent_memory.py
# - Storage namespace
# - Retention policies
# - Backup settings
```

---

## 📊 **Monitoring & Health Checks**

### **Daily Health Checks**

```bash
#!/bin/bash
# Daily memory system health check

echo "=== Mini-Agent Memory System Health Check ==="

# Check DragonflyDB
echo "Checking DragonflyDB..."
redis-cli -p 18000 -a df_cluster_2024_adapt_research ping
redis-cli -p 18001 -a df_cluster_2024_adapt_research ping
redis-cli -p 18002 -a df_cluster_2024_adapt_research ping

# Check Redis Cluster
echo "Checking Redis Cluster..."
redis-cli -p 18010 ping
redis-cli -p 18011 ping
redis-cli -p 18012 ping

# Check PostgreSQL
echo "Checking PostgreSQL..."
psql -h localhost -p 18030 -U postgres -c "SELECT version();"

# Get memory stats
echo "Memory System Statistics:"
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats
```

### **Weekly Reports**

```bash
#!/bin/bash
# Generate weekly memory system report

DATE=$(date +%Y%m%d)
REPORT_FILE="/tmp/memory_system_report_$DATE.txt"

echo "Mini-Agent Memory System - Weekly Report" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE

# System stats
echo -e "\n=== SYSTEM STATISTICS ===" >> $REPORT_FILE
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats >> $REPORT_FILE

# Knowledge breakdown
echo -e "\n=== KNOWLEDGE BREAKDOWN ===" >> $REPORT_FILE
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_knowledge.py --action get_knowledge --type "work_task" >> $REPORT_FILE

# Recent sessions
echo -e "\n=== RECENT SESSIONS ===" >> $REPORT_FILE
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_memory.py --action list >> $REPORT_FILE

echo "Report saved to: $REPORT_FILE"
```

### **Real-time Monitoring**

```bash
# Monitor memory usage
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO memory

# Check active connections
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO clients

# Monitor knowledge growth
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats | grep total_knowledge

# Session activity
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats | grep active_sessions
```

---

## 💾 **Backup & Recovery**

### **Automated Backups**

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backup/mini_agent_memory/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

echo "Starting memory system backup..."

# Backup DragonflyDB (knowledge & preferences)
redis-cli -p 18000 -a df_cluster_2024_adapt_research --rdb $BACKUP_DIR/dragonflydb_primary.rdb
redis-cli -p 18001 -a df_cluster_2024_adapt_research --rdb $BACKUP_DIR/dragonflydb_node2.rdb
redis-cli -p 18002 -a df_cluster_2024_adapt_research --rdb $BACKUP_DIR/dragonflydb_node3.rdb

# Backup Redis Cluster (sessions & chat history)
redis-cli -p 18010 --rdb $BACKUP_DIR/redis_node1.rdb
redis-cli -p 18011 --rdb $BACKUP_DIR/redis_node2.rdb
redis-cli -p 18012 --rdb $BACKUP_DIR/redis_node3.rdb

# Backup PostgreSQL (analytics & metadata)
pg_dump -h localhost -p 18030 -U postgres mini_agent_analytics > $BACKUP_DIR/postgresql_analytics.sql

# Backup configuration
cp /adaptai/aa-tools/database/*.py $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### **Manual Backup Commands**

```bash
# Backup knowledge from DragonflyDB
redis-cli -p 18000 -a df_cluster_2024_adapt_research --rdb /tmp/knowledge_backup.rdb

# Export user preferences
redis-cli -p 18000 -a df_cluster_2024_adapt_research HGETALL mini_agent:user_preferences > /tmp/preferences.json

# Export session data
redis-cli -p 18010 KEYS "mini_agent:sessions:*" > /tmp/sessions.txt

# Export knowledge
redis-cli -p 18000 -a df_cluster_2024_adapt_research KEYS "mini_agent:knowledge:*" > /tmp/knowledge.txt
```

### **Recovery Procedures**

```bash
# Stop services
systemctl stop dragonfly-cluster-node1 dragonfly-cluster-node2 dragonfly-cluster-node3
systemctl stop redis-cluster-node1 redis-cluster-node2 redis-cluster-node3

# Restore from backup
redis-cli -p 18000 -a df_cluster_2024_adapt_research --rdb /path/to/backup/dragonflydb_primary.rdb
redis-cli -p 18010 --rdb /path/to/backup/redis_node1.rdb

# Start services
systemctl start dragonfly-cluster-node1 dragonfly-cluster-node2 dragonfly-cluster-node3
systemctl start redis-cluster-node1 redis-cluster-node2 redis-cluster-node3

# Verify restoration
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats
```

---

## 🔧 **Database Management**

### **DragonflyDB Management**

```bash
# Connect to DragonflyDB
redis-cli -p 18000 -a df_cluster_2024_adapt_research

# Check memory usage
INFO memory

# Check keyspace
INFO keyspace

# List knowledge keys
KEYS mini_agent:knowledge:*

# List user preferences
HGETALL mini_agent:user_preferences

# List active sessions
SMEMBERS mini_agent:active_sessions

# Monitor memory growth
MONITOR
```

### **Redis Cluster Management**

```bash
# Check cluster status
redis-cli -p 18010 CLUSTER NODES

# Check slot distribution
redis-cli -p 18010 CLUSTER SLOTS

# Monitor connections
INFO clients

# Check memory usage
INFO memory
```

### **PostgreSQL Management**

```bash
# Connect to PostgreSQL
psql -h localhost -p 18030 -U postgres

# List databases
\l

# Connect to memory analytics DB
\c mini_agent_analytics

# Check table sizes
SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats;

# Monitor connections
SELECT count(*) FROM pg_stat_activity;
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Memory System Not Responding**

**Symptoms**: Commands timeout or return errors

**Diagnosis**:
```bash
# Check service status
systemctl status dragonfly-cluster-node1
systemctl status redis-cluster-node1

# Check port connectivity
nc -z localhost 18000
nc -z localhost 18010

# Check memory usage
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO memory
```

**Solution**:
```bash
# Restart services
systemctl restart dragonfly-cluster-node1 dragonfly-cluster-node2 dragonfly-cluster-node3
systemctl restart redis-cluster-node1 redis-cluster-node2 redis-cluster-node3

# Check logs
journalctl -u dragonfly-cluster-node1 -n 50
journalctl -u redis-cluster-node1 -n 50
```

#### **2. Knowledge Not Being Stored**

**Symptoms**: Interactions not recorded, knowledge not growing

**Diagnosis**:
```bash
# Test knowledge storage
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action process --user-input "test knowledge" --agent-response "test response"

# Check knowledge count
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats
```

**Solution**:
```bash
# Reinitialize system
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action init

# Check database connectivity
redis-cli -p 18000 -a df_cluster_2024_adapt_research ping
```

#### **3. Session Continuity Broken**

**Symptoms**: Previous sessions not remembered

**Diagnosis**:
```bash
# Check session data
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_memory.py \
    --action list

# Check session storage
redis-cli -p 18010 KEYS "mini_agent:sessions:*"
```

**Solution**:
```bash
# Restore from checkpoint
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action checkpoint --checkpoint-name "recovery_checkpoint"

# Reinitialize session management
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action start --user-name Chase --project-context "recovery_session"
```

### **Log Analysis**

```bash
# DragonflyDB logs
journalctl -u dragonfly-cluster-node1 -f

# Redis logs
journalctl -u redis-cluster-node1 -f

# System resource usage
htop
df -h
free -m
```

### **Performance Optimization**

```bash
# Check memory fragmentation
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO memory | grep mem_fragmentation_ratio

# Check slow queries
redis-cli -p 18000 -a df_cluster_2024_adapt_research SLOWLOG GET 10

# Monitor network
iftop -i eth0

# Check CPU usage
top -p $(pgrep -f mini_agent)
```

---

## 📈 **Performance Tuning**

### **Memory Optimization**

```bash
# Configure DragonflyDB memory
# Edit /etc/systemd/system/dragonfly-cluster-node1.service
# Add: --maxmemory=4gb --maxmemory-policy=allkeys-lru

# Configure Redis memory
# Edit redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### **Connection Pooling**

```python
# Optimize connection settings in mini_agent_core.py
redis.Redis(
    host=host,
    port=port,
    password=password,
    decode_responses=True,
    socket_timeout=5,
    connection_pool_size=20,  # Add for high concurrency
    max_retries=3  # Add for reliability
)
```

### **Index Optimization**

```bash
# Monitor key patterns
redis-cli -p 18000 -a df_cluster_2024_adapt_research --scan --pattern "mini_agent:*" | wc -l

# Check for memory leaks
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO memory | grep used_memory_human
```

---

## 🔒 **Security**

### **Access Control**

```bash
# Verify authentication
redis-cli -p 18000 -a df_cluster_2024_adapt_research AUTH df_cluster_2024_adapt_research

# Check ACL
redis-cli -p 18000 -a df_cluster_2024_adapt_research ACL LIST

# Monitor failed auth attempts
redis-cli -p 18000 -a df_cluster_2024_adapt_research MONITOR | grep AUTH
```

### **Data Encryption**

```bash
# Enable TLS for Redis (if required)
# Edit /etc/redis/redis.conf
tls-port 6380
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem
```

### **Backup Encryption**

```bash
# Encrypt backups
gpg --symmetric --cipher-algo AES256 backup.tar.gz
# Store encrypted backup securely
```

---

## 📋 **Maintenance Schedule**

### **Daily**
- [ ] Check system health
- [ ] Monitor memory usage
- [ ] Verify backup completion

### **Weekly**
- [ ] Generate system report
- [ ] Review performance metrics
- [ ] Clean up old logs
- [ ] Update documentation

### **Monthly**
- [ ] Full system backup
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Capacity planning review

### **Quarterly**
- [ ] Disaster recovery test
- [ ] System architecture review
- [ ] Update dependencies
- [ ] User feedback review

---

## 📞 **Support & Escalation**

### **Internal Support**

**Level 1 (Day-to-day)**
- Check USER_GUIDE.md
- Run health check scripts
- Review logs

**Level 2 (Technical)**
- Database administration
- Performance tuning
- Custom integrations

**Level 3 (Architecture)**
- System design
- Scaling decisions
- Technology upgrades

### **External Resources**

- **DragonflyDB**: https://dragonflydb.io/
- **Redis Documentation**: https://redis.io/documentation
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## 📊 **Key Metrics to Monitor**

### **Performance Metrics**
- Knowledge items stored per day
- Session response time
- Memory usage growth
- Query performance

### **Reliability Metrics**
- Uptime percentage
- Backup success rate
- Recovery time objective (RTO)
- Recovery point objective (RPO)

### **Usage Metrics**
- Active sessions per day
- Knowledge retrieval frequency
- User preference updates
- Checkpoint creation rate

### **Capacity Metrics**
- Storage utilization
- Memory usage trends
- Connection counts
- Network bandwidth

---

## 🎯 **Success Criteria**

### **System Health**
- [ ] 99.9% uptime
- [ ] <100ms response time
- [ ] Zero data loss
- [ ] Successful daily backups

### **User Experience**
- [ ] Seamless session continuity
- [ ] Relevant suggestions
- [ ] Fast knowledge retrieval
- [ ] Intuitive interface

### **Administrative**
- [ ] Automated monitoring
- [ ] Proactive alerting
- [ ] Documented procedures
- [ ] Regular maintenance

---

**Remember**: This memory system is the **brain** of Mini-Agent. Keep it healthy, monitored, and backed up!

**Chase trusts this system with all collaborative work - maintain it with excellence!** 🛠️✨
