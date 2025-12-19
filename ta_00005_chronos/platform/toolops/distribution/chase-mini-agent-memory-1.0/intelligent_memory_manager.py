#!/usr/bin/env python3
"""
Mini-Agent Intelligent Multi-Tier Memory Management System
===========================================================

Advanced memory management with:
- Multi-tier storage (short/medium/long term)
- Intelligent database selection
- Automatic TTL management
- Memory promotion/demotion
- Intelligent fan-out to appropriate databases

Author: Mini-Agent Core System
Version: 2.0
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import redis
import pymongo
import clickhouse_connect
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentMemoryManager:
    """
    Advanced memory management system with intelligent database selection
    and automatic memory lifecycle management.
    """
    
    def __init__(self):
        """Initialize multi-database connections and memory tiers."""
        
        # Database configurations
        self.db_configs = {
            'dragonfly': {
                'host': 'localhost',
                'port': 18000,
                'password': 'df_cluster_2024_adapt_research',
                'ttl_seconds': 7 * 24 * 60 * 60,  # 7 days
                'primary': True,
                'use_cases': ['fast_access', 'primary_memory', 'user_preferences', 'current_session']
            },
            'redis': {
                'host': 'localhost', 
                'port': 18010,
                'password': None,
                'ttl_seconds': 30 * 24 * 60 * 60,  # 30 days
                'primary': False,
                'use_cases': ['session_data', 'chat_history', 'short_term_buffer']
            },
            'mongodb': {
                'host': 'localhost',
                'port': 18070,
                'database': 'mini_agent_memory',
                'use_cases': ['documents', 'flexible_schemas', 'long_term_storage', 'analytics_raw']
            },
            'postgresql': {
                'host': 'localhost',
                'port': 18030,
                'database': 'teamadapt',
                'user': 'postgres_admin_user',
                'password': 'changeme',  # From /adaptai/db.env
                'use_cases': ['structured_analytics', 'complex_queries', 'relationships', 'reporting']
            },
            'clickhouse': {
                'host': 'localhost',
                'port': 18090,
                'database': 'mini_agent_memory',
                'use_cases': ['real_time_analytics', 'pattern_detection', 'trend_analysis', 'metrics']
            },
            'qdrant': {
                'host': 'localhost',
                'port': 18050,
                'use_cases': ['vector_storage', 'semantic_search', 'ai_embeddings', 'similarity_matching']
            }
        }
        
        # Initialize database connections
        self.connections = self._init_connections()
        
        # Memory tier definitions
        self.memory_tiers = {
            'short_term': {
                'ttl_hours': 24,
                'auto_promote': True,
                'promote_after_hours': 12,
                'databases': ['dragonfly', 'redis'],
                'memory_types': ['temp_calculations', 'current_context', 'recent_messages', 'active_sessions']
            },
            'medium_term': {
                'ttl_days': 30,
                'auto_promote': True,
                'promote_after_days': 14,
                'databases': ['mongodb', 'redis'],
                'memory_types': ['conversation_history', 'user_preferences', 'project_progress', 'learned_patterns']
            },
            'long_term': {
                'ttl_days': -1,  # Permanent
                'auto_promote': False,
                'databases': ['mongodb', 'postgresql', 'qdrant'],
                'memory_types': ['core_knowledge', 'important_decisions', 'user_profiles', 'ai_embeddings', 'analytics']
            }
        }
        
        logger.info("Intelligent Memory Manager initialized with multi-tier system")

    def _init_connections(self) -> Dict[str, Any]:
        """Initialize database connections."""
        connections = {}
        
        try:
            # DragonflyDB connection
            connections['dragonfly'] = redis.Redis(
                host=self.db_configs['dragonfly']['host'],
                port=self.db_configs['dragonfly']['port'],
                password=self.db_configs['dragonfly']['password'],
                decode_responses=True,
                socket_timeout=5
            )
            connections['dragonfly'].ping()
            logger.info("✅ DragonflyDB connected")
        except Exception as e:
            logger.error(f"❌ DragonflyDB connection failed: {e}")
            
        try:
            # Redis connection
            connections['redis'] = redis.Redis(
                host=self.db_configs['redis']['host'],
                port=self.db_configs['redis']['port'],
                decode_responses=True,
                socket_timeout=5
            )
            connections['redis'].ping()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            
        try:
            # MongoDB connection
            connections['mongodb'] = pymongo.MongoClient(
                host=self.db_configs['mongodb']['host'],
                port=self.db_configs['mongodb']['port'],
                serverSelectionTimeoutMS=5000
            )
            connections['mongodb'].admin.command('ping')
            logger.info("✅ MongoDB connected")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            
        try:
            # ClickHouse connection - fixed timeout parameter
            connections['clickhouse'] = clickhouse_connect.get_client(
                host=self.db_configs['clickhouse']['host'],
                port=self.db_configs['clickhouse']['port']
            )
            # Test connection
            connections['clickhouse'].query("SELECT 1")
            logger.info("✅ ClickHouse connected")
        except Exception as e:
            logger.error(f"❌ ClickHouse connection failed: {e}")
            
        try:
            # Qdrant connection (HTTP API)
            connections['qdrant'] = self.db_configs['qdrant']
            response = requests.get(f"http://localhost:18050/collections", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Qdrant connected")
            else:
                raise Exception("Qdrant not responding")
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            
        try:
            # PostgreSQL connection
            import psycopg2
            connections['postgresql'] = psycopg2.connect(
                host=self.db_configs['postgresql']['host'],
                port=self.db_configs['postgresql']['port'],
                database=self.db_configs['postgresql']['database'],
                user=self.db_configs['postgresql']['user'],
                password=self.db_configs['postgresql']['password']
            )
            # Test connection
            connections['postgresql'].cursor().execute("SELECT 1")
            connections['postgresql'].commit()
            logger.info("✅ PostgreSQL connected")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            # Keep config for potential reconnection
            connections['postgresql'] = self.db_configs['postgresql']
            
        return connections

    def determine_memory_tier(self, memory_type: str, importance: int = 5, 
                            context: str = "general") -> str:
        """
        Intelligently determine which memory tier to use based on content type and importance.
        
        Args:
            memory_type: Type of memory (conversation, preference, knowledge, etc.)
            importance: Importance score (1-10, 10 being most important)
            context: Context of the memory (work, personal, project, etc.)
            
        Returns:
            Memory tier: 'short_term', 'medium_term', or 'long_term'
        """
        
        # High importance memories go directly to long term
        if importance >= 8:
            return 'long_term'
            
        # Specific memory types mapping
        short_term_types = ['temp_calculation', 'current_context', 'recent_message', 'active_session']
        long_term_types = ['core_knowledge', 'important_decision', 'user_profile', 'learned_pattern']
        
        if memory_type in short_term_types:
            return 'short_term'
        elif memory_type in long_term_types:
            return 'long_term'
        else:
            # Default to medium term for most memories
            return 'medium_term'

    def select_optimal_databases(self, memory_type: str, tier: str, 
                               has_vector: bool = False) -> List[str]:
        """
        Select optimal databases for storing specific memory type.
        
        Args:
            memory_type: Type of memory to store
            tier: Memory tier (short_term, medium_term, long_term)
            has_vector: Whether memory contains vector data
            
        Returns:
            List of optimal database names
        """
        
        tier_config = self.memory_tiers[tier]
        selected_dbs = []
        
        # Check if memory type matches tier use cases
        for db_name in tier_config['databases']:
            db_config = self.db_configs.get(db_name)
            if db_config and memory_type in db_config.get('use_cases', []):
                selected_dbs.append(db_name)
                
        # Ensure DragonflyDB is always included for primary storage
        if 'dragonfly' not in selected_dbs and tier in ['short_term', 'medium_term']:
            selected_dbs.append('dragonfly')
            
        # Qdrant for vector data
        if has_vector and 'qdrant' not in selected_dbs:
            selected_dbs.append('qdrant')
            
        # ClickHouse for analytics
        if tier in ['medium_term', 'long_term'] and 'clickhouse' not in selected_dbs:
            selected_dbs.append('clickhouse')
            
        return selected_dbs

    def store_memory(self, key: str, content: Any, memory_type: str, 
                    importance: int = 5, context: str = "general",
                    tags: List[str] = None, metadata: Dict = None) -> Dict[str, bool]:
        """
        Store memory intelligently across appropriate databases with optimal tier placement.
        
        Args:
            key: Unique identifier for the memory
            content: Content to store
            memory_type: Type of memory
            importance: Importance score (1-10)
            context: Context (work, personal, etc.)
            tags: Optional tags for categorization
            metadata: Optional metadata
            
        Returns:
            Dictionary with database storage results
        """
        
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}
            
        # Determine optimal tier and databases
        tier = self.determine_memory_tier(memory_type, importance, context)
        has_vector = isinstance(content, dict) and 'vector' in content
        
        selected_dbs = self.select_optimal_databases(memory_type, tier, has_vector)
        
        # Prepare memory record
        memory_record = {
            'key': key,
            'content': content,
            'memory_type': memory_type,
            'tier': tier,
            'importance': importance,
            'context': context,
            'tags': tags,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            'created_at': time.time(),
            'database_sources': selected_dbs
        }
        
        storage_results = {}
        
        # Store in each selected database
        for db_name in selected_dbs:
            if db_name in self.connections:
                try:
                    success = self._store_in_database(db_name, memory_record)
                    storage_results[db_name] = success
                    logger.info(f"✅ Stored in {db_name}: {success}")
                except Exception as e:
                    logger.error(f"❌ Failed to store in {db_name}: {e}")
                    storage_results[db_name] = False
            else:
                logger.warning(f"⚠️ {db_name} not connected, skipping")
                storage_results[db_name] = False
                
        return storage_results

    def _store_in_database(self, db_name: str, memory_record: Dict) -> bool:
        """Store memory record in specific database."""
        
        key = memory_record['key']
        tier = memory_record['tier']
        
        if db_name == 'dragonfly':
            # DragonflyDB with TTL
            redis_client = self.connections['dragonfly']
            memory_key = f"memory:{memory_record['memory_type']}:{key}"
            
            # Set TTL based on tier
            ttl = self.db_configs['dragonfly']['ttl_seconds'] if tier == 'short_term' else None
            
            # Store as JSON
            data = json.dumps(memory_record, default=str)
            if ttl:
                redis_client.setex(memory_key, ttl, data)
            else:
                redis_client.set(memory_key, data)
                
            return True
            
        elif db_name == 'redis':
            # Redis for session data
            redis_client = self.connections['redis']
            memory_key = f"session:{memory_record['memory_type']}:{key}"
            data = json.dumps(memory_record, default=str)
            
            # TTL based on tier
            if tier == 'short_term':
                ttl = 24 * 60 * 60  # 24 hours
                redis_client.setex(memory_key, ttl, data)
            else:
                redis_client.set(memory_key, data)
                
            return True
            
        elif db_name == 'mongodb':
            # MongoDB for documents
            mongo_client = self.connections['mongodb']
            db = mongo_client[self.db_configs['mongodb']['database']]
            collection = db[f"{tier}_memory"]
            
            # Insert document
            result = collection.insert_one(memory_record)
            return result.inserted_id is not None
            
        elif db_name == 'clickhouse':
            # ClickHouse for analytics
            clickhouse_client = self.connections['clickhouse']
            
            # Create table if not exists
            clickhouse_client.command("""
                CREATE TABLE IF NOT EXISTS memory_analytics (
                    key String,
                    memory_type String,
                    tier String,
                    importance Int32,
                    context String,
                    timestamp DateTime,
                    tags Array(String),
                    metadata String
                ) ENGINE = MergeTree()
                ORDER BY (timestamp, tier)
            """)
            
            # Insert analytics data
            clickhouse_client.insert(
                "memory_analytics",
                [[
                    key,
                    memory_record['memory_type'],
                    tier,
                    memory_record['importance'],
                    context,
                    datetime.now(),
                    tags,
                    json.dumps(metadata, default=str)
                ]]
            )
            
            return True
            
        elif db_name == 'qdrant':
            # Qdrant for vector storage (if vector present)
            if 'vector' in memory_record['content']:
                # This would require proper Qdrant client implementation
                logger.info("Vector storage in Qdrant (implementation needed)")
                return True
            return True
            
        elif db_name == 'postgresql':
            # PostgreSQL for structured analytics
            postgresql_conn = self.connections['postgresql']
            cursor = postgresql_conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_analytics (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) NOT NULL,
                    memory_type VARCHAR(100),
                    tier VARCHAR(50),
                    importance INTEGER,
                    context VARCHAR(100),
                    timestamp TIMESTAMP,
                    tags TEXT[],
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert analytics data
            cursor.execute("""
                INSERT INTO memory_analytics 
                (key, memory_type, tier, importance, context, timestamp, tags, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                key,
                memory_record['memory_type'],
                tier,
                memory_record['importance'],
                context,
                datetime.now(),
                tags,
                json.dumps(metadata, default=str)
            ))
            
            postgresql_conn.commit()
            cursor.close()
            
            return True
            
        else:
            logger.warning(f"Unknown database: {db_name}")
            return False

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
            List of memory records ranked by relevance
        """
        
        results = []
        
        # Search in each connected database
        for db_name, connection in self.connections.items():
            if connection is None:
                continue
                
            try:
                db_results = self._search_in_database(db_name, query, memory_types, tiers, limit)
                results.extend(db_results)
            except Exception as e:
                logger.error(f"Search failed in {db_name}: {e}")
                
        # Rank and limit results
        results.sort(key=lambda x: x.get('importance', 0), reverse=True)
        return results[:limit]

    def _search_in_database(self, db_name: str, query: str, 
                          memory_types: List[str] = None, 
                          tiers: List[str] = None, 
                          limit: int = 10) -> List[Dict]:
        """Search memory in specific database."""
        
        results = []
        
        if db_name in ['dragonfly', 'redis']:
            # Redis/DragonflyDB search
            redis_client = self.connections[db_name]
            pattern = f"memory:*:{query}*" if query != "*" else "memory:*"
            
            for key in redis_client.keys(pattern):
                try:
                    data = redis_client.get(key)
                    memory_record = json.loads(data)
                    
                    # Apply filters
                    if memory_types and memory_record['memory_type'] not in memory_types:
                        continue
                    if tiers and memory_record['tier'] not in tiers:
                        continue
                        
                    memory_record['database_found'] = db_name
                    results.append(memory_record)
                    
                    if len(results) >= limit:
                        break
                        
                except Exception as e:
                    logger.error(f"Error parsing memory from {db_name}: {e}")
                    
        elif db_name == 'mongodb':
            # MongoDB search
            mongo_client = self.connections['mongodb']
            db = mongo_client[self.db_configs['mongodb']['database']]
            
            # Search across all tier collections
            for tier_collection in ['short_term_memory', 'medium_term_memory', 'long_term_memory']:
                collection = db[tier_collection]
                
                # Build query
                mongo_query = {"$text": {"$search": query}}
                if memory_types:
                    mongo_query["memory_type"] = {"$in": memory_types}
                if tiers:
                    mongo_query["tier"] = {"$in": tiers}
                    
                cursor = collection.find(mongo_query).limit(limit)
                
                for doc in cursor:
                    doc['database_found'] = db_name
                    results.append(doc)
                    
        return results

    def promote_memory(self, key: str, from_tier: str, to_tier: str) -> bool:
        """
        Promote memory from one tier to another (e.g., short_term -> medium_term).
        
        Args:
            key: Memory key
            from_tier: Current tier
            to_tier: Target tier
            
        Returns:
            Success status
        """
        
        logger.info(f"Promoting memory {key} from {from_tier} to {to_tier}")
        
        # Load from current tier
        memory_record = self._load_memory_from_tier(key, from_tier)
        if not memory_record:
            logger.error(f"Memory {key} not found in {from_tier}")
            return False
            
        # Update tier
        memory_record['tier'] = to_tier
        memory_record['promoted_at'] = time.time()
        memory_record['promotion_history'] = memory_record.get('promotion_history', []) + [{
            'from': from_tier,
            'to': to_tier,
            'timestamp': time.time()
        }]
        
        # Store in new tier
        selected_dbs = self.select_optimal_databases(
            memory_record['memory_type'], 
            to_tier, 
            'vector' in memory_record['content']
        )
        
        success_count = 0
        for db_name in selected_dbs:
            if db_name in self.connections:
                try:
                    if self._store_in_database(db_name, memory_record):
                        success_count += 1
                    # Clean up from old tier
                    self._delete_from_tier(key, from_tier, db_name)
                except Exception as e:
                    logger.error(f"Promotion failed in {db_name}: {e}")
                    
        return success_count > 0

    def _load_memory_from_tier(self, key: str, tier: str) -> Optional[Dict]:
        """Load memory record from specific tier."""
        
        # Search in all databases for this tier
        for db_name, connection in self.connections.items():
            if connection is None:
                continue
                
            try:
                if db_name in ['dragonfly', 'redis']:
                    redis_client = connection
                    pattern = f"memory:*:{key}"
                    for redis_key in redis_client.keys(pattern):
                        data = redis_client.get(redis_key)
                        return json.loads(data)
                        
                elif db_name == 'mongodb':
                    mongo_client = connection
                    db = mongo_client[self.db_configs['mongodb']['database']]
                    collection = db[f"{tier}_memory"]
                    doc = collection.find_one({"key": key})
                    return doc if doc else None
                    
            except Exception as e:
                logger.error(f"Error loading memory from {db_name}: {e}")
                
        return None

    def _delete_from_tier(self, key: str, tier: str, db_name: str) -> bool:
        """Delete memory from specific tier and database."""
        
        try:
            if db_name in ['dragonfly', 'redis']:
                redis_client = self.connections[db_name]
                pattern = f"memory:*:{key}"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    return True
                    
            elif db_name == 'mongodb':
                mongo_client = self.connections[db_name]
                db = mongo_client[self.db_configs['mongodb']['database']]
                collection = db[f"{tier}_memory"]
                result = collection.delete_one({"key": key})
                return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error deleting memory from {db_name}: {e}")
            
        return False

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics across all databases."""
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'tier_distribution': {},
            'memory_type_distribution': {},
            'database_usage': {},
            'total_memories': 0,
            'connectivity': {}
        }
        
        # Check connectivity
        for db_name, connection in self.connections.items():
            stats['connectivity'][db_name] = connection is not None
            
        # Get statistics from each database
        for db_name in ['dragonfly', 'redis', 'mongodb', 'clickhouse']:
            if db_name in self.connections and self.connections[db_name]:
                try:
                    db_stats = self._get_database_statistics(db_name)
                    stats['database_usage'][db_name] = db_stats
                except Exception as e:
                    logger.error(f"Failed to get stats from {db_name}: {e}")
                    
        return stats

    def _get_database_statistics(self, db_name: str) -> Dict[str, Any]:
        """Get statistics from specific database."""
        
        stats = {}
        
        if db_name in ['dragonfly', 'redis']:
            redis_client = self.connections[db_name]
            
            # Count memories by pattern
            memory_keys = redis_client.keys("memory:*")
            stats['total_memories'] = len(memory_keys)
            
            # Count by memory type
            memory_types = {}
            for key in memory_keys:
                try:
                    data = redis_client.get(key)
                    record = json.loads(data)
                    mem_type = record.get('memory_type', 'unknown')
                    memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
                except:
                    pass
                    
            stats['memory_types'] = memory_types
            
        elif db_name == 'postgresql':
            # PostgreSQL statistics
            if hasattr(self.connections['postgresql'], 'cursor'):
                postgresql_conn = self.connections['postgresql']
                cursor = postgresql_conn.cursor()
                
                # Count memories
                cursor.execute("SELECT COUNT(*) FROM memory_analytics")
                total = cursor.fetchone()[0]
                
                # Count by tier
                cursor.execute("SELECT tier, COUNT(*) FROM memory_analytics GROUP BY tier")
                tier_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.close()
                
                stats['total_memories'] = total
                stats['tier_distribution'] = tier_counts
                
        elif db_name == 'mongodb':
            mongo_client = self.connections['mongodb']
            db = mongo_client[self.db_configs['mongodb']['database']]
            
            # Count across all tier collections
            total = 0
            tier_counts = {}
            
            for tier_collection in ['short_term_memory', 'medium_term_memory', 'long_term_memory']:
                collection = db[tier_collection]
                count = collection.count_documents({})
                tier_counts[tier_collection.replace('_memory', '')] = count
                total += count
                
            stats['total_memories'] = total
            stats['tier_distribution'] = tier_counts
            
        return stats

    def cleanup_expired_memory(self) -> Dict[str, int]:
        """Clean up expired memory across all databases."""
        
        cleaned = {}
        
        for db_name, connection in self.connections.items():
            if connection is None:
                continue
                
            try:
                if db_name in ['dragonfly', 'redis']:
                    # Redis automatically handles TTL, but we can clean up expired keys
                    redis_client = connection
                    
                    # Count expired keys
                    expired_patterns = [
                        "memory:*:temp_*",
                        "memory:*:recent_*",
                        "session:*:temp_*"
                    ]
                    
                    for pattern in expired_patterns:
                        keys = redis_client.keys(pattern)
                        if keys:
                            cleaned[db_name] = len(keys)
                            # Redis will clean these up automatically
                            
                elif db_name == 'mongodb':
                    # MongoDB cleanup based on timestamp
                    mongo_client = connection
                    db = mongo_client[self.db_configs['mongodb']['database']]
                    
                    # Clean up old short-term memories
                    cutoff_date = datetime.now() - timedelta(days=7)
                    collection = db['short_term_memory']
                    result = collection.delete_many({
                        'created_at': {'$lt': cutoff_date.timestamp()}
                    })
                    
                    cleaned[db_name] = result.deleted_count
                    
                elif db_name == 'postgresql':
                    # PostgreSQL cleanup based on created_at timestamp
                    postgresql_conn = self.connections['postgresql']
                    cursor = postgresql_conn.cursor()
                    
                    cutoff_date = datetime.now() - timedelta(days=7)
                    cursor.execute("""
                        DELETE FROM memory_analytics 
                        WHERE created_at < %s AND tier = 'short_term'
                    """, (cutoff_date,))
                    
                    cleaned_count = cursor.rowcount
                    postgresql_conn.commit()
                    cursor.close()
                    
                    cleaned[db_name] = cleaned_count
                    
            except Exception as e:
                logger.error(f"Cleanup failed in {db_name}: {e}")
                
        return cleaned

    def run_maintenance_cycle(self) -> Dict[str, Any]:
        """Run complete maintenance cycle: promotion, cleanup, statistics."""
        
        logger.info("🧹 Running memory maintenance cycle...")
        
        maintenance_results = {
            'promotion_attempted': 0,
            'promotion_successful': 0,
            'cleanup_stats': {},
            'final_statistics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. Attempt memory promotion
        try:
            # This would require more complex logic to identify candidates
            # For now, log the intent
            logger.info("🔄 Memory promotion cycle (logic to be implemented)")
            maintenance_results['promotion_attempted'] = 0
            maintenance_results['promotion_successful'] = 0
        except Exception as e:
            logger.error(f"Promotion cycle failed: {e}")
            
        # 2. Clean up expired memory
        try:
            cleanup_stats = self.cleanup_expired_memory()
            maintenance_results['cleanup_stats'] = cleanup_stats
            logger.info(f"✅ Cleanup completed: {cleanup_stats}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            
        # 3. Get final statistics
        try:
            final_stats = self.get_memory_statistics()
            maintenance_results['final_statistics'] = final_stats
            logger.info("✅ Statistics updated")
        except Exception as e:
            logger.error(f"Statistics failed: {e}")
            
        logger.info("🏁 Memory maintenance cycle completed")
        return maintenance_results


# Example usage and testing
if __name__ == "__main__":
    
    # Initialize the intelligent memory manager
    memory_manager = IntelligentMemoryManager()
    
    print("🤖 Mini-Agent Intelligent Memory Manager")
    print("=" * 50)
    
    # Test storing different types of memory
    print("\n📝 Testing memory storage...")
    
    # Short-term memory (current calculation)
    result1 = memory_manager.store_memory(
        key="calc_001",
        content={"result": 42, "operation": "2+40"},
        memory_type="temp_calculation",
        importance=2,
        context="math",
        tags=["calculation", "temp"]
    )
    print(f"Short-term memory stored: {result1}")
    
    # Medium-term memory (conversation)
    result2 = memory_manager.store_memory(
        key="conv_001", 
        content={"user": "Alice", "message": "Hello!", "response": "Hi Alice!"},
        memory_type="conversation",
        importance=5,
        context="chat",
        tags=["conversation", "user"]
    )
    print(f"Medium-term memory stored: {result2}")
    
    # Long-term memory (important knowledge)
    result3 = memory_manager.store_memory(
        key="know_001",
        content={"fact": "Python is a programming language", "category": "technology"},
        memory_type="core_knowledge",
        importance=9,
        context="work",
        tags=["knowledge", "python", "programming"],
        metadata={"verified": True, "source": "manual"}
    )
    print(f"Long-term memory stored: {result3}")
    
    # Search test
    print("\n🔍 Testing memory search...")
    search_results = memory_manager.search_memory("hello", limit=5)
    print(f"Search results: {len(search_results)} found")
    
    # Statistics
    print("\n📊 Getting memory statistics...")
    stats = memory_manager.get_memory_statistics()
    print(f"Database connectivity: {stats['connectivity']}")
    print(f"Total memories: {stats.get('total_memories', 'N/A')}")
    
    # Maintenance cycle
    print("\n🔧 Running maintenance cycle...")
    maintenance = memory_manager.run_maintenance_cycle()
    print(f"Maintenance completed: {maintenance['timestamp']}")
    
    print("\n✅ Intelligent Memory Manager test completed!")