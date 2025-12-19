#!/usr/bin/env python3
"""
Mini-Agent Memory System Installer
Installs persistent memory capabilities for any Mini-Agent
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class MiniAgentMemoryInstaller:
    def __init__(self):
        self.installation_dir = Path("/adaptai/aa-tools/database")
        self.target_dir = Path.home() / ".mini_agent" / "memory"
        self.config_file = self.target_dir / "memory_config.json"
        
    def install_mini_agent_memory(self, database_config=None):
        """Install Mini-Agent memory system"""
        
        print("🚀 Mini-Agent Memory System Installer")
        print("=" * 50)
        
        # Create installation directory
        print("\n1. Creating installation directory...")
        self.target_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {self.target_dir}")
        
        # Copy memory system files
        print("\n2. Installing memory system files...")
        files_to_install = [
            "mini_agent_memory.py",
            "mini_agent_knowledge.py", 
            "mini_agent_session_manager.py",
            "mini_agent_core.py",
            "multi_database_memory.py",
            "integrated_memory_system.py",
            "session_persistence_demo.py"
        ]
        
        for file_name in files_to_install:
            source = self.installation_dir / file_name
            target = self.target_dir / file_name
            
            if source.exists():
                target.write_text(source.read_text())
                print(f"   ✅ Installed: {file_name}")
            else:
                print(f"   ⚠️  Missing: {file_name}")
        
        # Create configuration
        print("\n3. Creating configuration...")
        self.create_configuration(database_config)
        
        # Create launcher scripts
        print("\n4. Creating launcher scripts...")
        self.create_launcher_scripts()
        
        # Create setup script
        print("\n5. Creating setup automation...")
        self.create_setup_script()
        
        # Create integration guide
        print("\n6. Creating integration guide...")
        self.create_integration_guide()
        
        print("\n✅ INSTALLATION COMPLETE!")
        print(f"   Memory system installed to: {self.target_dir}")
        print(f"   Configuration: {self.config_file}")
        
        return True
    
    def create_configuration(self, database_config=None):
        """Create memory system configuration"""
        
        # Default database configuration
        default_config = {
            "memory_system": {
                "enabled": True,
                "namespace": "mini_agent",
                "auto_backup": True,
                "backup_interval_hours": 24
            },
            "databases": {
                "dragonfly": {
                    "enabled": True,
                    "hosts": ["localhost:18000"],
                    "password": "df_cluster_2024_adapt_research",
                    "primary": True,
                    "use_cases": ["fast_access", "primary_storage", "user_preferences"]
                },
                "redis": {
                    "enabled": True,
                    "hosts": ["localhost:18010"],
                    "password": None,
                    "use_cases": ["session_data", "chat_history", "backup_storage"]
                },
                "postgresql": {
                    "enabled": True,
                    "hosts": ["localhost:18030"],
                    "database": "mini_agent_memory",
                    "user": "postgres",
                    "password": "changeme",
                    "use_cases": ["structured_data", "analytics", "query_optimization"]
                },
                "clickhouse": {
                    "enabled": True,
                    "hosts": ["localhost:18090"],
                    "use_cases": ["pattern_analysis", "performance_metrics", "trend_detection"]
                },
                "mongodb": {
                    "enabled": False,
                    "hosts": ["localhost:27017"],
                    "use_cases": ["document_storage", "flexible_schema"]
                }
            },
            "agent_info": {
                "name": "Mini-Agent",
                "version": "1.0",
                "capabilities": ["persistent_memory", "knowledge_extraction", "session_continuity"],
                "created_by": "Chase's Memory System"
            }
        }
        
        # Allow custom database configuration
        if database_config:
            default_config["databases"].update(database_config)
        
        self.config_file.write_text(json.dumps(default_config, indent=2))
        print(f"   ✅ Configuration created: {self.config_file}")
    
    def create_launcher_scripts(self):
        """Create launcher scripts for easy use"""
        
        # Main memory launcher
        launcher_content = f"""#!/bin/bash
