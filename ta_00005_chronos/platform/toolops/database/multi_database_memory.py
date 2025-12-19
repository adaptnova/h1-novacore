#!/usr/bin/env python3
"""
Multi-Database Memory System
Comprehensive long-term memory using multiple database types
"""

import json
import redis
import psycopg2
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import subprocess

class MultiDatabaseMemory:
    """Multi-database memory system for comprehensive long-term storage"""
    
    def __init__(self):
        # Database connections
        self.dragonfly_clients = {}  # Primary memory (fast access)
        self.redis_clients = {}       # Session data and chat history
        self.postgresql_connections = {}  # Structured data and analytics
        self.mongodb_client = None    # Document storage
        self.clickhouse_client = None # Analytics and pattern analysis
        
        # Database configuration
        self.db_config = {
            "dragonfly": {
                "hosts": ["localhost:18000", "localhost:18001", "localhost:18002"],
                "password": "df_cluster_2024_adapt_research",
                "namespace": "memory_primary"
            },
            "redis": {
                "hosts": ["localhost:18010", "localhost:18011", "localhost:18012"],
                "password": None,
                "namespace": "memory_sessions"
            },
            "postgresql": {
                "hosts": ["localhost:18030", "localhost:18031", "localhost:18032"],
                "user": "postgres_admin_user",
                "password": "changeme",
                "database": "mini_agent_memory",
                "namespace": "memory_structured"
            },
            "mongodb": {
                "host": "localhost:27017",
                "database": "mini_agent_memory",
                "namespace": "memory_documents"
            },
            "clickhouse": {
                "host": "localhost:18090",
                "database": "mini_agent_memory",
                "namespace": "memory_analytics"
            }
        }
        
        self.connected_databases = {}
        self.connect_all_databases()
    
    def connect_all_databases(self):
        """Connect to all available databases"""
        print("🔗 Connecting to multi-database memory system...")
        
        # Connect to DragonflyDB (primary memory)
        self._connect_dragonflydb()
        
        # Connect to Redis Cluster (sessions)
        self._connect_redis_cluster()
        
        # Connect to PostgreSQL (structured data)
        self._connect_postgresql()
        
        # Connect to MongoDB (if available)
        self._connect_mongodb()
        
        # Connect to ClickHouse (analytics)
        self._connect_clickhouse()
        
        print(f"✅ Connected to {len(self.connected_databases)} databases")
        for db in self.connected_databases:
            print(f"   ✓ {db}")
    
    def _connect_dragonflydb(self):
        """Connect to DragonflyDB cluster"""
        try:
            for i, host in enumerate(self.db_config["dragonfly"]["hosts"]):
                host, port = host.split(":")
                client = redis.Redis(
                    host=host,
                    port=int(port),
                    password=self.db_config["dragonfly"]["password"],
                    decode_responses=True,
                    socket_timeout=5
                )
                client.ping()
                self.dragonfly_clients[f"node_{i}"] = client
                self.connected_databases["dragonfly"] = True
            print("   ✓ DragonflyDB cluster connected")
        except Exception as e:
            print(f"   ⚠️  DragonflyDB connection failed: {e}")
            self.connected_databases["dragonfly"] = False
    
    def _connect_redis_cluster(self):
        """Connect to Redis cluster"""
        try:
            for i, host in enumerate(self.db_config["redis"]["hosts"]):
                host, port = host.split(":")
                client = redis.Redis(
                    host=host,
                    port=int(port),
                    decode_responses=True,
                    socket_timeout=5
                )
                client.ping()
                self.redis_clients[f"node_{i}"] = client
                self.connected_databases["redis"] = True
            print("   ✓ Redis cluster connected")
        except Exception as e:
            print(f"   ⚠️  Redis cluster connection failed: {e}")
            self.connected_databases["redis"] = False
    
    def _connect_postgresql(self):
        """Connect to PostgreSQL"""
        try:
            host, port = self.db_config["postgresql"]["hosts"][0].split(":")
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                user=self.db_config["postgresql"]["user"],
                password=self.db_config["postgresql"]["password"],
                database=self.db_config["postgresql"]["database"]
            )
            
            # Create tables if they don't exist
            self._create_postgresql_tables(conn)
            
            self.postgresql_connections["primary"] = conn
            self.connected_databases["postgresql"] = True
            print("   ✓ PostgreSQL connected")
        except Exception as e:
            print(f"   ⚠️  PostgreSQL connection failed: {e}")
            self.connected_databases["postgresql"] = False
    
    def _connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            from pymongo import MongoClient
            client = MongoClient(
                self.db_config["mongodb"]["host"],
                serverSelectionTimeoutMS=5000
            )
            client.admin.command('ismaster')
            self.mongodb_client = client[self.db_config["mongodb"]["database"]]
            self.connected_databases["mongodb"] = True
            print("   ✓ MongoDB connected")
        except Exception as e:
            print(f"   ⚠️  MongoDB connection failed: {e}")
            self.connected_databases["mongodb"] = False
    
    def _connect_clickhouse(self):
        """Connect to ClickHouse"""
        try:
            import requests
            response = requests.get(f"http://{self.db_config['clickhouse']['host']}/ping")
            if response.status_code == 200:
                self.connected_databases["clickhouse"] = True
                print("   ✓ ClickHouse connected")
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  ClickHouse connection failed: {e}")
            self.connected_databases["clickhouse"] = False
    
    def _create_postgresql_tables(self, conn):
        """Create necessary PostgreSQL tables"""
        cursor = conn.cursor()
        
        # Knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id UUID PRIMARY KEY,
                type VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                tags TEXT[],
                context JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                relevance_score DECIMAL(3,2) DEFAULT 1.0,
                source_session VARCHAR(255)
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key VARCHAR(255) PRIMARY KEY,
                value JSONB NOT NULL,
                context VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(255)
            )
        """)
        
        # Session analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_analytics (
                id UUID PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_name VARCHAR(255),
                project_context VARCHAR(255),
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_interactions INTEGER DEFAULT 0,
                knowledge_gained INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                duration_minutes INTEGER,
                productivity_score DECIMAL(3,2)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge USING GIN(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_analytics_user ON session_analytics(user_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_analytics_start ON session_analytics(start_time)")
        
        conn.commit()
        cursor.close()
    
    def store_knowledge_comprehensive(self, knowledge_type: str, content: str, 
                                    context: Dict[str, Any] = None,
                                    metadata: Dict[str, Any] = None) -> str:
        """Store knowledge across multiple databases for redundancy and analytics"""
        
        knowledge_id = hashlib.md5(f"{knowledge_type}:{content}".encode()).hexdigest()
        timestamp = datetime.now().isoformat()
        
        # Store in DragonflyDB (primary, fast access)
        if self.connected_databases.get("dragonfly"):
            self._store_in_dragonflydb(knowledge_id, knowledge_type, content, context, metadata, timestamp)
        
        # Store in PostgreSQL (structured, analytics-ready)
        if self.connected_databases.get("postgresql"):
            self._store_in_postgresql(knowledge_id, knowledge_type, content, context, metadata, timestamp)
        
        # Store in MongoDB (document storage, flexible)
        if self.connected_databases.get("mongodb"):
            self._store_in_mongodb(knowledge_id, knowledge_type, content, context, metadata, timestamp)
        
        return knowledge_id
    
    def _store_in_dragonflydb(self, knowledge_id: str, knowledge_type: str, content: str,
                             context: Dict[str, Any], metadata: Dict[str, Any], timestamp: str):
        """Store knowledge in DragonflyDB for fast access"""
        for node_name, client in self.dragonfly_clients.items():
            try:
                knowledge_data = {
                    "id": knowledge_id,
                    "type": knowledge_type,
                    "content": content,
                    "context": json.dumps(context) if context else {},
                    "metadata": json.dumps(metadata) if metadata else {},
                    "created_at": timestamp,
                    "node": node_name
                }
                
                # Store by type for easy retrieval
                client.hset(f"memory:knowledge:{knowledge_type}", mapping=knowledge_data)
                
                # Store by ID for direct access
                client.hset(f"memory:knowledge:id:{knowledge_id}", mapping=knowledge_data)
                
                # Add to type index
                client.sadd(f"memory:index:types", knowledge_type)
                
            except Exception as e:
                print(f"   ⚠️  Failed to store in DragonflyDB {node_name}: {e}")
    
    def _store_in_postgresql(self, knowledge_id: str, knowledge_type: str, content: str,
                           context: Dict[str, Any], metadata: Dict[str, Any], timestamp: str):
        """Store knowledge in PostgreSQL for structured analytics"""
        try:
            cursor = self.postgresql_connections["primary"].cursor()
            cursor.execute("""
                INSERT INTO knowledge (id, type, content, tags, context, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    access_count = knowledge.access_count + 1
            """, (
                knowledge_id,
                knowledge_type,
                content,
                context.get("tags", []) if context else [],
                json.dumps(context) if context else {},
                timestamp
            ))
            
            self.postgresql_connections["primary"].commit()
            cursor.close()
            
        except Exception as e:
            print(f"   ⚠️  Failed to store in PostgreSQL: {e}")
    
    def _store_in_mongodb(self, knowledge_id: str, knowledge_type: str, content: str,
                         context: Dict[str, Any], metadata: Dict[str, Any], timestamp: str):
        """Store knowledge in MongoDB for document flexibility"""
        try:
            collection = self.mongodb_client["knowledge"]
            
            document = {
                "_id": knowledge_id,
                "type": knowledge_type,
                "content": content,
                "context": context or {},
                "metadata": metadata or {},
                "created_at": datetime.fromisoformat(timestamp),
                "database_source": "mongodb"
            }
            
            collection.replace_one({"_id": knowledge_id}, document, upsert=True)
            
        except Exception as e:
            print(f"   ⚠️  Failed to store in MongoDB: {e}")
    
    def store_session_comprehensive(self, session_data: Dict[str, Any]) -> str:
        """Store session data across multiple databases"""
        
        session_id = session_data.get("session_id")
        
        # Store in Redis (session data and chat history)
        if self.connected_databases.get("redis"):
            for node_name, client in self.redis_clients.items():
                try:
                    client.hset(f"memory:sessions", session_id, json.dumps(session_data))
                    client.hset(f"memory:sessions:node:{node_name}", session_id, json.dumps(session_data))
                    client.expire(f"memory:sessions:{session_id}", 86400 * 30)  # 30 days
                except Exception as e:
                    print(f"   ⚠️  Failed to store session in Redis {node_name}: {e}")
        
        # Store analytics in PostgreSQL
        if self.connected_databases.get("postgresql"):
            try:
                cursor = self.postgresql_connections["primary"].cursor()
                cursor.execute("""
                    INSERT INTO session_analytics 
                    (id, session_id, user_name, project_context, total_interactions, 
                     knowledge_gained, tasks_completed, duration_minutes, productivity_score)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id) DO UPDATE SET
                        end_time = CURRENT_TIMESTAMP,
                        total_interactions = EXCLUDED.total_interactions
                """, (
                    session_id,
                    session_data.get("user_name"),
                    session_data.get("project_context"),
                    session_data.get("total_interactions", 0),
                    session_data.get("knowledge_gained", 0),
                    session_data.get("tasks_completed", 0),
                    session_data.get("duration_minutes"),
                    session_data.get("productivity_score")
                ))
                
                self.postgresql_connections["primary"].commit()
                cursor.close()
                
            except Exception as e:
                print(f"   ⚠️  Failed to store session analytics in PostgreSQL: {e}")
    
    def store_user_preference_comprehensive(self, preference_key: str, value: Any,
                                          context: Dict[str, Any] = None) -> bool:
        """Store user preference across multiple databases"""
        
        # Store in DragonflyDB (fast access)
        if self.connected_databases.get("dragonfly"):
            for node_name, client in self.dragonfly_clients.items():
                try:
                    client.hset(f"memory:preferences", preference_key, json.dumps({
                        "key": preference_key,
                        "value": value,
                        "context": context or {},
                        "updated_at": datetime.now().isoformat(),
                        "node": node_name
                    }))
                except Exception as e:
                    print(f"   ⚠️  Failed to store preference in DragonflyDB {node_name}: {e}")
        
        # Store in PostgreSQL (structured analytics)
        if self.connected_databases.get("postgresql"):
            try:
                cursor = self.postgresql_connections["primary"].cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (key, value, context, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        context = EXCLUDED.context,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    preference_key,
                    json.dumps(value),
                    context.get("context") if context else None
                ))
                
                self.postgresql_connections["primary"].commit()
                cursor.close()
                
            except Exception as e:
                print(f"   ⚠️  Failed to store preference in PostgreSQL: {e}")
        
        return True
    
    def get_knowledge_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from all databases"""
        
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "connected_databases": self.connected_databases,
            "database_stats": {}
        }
        
        # DragonflyDB stats
        if self.connected_databases.get("dragonfly"):
            df_stats = {}
            for node_name, client in self.dragonfly_clients.items():
                try:
                    info = client.info()
                    df_stats[node_name] = {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory_human": info.get("used_memory_human", "unknown"),
                        "total_commands_processed": info.get("total_commands_processed", 0)
                    }
                except:
                    df_stats[node_name] = {"status": "error"}
            analytics["database_stats"]["dragonfly"] = df_stats
        
        # PostgreSQL analytics
        if self.connected_databases.get("postgresql"):
            try:
                cursor = self.postgresql_connections["primary"].cursor()
                
                # Knowledge counts by type
                cursor.execute("""
                    SELECT type, COUNT(*) as count 
                    FROM knowledge 
                    GROUP BY type 
                    ORDER BY count DESC
                """)
                knowledge_by_type = dict(cursor.fetchall())
                
                # Recent sessions
                cursor.execute("""
                    SELECT user_name, COUNT(*) as sessions, AVG(duration_minutes) as avg_duration
                    FROM session_analytics 
                    WHERE start_time > CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY user_name
                """)
                session_stats = cursor.fetchall()
                
                analytics["database_stats"]["postgresql"] = {
                    "knowledge_by_type": knowledge_by_type,
                    "session_stats": [
                        {"user": row[0], "sessions": row[1], "avg_duration": float(row[2]) if row[2] else 0}
                        for row in session_stats
                    ]
                }
                
                cursor.close()
                
            except Exception as e:
                analytics["database_stats"]["postgresql"] = {"error": str(e)}
        
        # Redis cluster stats
        if self.connected_databases.get("redis"):
            redis_stats = {}
            for node_name, client in self.redis_clients.items():
                try:
                    info = client.info()
                    redis_stats[node_name] = {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory_human": info.get("used_memory_human", "unknown"),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0)
                    }
                except:
                    redis_stats[node_name] = {"status": "error"}
            analytics["database_stats"]["redis"] = redis_stats
        
        return analytics
    
    def cross_database_search(self, query: str, knowledge_types: List[str] = None) -> Dict[str, Any]:
        """Search knowledge across multiple databases"""
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "search_results": {}
        }
        
        # Search in DragonflyDB (fast)
        if self.connected_databases.get("dragonfly"):
            try:
                df_results = []
                client = list(self.dragonfly_clients.values())[0]  # Use first node
                
                # Search by knowledge types
                if knowledge_types:
                    for ktype in knowledge_types:
                        keys = client.hkeys(f"memory:knowledge:{ktype}")
                        for key in keys:
                            data = client.hgetall(f"memory:knowledge:{ktype}")
                            if query.lower() in data.get("content", "").lower():
                                df_results.append({
                                    "database": "dragonfly",
                                    "type": ktype,
                                    "id": data.get("id"),
                                    "content": data.get("content"),
                                    "context": json.loads(data.get("context", "{}")),
                                    "created_at": data.get("created_at")
                                })
                
                results["search_results"]["dragonfly"] = df_results
                
            except Exception as e:
                results["search_results"]["dragonfly"] = {"error": str(e)}
        
        # Search in PostgreSQL (structured)
        if self.connected_databases.get("postgresql"):
            try:
                cursor = self.postgresql_connections["primary"].cursor()
                
                where_clause = "WHERE content ILIKE %s"
                params = [f"%{query}%"]
                
                if knowledge_types:
                    where_clause += " AND type = ANY(%s)"
                    params.append(knowledge_types)
                
                cursor.execute(f"""
                    SELECT id, type, content, context, created_at, relevance_score
                    FROM knowledge
                    {where_clause}
                    ORDER BY relevance_score DESC, created_at DESC
                    LIMIT 50
                """, params)
                
                pg_results = [
                    {
                        "database": "postgresql",
                        "id": row[0],
                        "type": row[1],
                        "content": row[2],
                        "context": json.loads(row[3]) if row[3] else {},
                        "created_at": row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                        "relevance_score": float(row[5]) if row[5] else 1.0
                    }
                    for row in cursor.fetchall()
                ]
                
                results["search_results"]["postgresql"] = pg_results
                cursor.close()
                
            except Exception as e:
                results["search_results"]["postgresql"] = {"error": str(e)}
        
        return results
    
    def get_database_health(self) -> Dict[str, Any]:
        """Get comprehensive health check across all databases"""
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "databases": {}
        }
        
        healthy_count = 0
        total_count = 0
        
        # Test each database
        for db_name in ["dragonfly", "redis", "postgresql", "mongodb", "clickhouse"]:
            if self.connected_databases.get(db_name):
                total_count += 1
                
                if db_name == "dragonfly":
                    try:
                        # Test all DragonflyDB nodes
                        nodes_healthy = 0
                        for client in self.dragonfly_clients.values():
                            if client.ping():
                                nodes_healthy += 1
                        
                        health["databases"][db_name] = {
                            "status": "healthy" if nodes_healthy > 0 else "unhealthy",
                            "nodes_healthy": nodes_healthy,
                            "total_nodes": len(self.dragonfly_clients)
                        }
                        if nodes_healthy > 0:
                            healthy_count += 1
                            
                    except Exception as e:
                        health["databases"][db_name] = {"status": "error", "error": str(e)}
                
                elif db_name == "redis":
                    try:
                        nodes_healthy = 0
                        for client in self.redis_clients.values():
                            if client.ping():
                                nodes_healthy += 1
                        
                        health["databases"][db_name] = {
                            "status": "healthy" if nodes_healthy > 0 else "unhealthy",
                            "nodes_healthy": nodes_healthy,
                            "total_nodes": len(self.redis_clients)
                        }
                        if nodes_healthy > 0:
                            healthy_count += 1
                            
                    except Exception as e:
                        health["databases"][db_name] = {"status": "error", "error": str(e)}
                
                elif db_name == "postgresql":
                    try:
                        cursor = self.postgresql_connections["primary"].cursor()
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        cursor.close()
                        
                        health["databases"][db_name] = {"status": "healthy"}
                        healthy_count += 1
                        
                    except Exception as e:
                        health["databases"][db_name] = {"status": "error", "error": str(e)}
                
                elif db_name == "mongodb":
                    try:
                        self.mongodb_client.admin.command('ismaster')
                        health["databases"][db_name] = {"status": "healthy"}
                        healthy_count += 1
                        
                    except Exception as e:
                        health["databases"][db_name] = {"status": "error", "error": str(e)}
                
                elif db_name == "clickhouse":
                    try:
                        import requests
                        response = requests.get(f"http://{self.db_config['clickhouse']['host']}/ping")
                        health["databases"][db_name] = {
                            "status": "healthy" if response.status_code == 200 else "unhealthy"
                        }
                        if response.status_code == 200:
                            healthy_count += 1
                            
                    except Exception as e:
                        health["databases"][db_name] = {"status": "error", "error": str(e)}
        
        # Overall health status
        if healthy_count == total_count and total_count > 0:
            health["overall_status"] = "healthy"
        elif healthy_count > 0:
            health["overall_status"] = "degraded"
        else:
            health["overall_status"] = "unhealthy"
        
        return health

def main():
    """Demo the multi-database memory system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Database Memory System")
    parser.add_argument("--action", required=True,
                       choices=["init", "store", "search", "analytics", "health"])
    parser.add_argument("--type", help="Knowledge type")
    parser.add_argument("--content", help="Content to store")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--key", help="Preference key")
    parser.add_argument("--value", help="Preference value")
    
    args = parser.parse_args()
    
    # Initialize multi-database memory
    memory = MultiDatabaseMemory()
    
    if args.action == "init":
        print("✅ Multi-database memory system initialized")
        health = memory.get_database_health()
        print(json.dumps(health, indent=2))
    
    elif args.action == "store":
        knowledge_id = memory.store_knowledge_comprehensive(
            args.type, args.content
        )
        print(f"Knowledge stored: {knowledge_id}")
    
    elif args.action == "search":
        results = memory.cross_database_search(args.query)
        print(json.dumps(results, indent=2))
    
    elif args.action == "analytics":
        analytics = memory.get_knowledge_analytics()
        print(json.dumps(analytics, indent=2))
    
    elif args.action == "health":
        health = memory.get_database_health()
        print(json.dumps(health, indent=2))

if __name__ == "__main__":
    main()
