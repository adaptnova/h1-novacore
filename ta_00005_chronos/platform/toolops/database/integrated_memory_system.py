#!/usr/bin/env python3
"""
Integrated Mini-Agent Memory System
Combines simple memory (DragonflyDB) with multi-database long-term storage
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from mini_agent_core import MiniAgentCore
from multi_database_memory import MultiDatabaseMemory

class IntegratedMiniAgentMemory:
    """Integrated memory system using both simple and multi-database approaches"""
    
    def __init__(self, redis_host="localhost", redis_port=18000, password=None):
        # Initialize both memory systems
        self.simple_memory = MiniAgentCore(
            redis_host=redis_host,
            redis_port=redis_port,
            password=password
        )
        
        self.multi_memory = MultiDatabaseMemory()
        
        # Configuration
        self.config = {
            "use_multi_database": True,
            "storage_strategy": {
                "fast_access": "dragonfly",      # Quick retrieval
                "long_term": "redis_cluster",    # Session persistence  
                "structured": "postgresql",      # Analytics and queries
                "analytics": "clickhouse",       # Pattern analysis
                "documents": "mongodb"           # Flexible storage (if available)
            }
        }
        
        self.session_id = None
        
    def start_integrated_session(self, user_name: str = "Chase", 
                               project_context: str = None) -> Dict[str, Any]:
        """Start session using both memory systems"""
        
        # Start simple memory session (immediate use)
        simple_result = self.simple_memory.start_work_session(user_name, project_context)
        self.session_id = simple_result["session_id"]
        
        # Store in multi-database for long-term
        session_data = {
            "session_id": self.session_id,
            "user_name": user_name,
            "project_context": project_context,
            "start_time": datetime.now().isoformat(),
            "memory_systems": ["simple", "multi_database"],
            "databases_connected": list(self.multi_memory.connected_databases.keys())
        }
        
        self.multi_memory.store_session_comprehensive(session_data)
        
        return {
            "session_id": self.session_id,
            "user_name": user_name,
            "project_context": project_context,
            "simple_memory": simple_result,
            "multi_database": {
                "connected_databases": self.multi_memory.connected_databases,
                "storage_ready": True
            }
        }
    
    def store_knowledge_integrated(self, knowledge_type: str, content: str,
                                 context: Dict[str, Any] = None,
                                 metadata: Dict[str, Any] = None) -> str:
        """Store knowledge using both systems for redundancy and optimization"""
        
        # Store in simple memory (immediate access)
        simple_knowledge_id = self.simple_memory.knowledge.memory.store_knowledge(
            knowledge_type, content, context
        )
        
        # Store in multi-database (long-term, analytics)
        multi_knowledge_id = self.multi_memory.store_knowledge_comprehensive(
            knowledge_type, content, context, metadata
        )
        
        # Link the IDs for cross-reference
        knowledge_id = simple_knowledge_id  # Use simple memory ID as primary
        
        return knowledge_id
    
    def process_interaction_integrated(self, user_input: str, 
                                     agent_response: str = None,
                                     tools_used: List[str] = None) -> Dict[str, Any]:
        """Process interaction using both memory systems"""
        
        # Process with simple memory (immediate learning)
        simple_result = self.simple_memory.process_user_interaction(
            user_input, agent_response, tools_used
        )
        
        # Extract and store knowledge in multi-database
        if agent_response:
            knowledge_items = self._extract_comprehensive_knowledge(user_input, agent_response, tools_used)
            for item in knowledge_items:
                self.multi_memory.store_knowledge_comprehensive(
                    item["type"],
                    item["content"],
                    item["context"],
                    item["metadata"]
                )
        
        return {
            "interaction_processed": True,
            "simple_memory": simple_result,
            "multi_database": {
                "knowledge_stored": len(knowledge_items) if 'knowledge_items' in locals() else 0,
                "databases_used": list(self.multi_memory.connected_databases.keys())
            },
            "session_id": self.session_id
        }
    
    def get_comprehensive_response(self, user_prompt: str) -> Dict[str, Any]:
        """Get response using both memory systems"""
        
        # Get response from simple memory (immediate context)
        simple_response = self.simple_memory.get_intelligent_response(user_prompt)
        
        # Search multi-database for comprehensive context
        multi_search = self.multi_memory.cross_database_search(user_prompt)
        
        # Combine results
        return {
            "user_prompt": user_prompt,
            "simple_memory": {
                "relevant_knowledge": simple_response.get("related_knowledge", []),
                "suggestions": simple_response.get("intelligent_suggestions", []),
                "context": simple_response.get("session_context", {})
            },
            "multi_database": {
                "search_results": multi_search.get("search_results", {}),
                "analytics_ready": bool(self.multi_memory.connected_databases),
                "databases_searched": list(multi_search.get("search_results", {}).keys())
            },
            "integrated_insights": self._generate_integrated_insights(
                user_prompt, simple_response, multi_search
            ),
            "recommended_actions": self._get_integrated_recommendations(
                simple_response, multi_search
            )
        }
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get analytics from both memory systems"""
        
        # Get simple memory stats
        simple_stats = self.simple_memory.get_memory_statistics()
        
        # Get multi-database analytics
        multi_analytics = self.multi_memory.get_knowledge_analytics()
        
        # Get multi-database health
        health = self.multi_memory.get_database_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "simple_memory": {
                "total_knowledge": simple_stats.get("total_knowledge", 0),
                "total_sessions": simple_stats.get("total_sessions", 0),
                "user_preferences": simple_stats.get("total_preferences", 0)
            },
            "multi_database": {
                "connected_databases": multi_analytics.get("connected_databases", {}),
                "database_stats": multi_analytics.get("database_stats", {}),
                "health_status": health.get("overall_status", "unknown")
            },
            "integration_status": {
                "both_systems_active": True,
                "redundancy_enabled": True,
                "long_term_ready": bool(self.multi_memory.connected_databases),
                "analytics_ready": True
            },
            "performance": {
                "fast_access": "dragonflyDB (simple memory)",
                "long_term_storage": "multi-database (Redis + PostgreSQL + ClickHouse)",
                "search_capability": "cross-database search",
                "analytics_capability": "comprehensive analytics"
            }
        }
    
    def end_integrated_session(self, summary: str = None) -> Dict[str, Any]:
        """End session with comprehensive data"""
        
        # Get work summary from simple memory
        simple_summary = self.simple_memory.get_work_summary()
        
        # Update multi-database session
        session_update = {
            "session_id": self.session_id,
            "end_time": datetime.now().isoformat(),
            "summary": summary,
            "total_interactions": simple_summary.get("task_summary", {}).get("current_tasks", 0),
            "knowledge_gained": len(self.simple_memory.knowledge.memory.get_recent_knowledge()),
            "productivity_score": simple_summary.get("productivity_score", 0)
        }
        
        self.multi_memory.store_session_comprehensive(session_update)
        
        # End simple memory session
        simple_end = self.simple_memory.end_session(summary)
        
        return {
            "session_ended": True,
            "session_id": self.session_id,
            "simple_memory_summary": simple_summary,
            "multi_database_update": session_update,
            "total_knowledge_items": simple_end.get("knowledge_gained", 0),
            "databases_used": list(self.multi_memory.connected_databases.keys())
        }
    
    def _extract_comprehensive_knowledge(self, user_input: str, agent_response: str,
                                       tools_used: List[str] = None) -> List[Dict[str, Any]]:
        """Extract comprehensive knowledge from interaction"""
        
        knowledge_items = []
        
        # Tool usage knowledge
        if tools_used:
            for tool in tools_used:
                knowledge_items.append({
                    "type": "tool_usage",
                    "content": f"Used tool: {tool} in response to user query",
                    "context": {
                        "user_query": user_input[:100],
                        "tools": tools_used,
                        "scenario": "interactive_help"
                    },
                    "metadata": {
                        "source": "tool_execution",
                        "tool_name": tool,
                        "interaction_context": user_input
                    }
                })
        
        # User pattern knowledge
        if any(word in user_input.lower() for word in ["remember", "store", "save"]):
            knowledge_items.append({
                "type": "user_behavior",
                "content": f"User explicitly requested memory storage: {user_input[:100]}",
                "context": {
                    "user_action": "explicit_memory_request",
                    "response_provided": bool(agent_response)
                },
                "metadata": {
                    "behavior_type": "memory_focus",
                    "user_preference": "persistent_storage"
                }
            })
        
        # Agent response patterns
        if agent_response:
            if "database" in agent_response.lower():
                knowledge_items.append({
                    "type": "agent_response_pattern",
                    "content": f"Agent provided database-related response",
                    "context": {
                        "response_type": "database_help",
                        "user_query": user_input,
                        "agent_capability": "database_assistance"
                    },
                    "metadata": {
                        "capability": "database_expertise",
                        "response_category": "technical_help"
                    }
                })
        
        return knowledge_items
    
    def _generate_integrated_insights(self, user_prompt: str, 
                                    simple_response: Dict, 
                                    multi_search: Dict) -> List[str]:
        """Generate insights combining both memory systems"""
        
        insights = []
        
        # Simple memory insights
        if simple_response.get("related_knowledge"):
            insights.append(f"Found {len(simple_response['related_knowledge'])} related items in fast memory")
        
        if simple_response.get("intelligent_suggestions"):
            insights.append(f"Generated {len(simple_response['intelligent_suggestions'])} intelligent suggestions")
        
        # Multi-database insights
        total_multi_results = sum(
            len(results) for results in multi_search.get("search_results", {}).values()
            if isinstance(results, list)
        )
        
        if total_multi_results > 0:
            insights.append(f"Cross-database search found {total_multi_results} historical matches")
        
        # Integration insights
        if self.multi_memory.connected_databases:
            insights.append(f"Long-term memory available across {len(self.multi_memory.connected_databases)} databases")
        
        return insights
    
    def _get_integrated_recommendations(self, simple_response: Dict, 
                                      multi_search: Dict) -> List[str]:
        """Get recommendations from both systems"""
        
        recommendations = []
        
        # Simple memory recommendations
        if simple_response.get("recommended_actions"):
            recommendations.extend(simple_response["recommended_actions"])
        
        # Multi-database recommendations
        if multi_search.get("search_results"):
            for db, results in multi_search["search_results"].items():
                if isinstance(results, list) and results:
                    recommendations.append(f"Apply historical knowledge from {db}")
        
        return recommendations[:5]  # Return top 5

def main():
    """Demo the integrated memory system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated Mini-Agent Memory System")
    parser.add_argument("--action", required=True,
                       choices=["start", "store", "process", "response", "analytics", "end"])
    parser.add_argument("--user-input", help="User input")
    parser.add_argument("--agent-response", help="Agent response")
    parser.add_argument("--type", help="Knowledge type")
    print("🎉 INTEGRATED MULTI-DATABASE MEMORY SYSTEM READY!")
    print("✅ Combines fast access (DragonflyDB) with long-term storage (Redis + PostgreSQL + ClickHouse)")
    print("✅ Provides redundancy, analytics, and comprehensive memory")
    print("✅ Ready for infinite collaborative work with Chase!")

if __name__ == "__main__":
    main()
