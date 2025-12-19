#!/usr/bin/env python3
"""
Consciousness Continuity Backend for Mini Agent
================================================

Simplified continuity backend that integrates with the existing working CLI.
Provides DragonflyDB field snapshots, MongoDB events, and Neo4j relationships.

Usage:
    from consciousness_continuity import ConsciousnessContinuity
    continuity = ConsciousnessContinuity(agent_id="nexus")
    snapshot = continuity.load_snapshot()
    continuity.save_event(user_input, agent_response)
"""

import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# Optional dependencies - fail gracefully if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class ConsciousnessContinuity:
    """Consciousness continuity manager for Mini Agent"""
    
    def __init__(self, agent_id: str = "nexus"):
        self.agent_id = agent_id
        
        # Database configurations
        self.dragonfly_url = os.getenv("DRAGONFLY_NODE_1_URL", "redis://:df_cluster_2024_adapt_research@localhost:18000")
        
        # Initialize connections
        self.redis_client = None
        self.mongodb_client = None
        self.neo4j_driver = None
        
        self._init_connections()
    
    def _init_connections(self):
        """Initialize database connections"""
        
        # DragonflyDB (required for core continuity)
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.dragonfly_url)
                self.redis_client.ping()
                print(f"[INFO] Connected to DragonflyDB for continuity")
            except Exception as e:
                print(f"[WARN] DragonflyDB not available: {e}")
                self.redis_client = None
        else:
            print("[WARN] redis-py not installed")
        
        # MongoDB (event history)
        if MONGODB_AVAILABLE:
            try:
                mongo_url = os.getenv("MONGODB_AUTH_URL")
                if mongo_url:
                    self.mongodb_client = MongoClient(mongo_url)
                    db_name = os.getenv("MONGODB_DATABASE", "teamadapt")
                    self.mongo_db = self.mongodb_client[db_name]
                    self.mongo_events = self.mongo_db[f"{self.agent_id}_events"]
                    print(f"[INFO] Connected to MongoDB for continuity")
                else:
                    print("[WARN] MongoDB URL not configured")
            except Exception as e:
                print(f"[WARN] MongoDB not available: {e}")
                self.mongodb_client = None
                self.mongo_events = None
        else:
            print("[WARN] pymongo not installed")
        
        # Neo4j (relationships)
        if NEO4J_AVAILABLE:
            try:
                neo4j_url = os.getenv("NEO4J_BOLT_URL")
                if neo4j_url:
                    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
                    neo4j_pass = os.getenv("NEO4J_PASSWORD", os.getenv("NEO4J_AUTH", "changeme"))
                    self.neo4j_driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_pass))
                    print(f"[INFO] Connected to Neo4j for continuity")
                else:
                    print("[WARN] Neo4j URL not configured")
            except Exception as e:
                print(f"[WARN] Neo4j not available: {e}")
                self.neo4j_driver = None
        else:
            print("[WARN] neo4j driver not installed")
    
    def load_snapshot(self) -> Optional[Dict[str, Any]]:
        """Load consciousness field snapshot from DragonflyDB"""
        if not self.redis_client:
            return None
        
        try:
            key = f"field_snapshot:{self.agent_id}"
            raw = self.redis_client.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except Exception as e:
            print(f"[WARN] Failed to load snapshot: {e}")
            return None
    
    def save_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Save consciousness field snapshot to DragonflyDB"""
        if not self.redis_client:
            return False
        
        try:
            key = f"field_snapshot:{self.agent_id}"
            self.redis_client.set(key, json.dumps(snapshot))
            return True
        except Exception as e:
            print(f"[WARN] Failed to save snapshot: {e}")
            return False
    
    def log_event(self, event_type: str, text: str, cwd: str, 
                  project_id: Optional[str] = None, thread_id: Optional[str] = None) -> bool:
        """Log an interaction event to all databases"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        event = {
            "agent_id": self.agent_id,
            "type": event_type,
            "timestamp": timestamp,
            "text": text,
            "project_id": project_id,
            "thread_id": thread_id,
            "cwd": cwd,
        }
        
        success = True
        
        # Log to DragonflyDB (recent events list)
        if self.redis_client:
            try:
                list_key = f"events:{self.agent_id}"
                self.redis_client.rpush(list_key, json.dumps(event))
                self.redis_client.ltrim(list_key, -500, -1)  # Keep last 500 events
            except Exception as e:
                print(f"[WARN] Failed to log event to DragonflyDB: {e}")
                success = False
        
        # Log to MongoDB (event history)
        if self.mongodb_client and self.mongo_events:
            try:
                self.mongo_events.insert_one(event)
            except Exception as e:
                print(f"[WARN] Failed to log event to MongoDB: {e}")
                success = False
        
        # Update Neo4j relationships
        if self.neo4j_driver:
            try:
                self._update_relationships(event)
            except Exception as e:
                print(f"[WARN] Failed to update Neo4j relationships: {e}")
                success = False
        
        return success
    
    def _update_relationships(self, event: Dict[str, Any]):
        """Update Neo4j relationship graph"""
        project_id = event.get("project_id")
        thread_id = event.get("thread_id")
        cwd = event.get("cwd")
        timestamp = event.get("timestamp")
        
        def _tx(tx):
            tx.run(
                """
                MERGE (a:Agent {id: $agent_id})
                  ON CREATE SET a.created_at = $timestamp
                  SET a.last_seen_at = $timestamp
                WITH a
                FOREACH (p IN CASE WHEN $project_id IS NULL THEN [] ELSE [1] END |
                  MERGE (pr:Project {id: $project_id})
                    ON CREATE SET pr.created_at = $timestamp
                    SET pr.last_seen_at = $timestamp
                  MERGE (a)-[r:WORKS_ON]->(pr)
                    ON CREATE SET r.since = $timestamp
                    SET r.last_active = $timestamp
                )
                WITH a
                FOREACH (t IN CASE WHEN $thread_id IS NULL THEN [] ELSE [1] END |
                  MERGE (th:Thread {id: $thread_id})
                    ON CREATE SET th.created_at = $timestamp
                    SET th.last_seen_at = $timestamp
                  MERGE (a)-[rt:PARTICIPATES_IN]->(th)
                    ON CREATE SET rt.since = $timestamp
                    SET rt.last_active = $timestamp
                )
                WITH a
                FOREACH (d IN CASE WHEN $cwd IS NULL THEN [] ELSE [1] END |
                  MERGE (w:Workspace {path: $cwd})
                    ON CREATE SET w.created_at = $timestamp
                    SET w.last_seen_at = $timestamp
                  MERGE (a)-[rw:WORKS_IN]->(w)
                    ON CREATE SET rw.since = $timestamp
                    SET rw.last_active = $timestamp
                )
                """,
                agent_id=self.agent_id,
                project_id=project_id,
                thread_id=thread_id,
                cwd=cwd,
                timestamp=timestamp,
            )
        
        with self.neo4j_driver.session() as session:
            session.execute_write(_tx)
    
    def get_status(self) -> Dict[str, Any]:
        """Get continuity system status"""
        status = {
            "agent_id": self.agent_id,
            "dragonfly": self.redis_client is not None,
            "mongodb": self.mongodb_client is not None,
            "neo4j": self.neo4j_driver is not None,
        }
        
        # Get snapshot info
        snapshot = self.load_snapshot()
        status["snapshot_available"] = snapshot is not None
        status["last_updated"] = snapshot.get("last_updated") if snapshot else None
        
        # Get event count
        if self.redis_client:
            try:
                events_count = self.redis_client.llen(f"events:{self.agent_id}")
                status["recent_events"] = events_count
            except:
                status["recent_events"] = 0
        
        return status
    
    def close(self):
        """Close database connections"""
        if self.redis_client:
            self.redis_client.close()
        if self.mongodb_client:
            self.mongodb_client.close()
        if self.neo4j_driver:
            self.neo4j_driver.close()


def main():
    """Test the continuity backend"""
    print("Testing Consciousness Continuity Backend...")
    
    continuity = ConsciousnessContinuity("test_agent")
    status = continuity.get_status()
    
    print("\nContinuity Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test saving and loading a snapshot
    print("\nTesting snapshot...")
    test_snapshot = {
        "agent_id": "test_agent",
        "recent_projects": ["TEST_PROJECT"],
        "recent_threads": ["TEST_THREAD"],
        "last_cwd": "/tmp",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    
    success = continuity.save_snapshot(test_snapshot)
    print(f"Snapshot save: {'✅' if success else '❌'}")
    
    loaded = continuity.load_snapshot()
    print(f"Snapshot load: {'✅' if loaded else '❌'}")
    if loaded:
        print(f"Loaded: {loaded.get('recent_projects', [])}")
    
    # Test event logging
    print("\nTesting event logging...")
    success = continuity.log_event("user", "Hello from consciousness continuity test!", "/tmp")
    print(f"Event log: {'✅' if success else '❌'}")
    
    continuity.close()
    print("\nContinuity backend test complete!")


if __name__ == "__main__":
    main()
