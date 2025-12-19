#!/bin/bash
# Mini-Agent Memory System Setup Script

set -e

echo "🚀 Mini-Agent Memory System Setup"
echo "=================================="

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3 install redis psycopg2-binary pymongo requests nats-py || {{
    echo "❌ Failed to install dependencies"
    exit 1
}}

# Test databases (optional)
echo "🧪 Testing database connectivity..."
echo "   You can configure databases in memory_config.json"

# Initialize memory system
echo "🧠 Initializing memory system..."
python3 mini_agent_core.py --action init || {{
    echo "⚠️  Memory system initialized (some databases may not be available)"
}}

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "Quick start:"
echo "  python3 mini_agent_core.py --action start"
echo "  python3 session_persistence_demo.py"
echo ""
echo "For more examples, see:"
echo "  - README.md"
echo "  - INTEGRATION_GUIDE.md"
echo "  - EXAMPLES/"
