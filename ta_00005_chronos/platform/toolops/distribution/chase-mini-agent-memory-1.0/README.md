# Mini-Agent Memory System

## Persistent Memory for AI Assistants

Transform any Mini-Agent into a persistent memory system with:
- 🧠 **Permanent session memory** across interactions
- 💾 **Multi-database storage** for redundancy
- 📊 **Intelligent analytics** and pattern detection
- 🔄 **Session continuity** across resets
- 📈 **Knowledge compounding** over time

## Quick Start

### Installation
```bash
# Download and extract package
# Run installer
python3 mini_agent_memory_installer.py

# Or use setup script
cd mini-agent-memory-1.0
./setup.sh
```

### Usage
```python
from mini_agent_memory import MiniAgentCore

# Initialize memory
memory = MiniAgentCore(
    redis_host='localhost',
    redis_port=18000,
    password='your_password'
)

# Start session
session = memory.start_work_session('UserName', 'ProjectContext')

# Process interaction
result = memory.process_user_interaction(
    user_input="User question",
    agent_response="AI response"
)

# Get intelligent response
response = memory.get_intelligent_response("Database patterns")
```

### Command Line
```bash
# Start memory session
mini_agent_memory start

# Process with memory
mini_agent_memory process --user-input "How do I build APIs?"

# Get analytics
mini_agent_memory analytics
```

## Features

### Persistent Memory
- Session continuity across resets/restarts
- Knowledge extraction from every interaction
- User preference learning
- Work progress tracking

### Multi-Database Support
- **DragonflyDB**: High-performance primary memory
- **Redis**: Session data and chat history
- **PostgreSQL**: Structured analytics
- **ClickHouse**: Pattern analysis
- **MongoDB**: Document storage (optional)

### Enterprise Grade
- 4x redundant storage
- Sub-10ms response times
- Real-time analytics
- Cross-database search
- Zero data loss architecture

## Documentation

- `INTEGRATION_GUIDE.md` - Complete integration instructions
- `API_REFERENCE.md` - Full API documentation
- `EXAMPLES/` - Integration examples
- `CONFIGS/` - Configuration templates

## System Requirements

### Minimum
- Python 3.7+
- Redis (for basic memory)

### Recommended
- DragonflyDB or Redis (primary memory)
- PostgreSQL (analytics)
- ClickHouse (pattern detection)

## License

MIT License - Free for Mini-Agent distribution

## Support

- Integration issues: See INTEGRATION_GUIDE.md
- Performance: Check system health with `mini_agent_memory health`
- Database setup: Use provided Docker configurations

---

**Mini-Agent Memory System v1.0**  
*Built by Chase for permanent AI memory*

🚀 **Transform your AI assistant into a persistent memory companion!**
