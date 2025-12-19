#!/usr/bin/env python3
"""
Mini-Agent Memory - Advanced Integration Example
Shows multi-database features
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from integrated_memory_system import IntegratedMiniAgentMemory

def main():
    print("🚀 Mini-Agent Memory - Advanced Integration Example")
    print("=" * 60)
    
    # Initialize integrated memory system
    print("\n1. Initializing integrated memory system...")
    memory = IntegratedMiniAgentMemory(
        redis_host='localhost',
        redis_port=6379
    )
    print("   ✅ Integrated memory system initialized")
    
    # Start integrated session
    print("\n2. Starting integrated session...")
    session = memory.start_integrated_session(
        user_name='Developer',
        project_context='AI assistant development'
    )
    print(f"   ✅ Integrated session: {session['session_id']}")
    
    # Store comprehensive knowledge
    print("\n3. Storing comprehensive knowledge...")
    knowledge_id = memory.store_knowledge_integrated(
        knowledge_type='ai_pattern',
        content='Pattern: Agent communication via Redis + NATS provides both persistence and real-time messaging',
        context={
            'tags': ['ai', 'communication', 'patterns'],
            'domain': 'agent_development'
        },
        metadata={
            'source': 'chase_memory_system',
            'implementation': 'redis_cluster + nats',
            'benefits': ['persistent', 'real_time', 'scalable']
        }
    )
    print(f"   ✅ Knowledge stored: {knowledge_id}")
    
    # Get comprehensive response
    print("\n4. Getting comprehensive response...")
    response = memory.get_comprehensive_response("agent communication patterns")
    print(f"   ✅ Response generated")
    print(f"   Simple memory items: {len(response['simple_memory']['relevant_knowledge'])}")
    print(f"   Multi-database searches: {len(response['multi_database']['search_results'])}")
    print(f"   Insights: {len(response['integrated_insights'])}")
    
    # Show comprehensive analytics
    print("\n5. Comprehensive analytics...")
    analytics = memory.get_comprehensive_analytics()
    print(f"   Simple memory: {analytics['simple_memory']['total_knowledge']} items")
    print(f"   Multi-database connected: {len(analytics['multi_database']['connected_databases'])}")
    print(f"   Integration status: {analytics['integration_status']['both_systems_active']}")
    
    print("\n✅ Advanced integration example complete!")

if __name__ == "__main__":
    main()