# Mini-Agent Memory System Launcher

MINI_AGENT_MEMORY_DIR="{self.target_dir}"
PYTHONPATH="$MINI_AGENT_MEMORY_DIR:$PYTHONPATH"

# Check if configuration exists
if [ ! -f "{self.config_file}" ]; then
    echo "❌ Mini-Agent memory not configured. Run setup first."
    exit 1
fi

# Parse command line arguments
ACTION="$1"
case "$ACTION" in
    "start")
        echo "🚀 Starting Mini-Agent memory session..."
        python3 "$MINI_AGENT_MEMORY_DIR/integrated_memory_system.py" --action start "$@"
        ;;
    "process")
        echo "🧠 Processing with memory enhancement..."
        python3 "$MINI_AGENT_MEMORY_DIR/integrated_memory_system.py" --action process "$@"
        ;;
    "response")
        echo "💡 Getting intelligent response..."
        python3 "$MINI_AGENT_MEMORY_DIR/integrated_memory_system.py" --action response "$@"
        ;;
    "analytics")
        echo "📊 Getting memory analytics..."
        python3 "$MINI_AGENT_MEMORY_DIR/integrated_memory_system.py" --action analytics "$@"
        ;;
    "health")
        echo "🔍 Checking memory system health..."
        python3 "$MINI_AGENT_MEMORY_DIR/multi_database_memory.py" --action health "$@"
        ;;
    "demo")
        echo "🎯 Running memory persistence demo..."
        python3 "$MINI_AGENT_MEMORY_DIR/session_persistence_demo.py"
        ;;
    "install-deps")
        echo "📦 Installing dependencies..."
        pip install redis psycopg2-binary pymongo requests nats-py
        ;;
    "help"|"--help"|"-h")
        echo "Mini-Agent Memory System Launcher"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start       - Start memory session"
        echo "  process     - Process interaction with memory"
        echo "  response    - Get intelligent response"
        echo "  analytics   - Get memory analytics"
        echo "  health      - Check system health"
        echo "  demo        - Run persistence demo"
        echo "  install-deps - Install dependencies"
        echo "  help        - Show this help"
        ;;
    *)
        echo "❌ Unknown command: $ACTION"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
"""
        
        launcher_file = self.target_dir / "mini_agent_memory"
        launcher_file.write_text(launcher_content)
        launcher_file.chmod(0o755)
        
        # Create symbolic link in user's bin
        bin_dir = Path.home() / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        link_path = bin_dir / "mini_agent_memory"
        if link_path.exists():
            link_path.unlink()
        link_path.symlink_to(launcher_file)
        
        print(f"   ✅ Launcher created: {launcher_file}")
        print(f"   ✅ Available as: mini_agent_memory (in PATH)")
    
    def create_setup_script(self):
        """Create automated setup script"""
        
        setup_content = f"""#!/bin/bash
# Mini-Agent Memory System Setup
# Automatically configures memory system for a Mini-Agent

set -e

echo "🚀 Mini-Agent Memory System Setup"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install redis psycopg2-binary pymongo requests nats-py

echo "🧪 Testing database connectivity..."

# Test databases (optional - memory system works with available databases)
echo "   Testing Redis..."
python3 -c "import redis; r=redis.Redis(host='localhost', port=6379); r.ping()" 2>/dev/null && echo "   ✅ Redis available" || echo "   ⚠️  Redis not available"

echo "   Testing PostgreSQL..."
python3 -c "import psycopg2; psycopg2.connect('host=localhost port=5432 user=postgres')" 2>/dev/null && echo "   ✅ PostgreSQL available" || echo "   ⚠️  PostgreSQL not available"

echo "   Testing ClickHouse..."
python3 -c "import requests; requests.get('http://localhost:18090/ping')" 2>/dev/null && echo "   ✅ ClickHouse available" || echo "   ⚠️  ClickHouse not available"

# Initialize memory system
echo "🧠 Initializing memory system..."
cd "{self.target_dir}"
python3 mini_agent_core.py --action init

