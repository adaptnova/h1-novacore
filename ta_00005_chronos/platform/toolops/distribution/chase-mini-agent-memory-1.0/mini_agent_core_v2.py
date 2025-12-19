#!/usr/bin/env python3
"""
Mini-Agent Core System v2.0 - Intelligent Memory Integration
============================================================

Updated core system that integrates the intelligent memory manager
with multi-tier storage and automatic lifecycle management.

Author: Mini-Agent Core System  
Version: 2.0
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from intelligent_memory_manager import IntelligentMemoryManager

class MiniAgentCoreV2:
    """
    Enhanced Mini-Agent core with intelligent multi-tier memory management.
    """
    
    def __init__(self):
        """Initialize Mini-Agent with intelligent memory management."""
        
        print("🤖 Initializing Mini-Agent Core v2.0...")
        print("🧠 Loading intelligent memory management system...")
        
        # Initialize intelligent memory manager
        self.memory_manager = IntelligentMemoryManager()
        
        # System metadata
        self.agent_id = f"mini_agent_{int(time.time())}"
        self.session_start = time.time()
        self.version = "2.0"
        
        print("✅ Mini-Agent Core v2.0 initialized with intelligent memory!")
        
    def process_user_interaction(self, user_input: str, agent_response: str,
                                context: str = "general", tags: List[str] = None) -> Dict[str, Any]:
        """
        Process user interaction with intelligent memory storage.
        
        Args:
            user_input: User's input
            agent_response: Agent's response
            context: Context of the interaction
            tags: Optional tags
            
        Returns:
            Processing result with memory storage status
        """
        
        if tags is None:
            tags = ["conversation", "user_interaction"]
            
        # Store the interaction in memory
        interaction_key = f"interaction_{int(time.time())}_{hash(user_input) % 10000}"
        
        interaction_data = {
            'user_input': user_input,
            'agent_response': agent_response,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_start
        }
        
        # Store with intelligent tier placement
        storage_result = self.memory_manager.store_memory(
            key=interaction_key,
            content=interaction_data,
            memory_type="conversation",
            importance=5,  # Default importance
            context=context,
            tags=tags
        )
        
        return {
            'interaction_stored': True,
            'storage_result': storage_result,
            'key': interaction_key,
            'timestamp': datetime.now().isoformat()
        }
        
    def store_knowledge(self, key: str, content: Any, knowledge_type: str = "general",
                       importance: int = 7, context: str = "knowledge",
                       tags: List[str] = None, metadata: Dict = None) -> Dict[str, bool]:
        """
        Store knowledge with intelligent database selection.
        
        Args:
            key: Unique knowledge identifier
            content: Knowledge content
            knowledge_type: Type of knowledge
            importance: Importance score (1-10)
            context: Context of the knowledge
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Storage results by database
        """
        
        if tags is None:
            tags = ["knowledge"]
        if metadata is None:
            metadata = {}
            
        # Intelligent memory placement
        return self.memory_manager.store_memory(
            key=key,
            content=content,
            memory_type=knowledge_type,
            importance=importance,
            context=context,
            tags=tags,
            metadata=metadata
        )
        
    def search_memory(self, query: str, memory_types: List[str] = None,
                     tiers: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search memory across all databases with intelligent ranking.
        
        Args:
            query: Search query
            memory_types: Filter by memory types
            tiers: Filter by memory tiers
            limit: Maximum results
            
        Returns:
            Ranked memory results
        """
        
        return self.memory_manager.search_memory(
            query=query,
            memory_types=memory_types,
            tiers=tiers,
            limit=limit
        )
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including memory statistics."""
        
        stats = self.memory_manager.get_memory_statistics()
        
        # Add system information
        stats['system'] = {
            'agent_id': self.agent_id,
            'version': self.version,
            'session_start': self.session_start,
            'uptime_seconds': time.time() - self.session_start,
            'memory_manager_status': 'active'
        }
        
        return stats
        
    def promote_memory(self, key: str, from_tier: str, to_tier: str) -> bool:
        """
        Promote memory from one tier to another.
        
        Args:
            key: Memory key
            from_tier: Source tier
            to_tier: Target tier
            
        Returns:
            Success status
        """
        
        return self.memory_manager.promote_memory(key, from_tier, to_tier)
        
    def run_maintenance(self) -> Dict[str, Any]:
        """Run memory maintenance cycle."""
        
        return self.memory_manager.run_maintenance_cycle()
        
    def intelligent_response(self, user_query: str) -> Dict[str, Any]:
        """
        Generate intelligent response using memory context.
        
        Args:
            user_query: User's query
            
        Returns:
            Response with memory context
        """
        
        # Search relevant memory
        relevant_memory = self.search_memory(user_query, limit=5)
        
        # Generate response context
        context = {
            'user_query': user_query,
            'relevant_memories': len(relevant_memory),
            'memory_sources': list(set([m.get('database_found', 'unknown') for m in relevant_memory])),
            'timestamp': datetime.now().isoformat()
        }
        
        # In a real implementation, this would use the memories to generate context-aware responses
        response = f"Found {len(relevant_memory)} relevant memories for your query. Processing with memory context..."
        
        return {
            'response': response,
            'context': context,
            'memories_found': relevant_memory
        }


# Command line interface
def main():
    """Main CLI interface for Mini-Agent Core v2.0."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Core v2.0 with Intelligent Memory")
    parser.add_argument('--action', choices=['init', 'status', 'test', 'search', 'maintenance'], 
                       default='status', help='Action to perform')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--tier-from', help='Source tier for promotion')
    parser.add_argument('--tier-to', help='Target tier for promotion')
    parser.add_argument('--key', help='Memory key')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = MiniAgentCoreV2()
    
    if args.action == 'init':
        print("🧠 Mini-Agent Core v2.0 initialized with intelligent memory management")
        
    elif args.action == 'status':
        status = agent.get_system_status()
        print("\n📊 System Status:")
        print(f"Agent ID: {status['system']['agent_id']}")
        print(f"Version: {status['system']['version']}")
        print(f"Uptime: {status['system']['uptime_seconds']:.1f} seconds")
        print("\n🔌 Database Connectivity:")
        for db, connected in status['connectivity'].items():
            status_icon = "✅" if connected else "❌"
            print(f"  {status_icon} {db}")
            
    elif args.action == 'test':
        print("🧪 Running intelligent memory tests...")
        
        # Test 1: Store different types of memory
        print("\n1. Testing short-term memory storage...")
        short_result = agent.store_knowledge(
            key="test_short_001",
            content={"type": "calculation", "result": "42"},
            knowledge_type="temp_calculation",
            importance=2
        )
        print(f"   Result: {short_result}")
        
        print("\n2. Testing medium-term memory storage...")
        medium_result = agent.store_knowledge(
            key="test_medium_001", 
            content={"type": "preference", "user": "test", "value": "dark_mode"},
            knowledge_type="user_preference",
            importance=6
        )
        print(f"   Result: {medium_result}")
        
        print("\n3. Testing long-term memory storage...")
        long_result = agent.store_knowledge(
            key="test_long_001",
            content={"type": "knowledge", "fact": "Python is awesome", "verified": True},
            knowledge_type="core_knowledge",
            importance=9
        )
        print(f"   Result: {long_result}")
        
        print("\n4. Testing memory search...")
        search_results = agent.search_memory("test", limit=5)
        print(f"   Found {len(search_results)} memories")
        
        print("\n5. Running maintenance cycle...")
        maintenance = agent.run_maintenance()
        print(f"   Maintenance completed: {maintenance['timestamp']}")
        
        print("\n✅ All tests completed!")
        
    elif args.action == 'search':
        if not args.query:
            print("❌ --query required for search action")
            return
            
        print(f"🔍 Searching for: {args.query}")
        results = agent.search_memory(args.query)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('key', 'N/A')} (tier: {result.get('tier', 'N/A')})")
            
    elif args.action == 'maintenance':
        print("🔧 Running maintenance cycle...")
        maintenance = agent.run_maintenance()
        print("Maintenance Results:")
        print(f"  Cleanup: {maintenance['cleanup_stats']}")
        print(f"  Timestamp: {maintenance['timestamp']}")


if __name__ == "__main__":
    main()
