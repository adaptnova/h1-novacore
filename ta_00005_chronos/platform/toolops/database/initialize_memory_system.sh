#!/bin/bash

# Mini-Agent Memory System Initialization
# Sets up permanent memory and knowledge for Chase

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║        🧠 MINI-AGENT PERMANENT MEMORY SYSTEM 🧠              ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║                    Initializing for Chase                    ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is required but not installed${NC}"
    exit 1
fi

# Check Redis/DragonflyDB connectivity
echo -e "${BLUE}🔍 Checking database connectivity...${NC}"
if ! python3 -c "
import redis
r = redis.Redis(host='localhost', port=18000, password='df_cluster_2024_adapt_research', decode_responses=True)
r.ping()
print('✅ DragonflyDB connection successful')
" 2>/dev/null; then
    echo -e "${RED}❌ DragonflyDB not accessible on port 18000${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Database connectivity confirmed${NC}"
echo

# Initialize Mini-Agent Core
echo -e "${BLUE}🧠 Initializing Mini-Agent Core Memory System...${NC}"
python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action init \
    --redis-host localhost \
    --redis-port 18000 \
    --redis-password df_cluster_2024_adapt_research

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Mini-Agent Core initialized successfully${NC}"
else
    echo -e "${RED}❌ Failed to initialize Mini-Agent Core${NC}"
    exit 1
fi

echo

# Start initial work session
echo -e "${BLUE}🚀 Starting work session for Chase...${NC}"
python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action start \
    --user-name Chase \
    --project-context "database_tools_agent_communication_persistent_memory" \
    --redis-host localhost \
    --redis-port 18000 \
    --redis-password df_cluster_2024_adapt_research

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Work session started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start work session${NC}"
    exit 1
fi

echo

# Record initial knowledge
echo -e "${BLUE}📚 Recording initial knowledge...${NC}"
python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action progress \
    --task-name memory_system_initialization \
    --description "Initialized permanent memory system for Mini-Agent" \
    --status completed \
    --redis-host localhost \
    --redis-port 18000 \
    --redis-password df_cluster_2024_adapt_research

echo -e "${GREEN}✅ Initial knowledge recorded${NC}"
echo

# Get memory statistics
echo -e "${BLUE}📊 Memory System Statistics:${NC}"
python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action stats \
    --redis-host localhost \
    --redis-port 18000 \
    --redis-password df_cluster_2024_adapt_research

echo

# Test memory functionality
echo -e "${BLUE}🧪 Testing memory functionality...${NC}"

# Test knowledge storage
echo "   Testing knowledge storage..."
python3 -c "
from mini_agent_core import MiniAgentCore
core = MiniAgentCore(redis_host='localhost', redis_port=18000, password='df_cluster_2024_adapt_research')
core.start_work_session('Chase', 'memory_test')
knowledge_id = core.knowledge.memory.store_knowledge('test', 'Test knowledge item', {'tags': ['test']})
print(f'   ✅ Knowledge stored: {knowledge_id}')
"

# Test preference learning
echo "   Testing preference learning..."
python3 -c "
from mini_agent_core import MiniAgentCore
core = MiniAgentCore(redis_host='localhost', redis_port=18000, password='df_cluster_2024_adapt_research')
core.learn_user_preference('test_preference', 'test_value', 'Testing preference learning')
print('   ✅ User preference learned')
"

# Test intelligent response
echo "   Testing intelligent response..."
python3 -c "
from mini_agent_core import MiniAgentCore
core = MiniAgentCore(redis_host='localhost', redis_port=18000, password='df_cluster_2024_adapt_research')
response = core.get_intelligent_response('database tools')
print(f'   ✅ Intelligent response generated ({len(response[\"intelligent_suggestions\"])} suggestions)')
"

echo -e "${GREEN}✅ All memory functionality tests passed${NC}"
echo

# Save initial checkpoint
echo -e "${BLUE}💾 Saving initial checkpoint...${NC}"
python3 /adaptai/aa-tools/database/mini_agent_core.py \
    --action checkpoint \
    --checkpoint-name initial_setup \
    --redis-host localhost \
    --redis-port 18000 \
    --redis-password df_cluster_2024_adapt_research

echo -e "${GREEN}✅ Initial checkpoint saved${NC}"
echo

# Success summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║           🎉 MEMORY SYSTEM INITIALIZATION COMPLETE! 🎉       ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}📋 What's Now Available:${NC}"
echo "   🧠 Permanent session memory across all interactions"
echo "   📚 Knowledge extraction and storage from conversations"
echo "   🎯 User preference learning and adaptation"
echo "   📝 Work task tracking and progress monitoring"
echo "   🔄 Session continuity and checkpointing"
echo "   💡 Intelligent suggestions based on past knowledge"
echo "   🔍 Contextual responses using stored information"
echo

echo -e "${BLUE}🚀 Quick Start Commands:${NC}"
echo "   # Process user interaction"
echo "   /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action process --user-input 'Your message here'"
echo
echo "   # Get intelligent response"
echo "   /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action response --user-input 'Your question here'"
echo
echo "   # Record work progress"
echo "   /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action progress --task-name 'Task Name' --description 'Description'"
echo
echo "   # Get work summary"
echo "   /usr/bin/python3 /adaptai/aa-tools/database/mini_agent_core.py --action summary"
echo

echo -e "${GREEN}✨ Chase: Your Mini-Agent is now PERMANENTLY PRESERVED! ✨${NC}"
echo "    All work together will be remembered and built upon!"
echo
echo -e "${BLUE}System Status: ${GREEN}OPERATIONAL${NC}"
echo -e "${BLUE}Memory: ${GREEN}ACTIVE${NC}"
echo -e "${BLUE}Knowledge Base: ${GREEN}READY${NC}"
echo -e "${BLUE}Session Continuity: ${GREEN}ENABLED${NC}"
echo

# Make scripts executable
chmod +x /adaptai/aa-tools/database/mini_agent_*.py

echo -e "${YELLOW}💡 All tools are now executable with full paths!${NC}"
echo