echo ""
echo "✅ SETUP COMPLETE!"
echo "Mini-Agent memory system is ready to use."
echo ""
echo "Quick start:"
echo "  mini_agent_memory start"
echo "  mini_agent_memory help"
echo ""
echo "Integration guide: {self.target_dir}/INTEGRATION_GUIDE.md"
"""
        
        setup_file = self.target_dir / "setup_memory.sh"
        setup_file.write_text(setup_content)
        setup_file.chmod(0o755)
        
        print(f"   ✅ Setup script created: {setup_file}")
    
    def create_integration_guide(self):
        """Create integration guide for developers"""
        
        guide_content = f"""# Mini-Agent Memory System - Integration Guide

## Overview

The Mini-Agent Memory System provides persistent memory capabilities for AI assistants, enabling:
- Permanent session memory across interactions
- Knowledge extraction and storage
- User preference learning
- Session continuity
- Cross-database redundancy

## Installation

### Quick Setup
```bash
# Clone or copy the memory system
cp -r {self.installation_dir}/database/* {self.target_dir}/

# Run automated setup
cd {self.target_dir}
./setup_memory.sh

# Test installation
mini_agent_memory demo
```

### Manual Installation
```bash
# Install dependencies
pip install redis psycopg2-binary pymongo requests nats-py

# Configure databases (edit memory_config.json)
cd {self.target_dir}
nano memory_config.json

# Initialize memory system
python3 mini_agent_core.py --action init
```

## Integration with Mini-Agent

### Basic Integration
```python
import sys
sys.path.append('{self.target_dir}')

from mini_agent_core import MiniAgentCore

# Initialize memory system
memory = MiniAgentCore(
    redis_host='localhost',
    redis_port=18000,
    password='your_password'
)

# Start work session
session = memory.start_work_session('UserName', 'ProjectContext')

# Process user interaction
result = memory.process_user_interaction(
    user_input="User question",
    agent_response="AI response",
    tools_used=['tool1', 'tool2']
)

# Get intelligent response
response = memory.get_intelligent_response("User query")
```

### Advanced Integration
```python
from integrated_memory_system import IntegratedMiniAgentMemory

# Use multi-database system
memory = IntegratedMiniAgentMemory(
    redis_host='localhost',
    redis_port=18000,
    password='your_password'
)

# Start integrated session
session = memory.start_integrated_session('UserName')

# Store knowledge across databases
knowledge_id = memory.store_knowledge_integrated(
    knowledge_type='skill',
    content='Learned skill description',
    context={{'domain': 'programming'}},
    metadata={{'source': 'user_interaction'}}
)

# Get comprehensive response
response = memory.get_comprehensive_response("User query")
```

## Configuration

Edit `{self.target_dir}/memory_config.json`:

```json
{{
  "databases": {{
    "dragonfly": {{
      "enabled": true,
      "hosts": ["localhost:18000"],
      "password": "your_password",
      "primary": true
    }},
    "redis": {{
      "enabled": true,
      "hosts": ["localhost:6379"],
      "password": null
    }}
  }}
}}
```

## Usage Examples

### Start Memory Session
```bash
mini_agent_memory start --user-name "Alice" --project-context "web development"
```

### Process Interaction
```bash
mini_agent_memory process --user-input "How do I build a REST API?" --agent-response "Here's how to build a REST API..."
```

### Get Intelligent Response
```bash
mini_agent_memory response --user-input "database design patterns"
```

### Check System Health
```bash
mini_agent_memory health
```

## Database Requirements

### Minimum (Works with any database)
- **Redis**: For session data and basic memory
- **PostgreSQL**: For structured analytics

### Recommended (Full capabilities)
- **DragonflyDB**: For high-performance primary memory
- **Redis Cluster**: For session persistence
- **PostgreSQL**: For structured data
- **ClickHouse**: For analytics
- **MongoDB**: For document storage

