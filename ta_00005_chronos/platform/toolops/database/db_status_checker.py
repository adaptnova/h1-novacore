#!/usr/bin/env python3
"""
Database Status Checker
Checks connectivity and basic stats for multiple database types
"""

import sys
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class DatabaseStatusChecker:
    def __init__(self):
        self.results = {}
        
    def check_redis(self, host="localhost", port=6379, password=None) -> Dict[str, Any]:
        """Check Redis status"""
        try:
            import redis
            r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
            info = r.info()
            return {
                "status": "connected",
                "type": "redis",
                "version": info.get("redis_version", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace": info.get("keyspace", {})
            }
        except Exception as e:
            return {"status": "error", "type": "redis", "error": str(e)}
    
    def check_mongodb(self, connection_string="mongodb://localhost:27017") -> Dict[str, Any]:
        """Check MongoDB status"""
        try:
            from pymongo import MongoClient
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            server_info = client.server_info()
            db_stats = client.admin.command("dbStats")
            
            return {
                "status": "connected",
                "type": "mongodb",
                "version": server_info.get("version", "unknown"),
                "uptime": server_info.get("uptime", 0),
                "databases": db_stats.get("databases", 0),
                "collections": db_stats.get("collections", 0),
                "objects": db_stats.get("objects", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0)
            }
        except Exception as e:
            return {"status": "error", "type": "mongodb", "error": str(e)}
    
    def check_cassandra(self, host="localhost", port=9042) -> Dict[str, Any]:
        """Check Cassandra status"""
        try:
            from cassandra.cluster import Cluster
            cluster = Cluster([host], port=port)
            session = cluster.connect()
            
            # Get cluster info
            hosts = cluster.metadata.all_hosts()
            keyspaces = cluster.metadata.keyspaces
            
            # Get basic stats
            result = session.execute("SELECT * FROM system.local")
            local_info = result.one()
            
            cluster.shutdown()
            
            return {
                "status": "connected",
                "type": "cassandra",
                "cluster_name": cluster.metadata.cluster_name,
                "hosts": len(hosts),
                "keyspaces": len(keyspaces),
                "data_center": local_info.data_center if local_info else "unknown",
                "rack": local_info.rack if local_info else "unknown"
            }
        except Exception as e:
            return {"status": "error", "type": "cassandra", "error": str(e)}
    
    def check_qdrant(self, host="localhost", port=6333) -> Dict[str, Any]:
        """Check Qdrant status"""
        try:
            import requests
            response = requests.get(f"http://{host}:{port}/collections", timeout=5)
            if response.status_code == 200:
                collections = response.json()
                return {
                    "status": "connected",
                    "type": "qdrant",
                    "collections_count": len(collections.get("result", {}).get("collections", [])),
                    "collections": [c["name"] for c in collections.get("result", {}).get("collections", [])]
                }
            else:
                return {"status": "error", "type": "qdrant", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "type": "qdrant", "error": str(e)}
    
    def check_nats(self, host="nats://localhost:4222") -> Dict[str, Any]:
        """Check NATS status"""
        try:
            import nats
            import asyncio
            
            async def check_nats_async():
                nc = await nats.connect(host, allow_reconnect=False)
                stats = nc.stats()
                await nc.close()
                return stats
            
            stats = asyncio.run(check_nats_async())
            return {
                "status": "connected",
                "type": "nats",
                "in_msgs": stats["in_msgs"],
                "out_msgs": stats["out_msgs"],
                "in_bytes": stats["in_bytes"],
                "out_bytes": stats["out_bytes"],
                "connections": stats["connections"]
            }
        except Exception as e:
            return {"status": "error", "type": "nats", "error": str(e)}
    
    def check_dragonfly(self, host="localhost", port=6379) -> Dict[str, Any]:
        """Check DragonflyDB status"""
        try:
            import redis
            r = redis.Redis(host=host, port=port, decode_responses=True)
            info = r.info()
            return {
                "status": "connected",
                "type": "dragonfly",
                "version": info.get("version", "unknown"),
                "uptime": info.get("uptime", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_rss", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            return {"status": "error", "type": "dragonfly", "error": str(e)}
    
    def run_all_checks(self, config: Optional[Dict[str, Dict]] = None) -> Dict[str, Any]:
        """Run all database checks"""
        if config is None:
            # Default configuration
            config = {
                "redis": {"host": "localhost", "port": 6379},
                "mongodb": {"connection_string": "mongodb://localhost:27017"},
                "cassandra": {"host": "localhost", "port": 9042},
                "qdrant": {"host": "localhost", "port": 6333},
                "nats": {"host": "nats://localhost:4222"},
                "dragonfly": {"host": "localhost", "port": 6379}
            }
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        for db_type, db_config in config.items():
            print(f"Checking {db_type}...", file=sys.stderr)
            if db_type == "redis":
                results["checks"]["redis"] = self.check_redis(**db_config)
            elif db_type == "mongodb":
                results["checks"]["mongodb"] = self.check_mongodb(**db_config)
            elif db_type == "cassandra":
                results["checks"]["cassandra"] = self.check_cassandra(**db_config)
            elif db_type == "qdrant":
                results["checks"]["qdrant"] = self.check_qdrant(**db_config)
            elif db_type == "nats":
                results["checks"]["nats"] = self.check_nats(**db_config)
            elif db_type == "dragonfly":
                results["checks"]["dragonfly"] = self.check_dragonfly(**db_config)
        
        return results
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print a human-readable summary"""
        print("\n=== Database Status Summary ===")
        print(f"Timestamp: {results['timestamp']}\n")
        
        connected = 0
        errors = 0
        
        for db_name, db_result in results["checks"].items():
            if db_result["status"] == "connected":
                connected += 1
                print(f"✓ {db_name.upper()}: Connected")
                if "version" in db_result:
                    print(f"  Version: {db_result['version']}")
                if "uptime" in db_result:
                    print(f"  Uptime: {db_result['uptime']} seconds")
                if "used_memory" in db_result:
                    print(f"  Memory: {db_result['used_memory']}")
            else:
                errors += 1
                print(f"✗ {db_name.upper()}: Error - {db_result.get('error', 'Unknown')}")
            print()
        
        print(f"Summary: {connected} connected, {errors} errors")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Check database status")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--install-deps", action="store_true", help="Install required dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        import subprocess
        print("Installing dependencies...")
        deps = ["redis", "pymongo", "cassandra-driver", "requests", "nats"]
        for dep in deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")
        return
    
    checker = DatabaseStatusChecker()
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        checker.print_summary(results)

if __name__ == "__main__":
    main()
