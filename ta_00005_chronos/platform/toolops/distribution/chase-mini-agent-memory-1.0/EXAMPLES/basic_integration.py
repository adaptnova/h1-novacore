#!/usr/bin/env python3
"""
Mini-Agent Memory - Basic Integration Example
"""

import sys
from pathlib import Path

# Add memory system to path
memory_dir = Path(__file__).parent.parent
sys.path.append(str(memory_dir))

from mini_agent_core import MiniAgentCore

def main():
    print("🧠 Mini-Agent Memory - Basic Integration Example")
    print("=" * 50)
    
    # Initialize memory system
    print("\n1. Initializing memory system...")
    memory = MiniAgentCore(
        redis_host='localhost',
        redis_port=6379
    )
    print("   ✅ Memory system initialized")
    
    # Start session
    print("\n2. Starting work session...")
    session = memory.start_work_session(
        user_name='Alice',
        project_context='web development'
    )
    print(f"   ✅ Session started: {session['session_id']}")
    
    # Process interaction
    print("\n3. Processing user interaction...")
    result = memory.process_user_interaction(
        user_input="I need to build a REST API for user management",
        agent_response="I can help you build a REST API. Let's start with the user model..."
    )
    print("   ✅ Interaction processed")
    
    # Get intelligent response
    print("\n4. Getting intelligent response...")
    response = memory.get_intelligent_response("API development best practices")
    print(f"   ✅ Generated {len(response.get('intelligent_suggestions', []))} suggestions")
    
    # Show analytics
    print("\n5. Memory statistics...")
    stats = memory.get_memory_statistics()
    print(f"   Total knowledge: {stats.get('total_knowledge', 0)}")
    print(f"   Total sessions: {stats.get('total_sessions', 0)}")
    
    print("\n✅ Basic integration example complete!")

if __name__ == "__main__":
    main()