### Setup databases:
```bash
# Redis
docker run -d -p 6379:6379 redis

# PostgreSQL  
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres

# Or use TeamADAPT infrastructure (if available)
# DragonflyDB: localhost:18000-18002
# Redis Cluster: localhost:18010-18012
# PostgreSQL: localhost:18030-18032
# ClickHouse: localhost:18090
```

## API Reference

### MiniAgentCore Class
- `start_work_session(user_name, project_context)`
- `process_user_interaction(user_input, agent_response, tools_used)`
- `get_intelligent_response(user_prompt)`
- `record_work_progress(task_name, description, status)`
- `get_memory_statistics()`
- `end_session(summary)`

### IntegratedMiniAgentMemory Class
- `start_integrated_session(user_name, project_context)`
- `store_knowledge_integrated(knowledge_type, content, context, metadata)`
- `get_comprehensive_response(user_prompt)`
- `get_comprehensive_analytics()`

### Memory Storage
- `knowledge`: Facts, skills, relationships
- `user_preferences`: Working style, command preferences
- `session_history`: Complete interaction logs
- `work_progress`: Task tracking and completion

## Troubleshooting

### Connection Issues
```bash
# Test database connectivity
mini_agent_memory health

# Check specific database
redis-cli -h localhost -p 6379 ping
```

### Memory Not Persisting
```bash
# Verify configuration
cat {self.config_file}

# Reinitialize memory system
python3 mini_agent_core.py --action init
```

### Performance Issues
```bash
# Check memory usage
redis-cli -h localhost -p 6379 INFO memory

# Monitor database performance
mini_agent_memory analytics
```

## Deployment Options

### Docker
```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install redis psycopg2-binary pymongo requests nats-py
CMD ["python3", "mini_agent_core.py", "--action", "start"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mini-agent-memory
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mini-agent-memory
  template:
    metadata:
      labels:
        app: mini-agent-memory
    spec:
      containers:
      - name: memory-system
        image: mini-agent-memory:latest
        ports:
        - containerPort: 8080
```

### Cloud Services
- **AWS**: Use ElastiCache (Redis), RDS (PostgreSQL), DocumentDB
- **GCP**: Use Memorystore (Redis), Cloud SQL
- **Azure**: Use Azure Cache for Redis, Azure Database for PostgreSQL

## Support

- **Documentation**: {self.target_dir}/INTEGRATION_GUIDE.md
- **Demo**: `mini_agent_memory demo`
- **Health Check**: `mini_agent_memory health`
- **Analytics**: `mini_agent_memory analytics`

## License

This memory system is designed for Mini-Agent distribution. See individual database licenses for storage backend requirements.

---

*Mini-Agent Memory System v1.0*  
*Built by Chase for permanent AI memory*
"""
        
        guide_file = self.target_dir / "INTEGRATION_GUIDE.md"
        guide_file.write_text(guide_content)
        
        print(f"   ✅ Integration guide created: {guide_file}")

def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Memory System Installer")
    parser.add_argument("--database-config", type=str, help="Path to custom database config")
    parser.add_argument("--install-dir", type=str, help="Installation directory")
    
    args = parser.parse_args()
    
    # Load custom database config if provided
    database_config = None
    if args.database_config and os.path.exists(args.database_config):
        with open(args.database_config, 'r') as f:
            database_config = json.load(f)
    
    installer = MiniAgentMemoryInstaller()
    
    if args.install_dir:
        installer.target_dir = Path(args.install_dir)
        installer.config_file = installer.target_dir / "memory_config.json"
    
    success = installer.install_mini_agent_memory(database_config)
    
    if success:
        print(f"\n🎉 Mini-Agent Memory System installed successfully!")
        print(f"   Installation directory: {installer.target_dir}")
        print(f"   Launcher available: mini_agent_memory")
        print(f"   Setup script: {installer.target_dir}/setup_memory.sh")
        print(f"\nNext steps:")
        print(f"   1. Run: cd {installer.target_dir}")
        print(f"   2. Run: ./setup_memory.sh")
        print(f"   3. Run: mini_agent_memory demo")
    else:
        print(f"\n❌ Installation failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
