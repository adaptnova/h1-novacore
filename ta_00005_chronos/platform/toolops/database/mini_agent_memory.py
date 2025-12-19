#!/usr/bin/env python3
"""
Mini-Agent Persistent Memory System
Integrates with Redis/DragonflyDB for permanent session history, memory, and knowledge
"""

import json
import redis
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class MiniAgentMemory:
    """Permanent memory system for Mini-Agent using Redis/DragonflyDB"""
    
    def __init__(self, redis_host="localhost", redis_port=18000, password=None, db=0):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = password
        self.redis_db = db
        self.redis_client = None
        self.session_id = None
        self.namespace = "mini_agent"
        
        self.connect()
        
    def connect(self):
        """Connect to Redis/DragonflyDB"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=self.redis_db,
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            print(f"✓ Connected to Mini-Agent Memory System ({self.redis_host}:{self.redis_port})")
        except Exception as e:
            print(f"✗ Failed to connect to memory system: {e}")
            raise
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.session_id = session_id
        
        session_data = {
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "total_interactions": 0,
            "tools_created": [],
            "knowledge_gained": [],
            "key_decisions": [],
            "user_preferences": {},
            "session_summary": ""
        }
        
        # Store session data
        self.redis_client.hset(
            f"{self.namespace}:sessions", 
            session_id, 
            json.dumps(session_data)
        )
        
        # Add to active sessions
        self.redis_client.sadd(f"{self.namespace}:active_sessions", session_id)
        
        # Create session conversation history
        self.redis_client.lpush(f"{self.namespace}:conversations:{session_id}", json.dumps({
            "type": "session_start",
            "timestamp": datetime.now().isoformat(),
            "message": "Session started",
            "agent": "system"
        }))
        
        return session_id
    
    def record_interaction(self, interaction_type: str, content: str, 
                          metadata: Dict[str, Any] = None) -> str:
        """Record an interaction in the session"""
        if not self.session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        interaction_id = str(uuid.uuid4())
        interaction_data = {
            "id": interaction_id,
            "session_id": self.session_id,
            "type": interaction_type,  # "user_query", "agent_response", "tool_execution", "knowledge_gain"
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "interaction_number": self._get_interaction_count() + 1
        }
        
        # Store interaction
        interaction_key = f"{self.namespace}:interactions:{self.session_id}"
        self.redis_client.lpush(interaction_key, json.dumps(interaction_data))
        
        # Update session statistics
        session_key = f"{self.namespace}:sessions:{self.session_id}"
        self.redis_client.hincrby(session_key, "total_interactions", 1)
        
        # Add to conversation history
        conversation_entry = {
            "type": "interaction",
            "interaction_type": interaction_type,
            "content": content[:200],  # Truncate for conversation view
            "timestamp": datetime.now().isoformat(),
            "agent": metadata.get("agent", "user") if metadata else "user"
        }
        
        conv_key = f"{self.namespace}:conversations:{self.session_id}"
        self.redis_client.lpush(conv_key, json.dumps(conversation_entry))
        
        return interaction_id
    
    def store_knowledge(self, knowledge_type: str, content: str, 
                       context: Dict[str, Any] = None) -> str:
        """Store knowledge for permanent retention"""
        knowledge_id = str(uuid.uuid4())
        
        # Create knowledge entry
        knowledge_data = {
            "id": knowledge_id,
            "type": knowledge_type,  # "fact", "skill", "relationship", "decision", "preference"
            "content": content,
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "relevance_score": 1.0,
            "source_session": self.session_id,
            "tags": context.get("tags", []) if context else []
        }
        
        # Store knowledge
        self.redis_client.hset(
            f"{self.namespace}:knowledge",
            knowledge_id,
            json.dumps(knowledge_data)
        )
        
        # Add to knowledge index by type
        self.redis_client.sadd(f"{self.namespace}:knowledge_type:{knowledge_type}", knowledge_id)
        
        # Add to tags index
        for tag in knowledge_data["tags"]:
            self.redis_client.sadd(f"{self.namespace}:knowledge_tag:{tag}", knowledge_id)
        
        # Update session knowledge list
        session_key = f"{self.namespace}:sessions:{self.session_id}"
        self.redis_client.hincrby(session_key, "knowledge_gained", 1)
        
        return knowledge_id
    
    def store_user_preference(self, preference_key: str, value: Any, 
                             context: str = None) -> bool:
        """Store user preference for future reference"""
        preference_data = {
            "key": preference_key,
            "value": value,
            "context": context or "",
            "updated_at": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        # Store preference
        self.redis_client.hset(
            f"{self.namespace}:user_preferences",
            preference_key,
            json.dumps(preference_data)
        )
        
        # Update session preferences
        session_key = f"{self.namespace}:sessions:{self.session_id}"
        current_prefs = self.redis_client.hget(session_key, "user_preferences")
        if current_prefs:
            prefs = json.loads(current_prefs)
        else:
            prefs = {}
        
        prefs[preference_key] = preference_data
        self.redis_client.hset(session_key, "user_preferences", json.dumps(prefs))
        
        return True
    
    def get_user_preference(self, preference_key: str) -> Optional[Any]:
        """Get user preference"""
        pref_data = self.redis_client.hget(f"{self.namespace}:user_preferences", preference_key)
        if pref_data:
            return json.loads(pref_data)
        return None
    
    def get_knowledge_by_type(self, knowledge_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get knowledge by type"""
        knowledge_ids = self.redis_client.smembers(f"{self.namespace}:knowledge_type:{knowledge_type}")
        knowledge = []
        
        for kid in list(knowledge_ids)[:limit]:
            k_data = self.redis_client.hget(f"{self.namespace}:knowledge", kid)
            if k_data:
                knowledge.append(json.loads(k_data))
        
        return knowledge
    
    def get_recent_knowledge(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent knowledge"""
        all_knowledge_ids = self.redis_client.hkeys(f"{self.namespace}:knowledge")
        knowledge = []
        
        for kid in all_knowledge_ids[:limit]:
            k_data = self.redis_client.hget(f"{self.namespace}:knowledge", kid)
            if k_data:
                knowledge.append(json.loads(k_data))
        
        return sorted(knowledge, key=lambda x: x["created_at"], reverse=True)
    
    def get_session_history(self, session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get session interaction history"""
        if not session_id:
            session_id = self.session_id
        
        if not session_id:
            return []
        
        interactions = self.redis_client.lrange(
            f"{self.namespace}:interactions:{session_id}", 
            0, limit - 1
        )
        
        return [json.loads(i) for i in interactions]
    
    def get_conversation_history(self, session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history (simplified view)"""
        if not session_id:
            session_id = self.session_id
        
        if not session_id:
            return []
        
        conversations = self.redis_client.lrange(
            f"{self.namespace}:conversations:{session_id}",
            0, limit - 1
        )
        
        return [json.loads(c) for c in conversations]
    
    def search_knowledge(self, query: str, knowledge_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search knowledge by content"""
        knowledge = []
        
        # Get all knowledge or filter by types
        if knowledge_types:
            for ktype in knowledge_types:
                knowledge.extend(self.get_knowledge_by_type(ktype, limit=100))
        else:
            knowledge = self.get_recent_knowledge(limit=100)
        
        # Simple text search (in production, use more sophisticated search)
        query_lower = query.lower()
        results = []
        
        for k in knowledge:
            if (query_lower in k["content"].lower() or 
                any(query_lower in tag.lower() for tag in k.get("tags", []))):
                results.append(k)
        
        return results
    
    def end_session(self, summary: str = None) -> Dict[str, Any]:
        """End current session"""
        if not self.session_id:
            return {"error": "No active session"}
        
        session_key = f"{self.namespace}:sessions:{self.session_id}"
        
        # Update session data
        self.redis_client.hset(session_key, "status", "ended")
        self.redis_client.hset(session_key, "ended_at", datetime.now().isoformat())
        if summary:
            self.redis_client.hset(session_key, "session_summary", summary)
        
        # Remove from active sessions
        self.redis_client.srem(f"{self.namespace}:active_sessions", self.session_id)
        
        # Get final session data
        session_data = self.redis_client.hgetall(session_key)
        
        # Add final conversation entry
        conv_key = f"{self.namespace}:conversations:{self.session_id}"
        self.redis_client.lpush(conv_key, json.dumps({
            "type": "session_end",
            "timestamp": datetime.now().isoformat(),
            "message": "Session ended",
            "agent": "system",
            "summary": summary
        }))
        
        self.session_id = None
        return session_data
    
    def get_session_list(self) -> List[str]:
        """Get list of all sessions"""
        sessions = self.redis_client.hkeys(f"{self.namespace}:sessions")
        return list(sessions)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active sessions"""
        return list(self.redis_client.smembers(f"{self.namespace}:active_sessions"))
    
    def _get_interaction_count(self) -> int:
        """Get current interaction count for session"""
        if not self.session_id:
            return 0
        
        session_key = f"{self.namespace}:sessions:{self.session_id}"
        count = self.redis_client.hget(session_key, "total_interactions")
        return int(count) if count else 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_knowledge = len(self.redis_client.hkeys(f"{self.namespace}:knowledge"))
        total_sessions = len(self.redis_client.hkeys(f"{self.namespace}:sessions"))
        active_sessions = len(self.redis_client.smembers(f"{self.namespace}:active_sessions"))
        total_preferences = len(self.redis_client.hkeys(f"{self.namespace}:user_preferences"))
        
        # Knowledge type breakdown
        knowledge_types = self.redis_client.keys(f"{self.namespace}:knowledge_type:*")
        type_breakdown = {}
        for key in knowledge_types:
            type_name = key.split(":")[-1]
            type_breakdown[type_name] = len(self.redis_client.smembers(key))
        
        return {
            "total_knowledge": total_knowledge,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_preferences": total_preferences,
            "knowledge_types": type_breakdown,
            "memory_system": "operational",
            "connected_to": f"{self.redis_host}:{self.redis_port}"
        }

def main():
    """Demo the memory system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Memory System")
    parser.add_argument("--action", required=True, 
                       choices=["start", "store_knowledge", "get_knowledge", "search", "stats", "end"])
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--type", help="Knowledge type (fact, skill, etc.)")
    parser.add_argument("--content", help="Content to store")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=18000)
    parser.add_argument("--redis-password", default="df_cluster_2024_adapt_research")
    
    args = parser.parse_args()
    
    memory = MiniAgentMemory(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        password=args.redis_password
    )
    
    if args.action == "start":
        session_id = memory.start_session(args.session_id)
        print(f"Session started: {session_id}")
        
        # Record initial knowledge
        memory.record_interaction("session_start", f"Memory system initialized", {
            "agent": "system",
            "session_id": session_id
        })
        
        knowledge_id = memory.store_knowledge("system", f"Memory system started in session {session_id}", {
            "tags": ["memory", "system", "initialization"]
        })
        print(f"Knowledge stored: {knowledge_id}")
    
    elif args.action == "store_knowledge":
        if not memory.session_id:
            memory.start_session()
        
        knowledge_id = memory.store_knowledge(args.type, args.content, {
            "tags": [args.type]
        })
        print(f"Knowledge stored: {knowledge_id}")
    
    elif args.action == "get_knowledge":
        knowledge = memory.get_knowledge_by_type(args.type)
        print(json.dumps(knowledge, indent=2))
    
    elif args.action == "search":
        results = memory.search_knowledge(args.query)
        print(json.dumps(results, indent=2))
    
    elif args.action == "stats":
        stats = memory.get_memory_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.action == "end":
        summary = "Memory system demonstration completed"
        session_data = memory.end_session(summary)
        print(f"Session ended: {session_data}")

if __name__ == "__main__":
    main()
