#!/usr/bin/env python3
"""
Multi-Database Query Runner
Execute queries across different database types
"""

import sys
import json
import argparse
from typing import Any, Dict, Optional, List

class DatabaseQueryRunner:
    def __init__(self):
        self.results = []
    
    def execute_redis_query(self, query: str, host="localhost", port=6379, password=None) -> Dict[str, Any]:
        """Execute Redis commands"""
        try:
            import redis
            r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
            
            # Parse query (simple parsing for common commands)
            parts = query.strip().split()
            if not parts:
                return {"success": False, "error": "Empty query"}
            
            command = parts[0].lower()
            
            if command == "get":
                key = parts[1] if len(parts) > 1 else None
                if not key:
                    return {"success": False, "error": "Key required for GET"}
                result = r.get(key)
                return {"success": True, "command": query, "result": result}
            
            elif command == "set":
                if len(parts) < 3:
                    return {"success": False, "error": "SET requires key and value"}
                key, value = parts[1], parts[2]
                r.set(key, value)
                return {"success": True, "command": query, "result": "OK"}
            
            elif command == "keys":
                pattern = parts[1] if len(parts) > 1 else "*"
                keys = r.keys(pattern)
                return {"success": True, "command": query, "result": keys}
            
            elif command == "info":
                info = r.info()
                return {"success": True, "command": query, "result": info}
            
            else:
                # Try to execute as-is
                try:
                    result = r.execute_command(*parts)
                    return {"success": True, "command": query, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_mongodb_query(self, query: str, connection_string="mongodb://localhost:27017", 
                              db_name=None, collection_name=None) -> Dict[str, Any]:
        """Execute MongoDB queries"""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Parse query (simple parsing)
            if not db_name:
                db_name = "test"
            
            db = client[db_name]
            
            # Try to parse as JSON first
            try:
                query_obj = json.loads(query)
            except json.JSONDecodeError:
                # If not JSON, try to extract collection and operation
                if collection_name:
                    collection = db[collection_name]
                    if query.strip().lower() == "find":
                        docs = list(collection.find().limit(10))
                        return {"success": True, "command": query, "result": docs}
                    elif query.strip().lower().startswith("count"):
                        count = collection.count_documents({})
                        return {"success": True, "command": query, "result": count}
                    else:
                        return {"success": False, "error": "Unsupported MongoDB operation"}
                else:
                    return {"success": False, "error": "Collection name required"}
            
            # If query_obj is a dict, try to execute
            if isinstance(query_obj, dict):
                # Check if it's a find operation
                if "$find" in query_obj:
                    # Simple aggregation
                    collection_name = query_obj["$find"].get("collection")
                    if collection_name:
                        collection = db[collection_name]
                        result = list(collection.find().limit(10))
                        return {"success": True, "command": query, "result": result}
            
            # Default: try to find documents
            if not collection_name:
                collection_name = "test"
            
            collection = db[collection_name]
            result = list(collection.find(query_obj).limit(10))
            return {"success": True, "command": query, "result": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_cassandra_query(self, query: str, host="localhost", port=9042, keyspace=None) -> Dict[str, Any]:
        """Execute Cassandra CQL queries"""
        try:
            from cassandra.cluster import Cluster
            
            cluster = Cluster([host], port=port)
            session = cluster.connect(keyspace)
            
            result = session.execute(query)
            rows = list(result)
            
            cluster.shutdown()
            
            return {
                "success": True,
                "command": query,
                "result": rows,
                "row_count": len(rows),
                "column_names": result.column_names if hasattr(result, 'column_names') else []
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_qdrant_query(self, query: str, host="localhost", port=6333) -> Dict[str, Any]:
        """Execute Qdrant operations"""
        try:
            import requests
            
            # Parse query
            if query.strip().lower() == "collections":
                response = requests.get(f"http://{host}:{port}/collections")
                return {"success": True, "command": query, "result": response.json()}
            elif query.strip().lower().startswith("collection "):
                parts = query.split()
                if len(parts) >= 3:
                    collection_name = parts[2]
                    response = requests.get(f"http://{host}:{port}/collections/{collection_name}")
                    return {"success": True, "command": query, "result": response.json()}
            
            return {"success": False, "error": "Unsupported Qdrant operation"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_query(self, db_type: str, query: str, **kwargs) -> Dict[str, Any]:
        """Execute a query on the specified database"""
        if db_type == "redis":
            return self.execute_redis_query(query, **kwargs)
        elif db_type == "mongodb":
            return self.execute_mongodb_query(query, **kwargs)
        elif db_type == "cassandra":
            return self.execute_cassandra_query(query, **kwargs)
        elif db_type == "qdrant":
            return self.execute_qdrant_query(query, **kwargs)
        else:
            return {"success": False, "error": f"Unsupported database type: {db_type}"}
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print query result in a readable format"""
        if result["success"]:
            print(f"✓ Query executed successfully")
            print(f"Command: {result['command']}")
            if "result" in result:
                result_str = json.dumps(result["result"], indent=2, default=str)
                print(f"Result:\n{result_str}")
            if "row_count" in result:
                print(f"Rows affected: {result['row_count']}")
        else:
            print(f"✗ Query failed")
            print(f"Error: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description="Execute queries on databases")
    parser.add_argument("--type", required=True, choices=["redis", "mongodb", "cassandra", "qdrant"],
                        help="Database type")
    parser.add_argument("--query", required=True, help="Query to execute")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--db", help="Database/keyspace name")
    parser.add_argument("--collection", help="Collection/table name")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--install-deps", action="store_true", help="Install required dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        import subprocess
        print("Installing dependencies...")
        deps = ["redis", "pymongo", "cassandra-driver", "requests"]
        for dep in deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")
        return
    
    runner = DatabaseQueryRunner()
    
    # Build kwargs
    kwargs = {}
    if args.host:
        kwargs["host"] = args.host
    if args.port:
        kwargs["port"] = args.port
    if args.db:
        kwargs["db_name"] = args.db
    if args.collection:
        kwargs["collection_name"] = args.collection
    
    result = runner.run_query(args.type, args.query, **kwargs)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        runner.print_result(result)

if __name__ == "__main__":
    main()
