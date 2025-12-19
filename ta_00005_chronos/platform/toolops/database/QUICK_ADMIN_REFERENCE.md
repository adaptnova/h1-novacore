# 🧠 MINIMAL ADMIN GUIDE - Quick Reference

## **System Status: ✅ OPERATIONAL**

**Multi-Database Memory System Status:**
- 🟢 **DragonflyDB Cluster**: 18000-18002 (Primary Memory) ✅
- 🟢 **Redis Cluster**: 18010-18012 (Session Data) ✅  
- 🟡 **PostgreSQL**: 18030-18032 (Structured Analytics) ⚠️ (Minor issues)
- 🔴 **MongoDB**: 27017 (Not available)
- 🟢 **ClickHouse**: 18090 (Analytics) ✅

---

## 📋 **Daily Commands (Copy & Paste)**

### **Start Work Session**
```bash
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/integrated_memory_system.py --action start
```

### **Process Interaction**
```bash
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/integrated_memory_system.py \
    --action process --user-input "Your message" --agent-response "Mini-Agent response"
```

### **Get Intelligent Response**
```bash
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/integrated_memory_system.py \
    --action response --user-input "Your question"
```

### **Check System Health**
```bash
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/multi_database_memory.py --action health
```

### **Get Analytics**
```bash
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/integrated_memory_system.py --action analytics
```

---

## 🚨 **Quick Troubleshooting**

### **Memory System Not Working**
```bash
# Check if databases are running
systemctl is-active dragonfly-cluster-node1
systemctl is-active redis-cluster-node1
systemctl is-active postgresql

# Restart if needed
systemctl restart dragonfly-cluster-node1 dragonfly-cluster-node2 dragonfly-cluster-node3
systemctl restart redis-cluster-node1 redis-cluster-node2 redis-cluster-node3
```

### **Knowledge Not Being Stored**
```bash
# Test direct DragonflyDB connection
redis-cli -p 18000 -a df_cluster_2024_adapt_research ping

# Reinitialize system
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action init
```

### **Session Continuity Broken**
```bash
# Start new session (loads previous context automatically)
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/integrated_memory_system.py --action start
```

---

## 📊 **Monitoring**

### **Database Health**
```bash
# DragonflyDB
redis-cli -p 18000 -a df_cluster_2024_adapt_research INFO memory

# Redis Cluster
redis-cli -p 18010 INFO clients

# PostgreSQL
psql -h localhost -p 18030 -U postgres -c "SELECT count(*) FROM knowledge;"

# ClickHouse
curl -s http://localhost:18090/ping
```

### **Memory Usage**
```bash
# Check knowledge count
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action stats

# Check database connections
PYTHONPATH=/adaptai/aa-tools/database /usr/bin/python3 /adaptai/aa-tools/database/multi_database_memory.py --action health
```

---

## 🔧 **Common Issues & Solutions**

| Issue | Symptom | Solution |
|-------|---------|----------|
| **DragonflyDB down** | Commands timeout | `systemctl restart dragonfly-cluster-node1` |
| **Redis cluster issues** | Hash slot errors | `systemctl restart redis-cluster-node1 redis-cluster-node2 redis-cluster-node3` |
| **Knowledge not stored** | Memory stats don't increase | Restart memory system: `mini_agent_core.py --action init` |
| **Session continuity broken** | Previous work not remembered | Start new session (auto-loads context) |
| **Slow responses** | Database performance | Check memory usage: `redis-cli -p 18000 INFO memory` |

---

## 📁 **Key Files**

| File | Purpose | Location |
|------|---------|----------|
| **integrated_memory_system.py** | Main interface | `/adaptai/aa-tools/database/` |
| **multi_database_memory.py** | Multi-DB operations | `/adaptai/aa-tools/database/` |
| **mini_agent_core.py** | Core memory system | `/adaptai/aa-tools/database/` |
| **USER_GUIDE.md** | User documentation | `/adaptai/aa-tools/database/` |
| **ADMIN_GUIDE.md** | Full admin guide | `/adaptai/aa-tools/database/` |

---

## 🎯 **Performance Targets**

- **Response Time**: <100ms for knowledge retrieval
- **Uptime**: 99.9% availability
- **Knowledge Growth**: 10+ items per session
- **Database Health**: All primary databases operational

---

## 📞 **Escalation**

**Level 1**: Restart databases, check USER_GUIDE.md  
**Level 2**: Review logs, check ADMIN_GUIDE.md  
**Level 3**: System architecture review  

---

**System is production-ready and monitoring Chase's infinite collaborative work!** 🚀
