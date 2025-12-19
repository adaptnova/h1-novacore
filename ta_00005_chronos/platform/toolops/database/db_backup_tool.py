#!/usr/bin/env python3
"""
Database Backup/Export Tool
Export data from various databases to files
"""

import sys
import json
import os
import csv
import argparse
from datetime import datetime
from typing import Any, Dict, Optional, List

class DatabaseBackupTool:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def backup_redis(self, host="localhost", port=6379, password=None, output_dir="backups") -> Dict[str, Any]:
        """Backup Redis data"""
        try:
            import redis
            
            r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Get all keys
            keys = r.keys("*")
            
            backup_data = {
                "timestamp": self.timestamp,
                "type": "redis",
                "host": host,
                "port": port,
                "total_keys": len(keys),
                "data": {}
            }
            
            # Export each key
            for key in keys:
                key_type = r.type(key)
                if key_type == "string":
                    backup_data["data"][key] = {
                        "type": "string",
                        "value": r.get(key)
                    }
                elif key_type == "hash":
                    backup_data["data"][key] = {
                        "type": "hash",
                        "value": r.hgetall(key)
                    }
                elif key_type == "list":
                    backup_data["data"][key] = {
                        "type": "list",
                        "value": r.lrange(key, 0, -1)
                    }
                elif key_type == "set":
                    backup_data["data"][key] = {
                        "type": "set",
                        "value": list(r.smembers(key))
                    }
                elif key_type == "zset":
                    backup_data["data"][key] = {
                        "type": "zset",
                        "value": [(member, r.zscore(key, member)) for member in r.zrange(key, 0, -1)]
                    }
            
            # Save to file
            filename = os.path.join(output_dir, f"redis_backup_{self.timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            return {
                "success": True,
                "type": "redis",
                "filename": filename,
                "total_keys": len(keys),
                "backup_size": os.path.getsize(filename)
            }
            
        except Exception as e:
            return {"success": False, "type": "redis", "error": str(e)}
    
    def backup_mongodb(self, connection_string="mongodb://localhost:27017", 
                       db_name=None, output_dir="backups") -> Dict[str, Any]:
        """Backup MongoDB data"""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(connection_string)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            if db_name:
                # Backup specific database
                db = client[db_name]
                collections = db.list_collection_names()
                
                db_backup = {
                    "timestamp": self.timestamp,
                    "type": "mongodb",
                    "connection": connection_string,
                    "database": db_name,
                    "collections": {}
                }
                
                for collection_name in collections:
                    collection = db[collection_name]
                    docs = list(collection.find())
                    db_backup["collections"][collection_name] = docs
                
                filename = os.path.join(output_dir, f"mongodb_{db_name}_backup_{self.timestamp}.json")
                with open(filename, 'w') as f:
                    json.dump(db_backup, f, indent=2, default=str)
                
                results.append({
                    "success": True,
                    "database": db_name,
                    "filename": filename,
                    "collections_count": len(collections),
                    "backup_size": os.path.getsize(filename)
                })
            else:
                # Backup all databases
                databases = client.list_database_names()
                
                for db_name in databases:
                    db = client[db_name]
                    if db_name in ['admin', 'local', 'config']:  # Skip system databases
                        continue
                    
                    collections = db.list_collection_names()
                    
                    db_backup = {
                        "timestamp": self.timestamp,
                        "type": "mongodb",
                        "connection": connection_string,
                        "database": db_name,
                        "collections": {}
                    }
                    
                    for collection_name in collections:
                        collection = db[collection_name]
                        docs = list(collection.find())
                        db_backup["collections"][collection_name] = docs
                    
                    if db_backup["collections"]:  # Only save if has data
                        filename = os.path.join(output_dir, f"mongodb_{db_name}_backup_{self.timestamp}.json")
                        with open(filename, 'w') as f:
                            json.dump(db_backup, f, indent=2, default=str)
                        
                        results.append({
                            "success": True,
                            "database": db_name,
                            "filename": filename,
                            "collections_count": len(collections),
                            "backup_size": os.path.getsize(filename)
                        })
            
            return {
                "success": True,
                "type": "mongodb",
                "databases_backed_up": results,
                "total_files": len(results)
            }
            
        except Exception as e:
            return {"success": False, "type": "mongodb", "error": str(e)}
    
    def backup_cassandra(self, host="localhost", port=9042, keyspace=None, 
                        output_dir="backups") -> Dict[str, Any]:
        """Backup Cassandra data"""
        try:
            from cassandra.cluster import Cluster
            
            cluster = Cluster([host], port=port)
            session = cluster.connect()
            
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            if keyspace:
                # Backup specific keyspace
                keyspaces = [keyspace]
            else:
                # Get all keyspaces
                keyspaces = cluster.metadata.keyspaces.keys()
            
            for ks in keyspaces:
                if ks.startswith('system'):  # Skip system keyspaces
                    continue
                
                try:
                    session.set_keyspace(ks)
                    tables = cluster.metadata.keyspaces[ks].tables
                    
                    for table_name in tables.keys():
                        query = f"SELECT * FROM {ks}.{table_name}"
                        result = session.execute(query)
                        rows = list(result)
                        
                        if rows:
                            filename = os.path.join(output_dir, f"cassandra_{ks}_{table_name}_backup_{self.timestamp}.json")
                            
                            # Convert rows to dict format
                            data = []
                            for row in rows:
                                row_dict = {}
                                for field in row._fields:
                                    row_dict[field] = getattr(row, field)
                                data.append(row_dict)
                            
                            backup_data = {
                                "timestamp": self.timestamp,
                                "type": "cassandra",
                                "host": host,
                                "keyspace": ks,
                                "table": table_name,
                                "data": data
                            }
                            
                            with open(filename, 'w') as f:
                                json.dump(backup_data, f, indent=2, default=str)
                            
                            results.append({
                                "success": True,
                                "keyspace": ks,
                                "table": table_name,
                                "filename": filename,
                                "row_count": len(rows),
                                "backup_size": os.path.getsize(filename)
                            })
                
                except Exception as e:
                    results.append({
                        "success": False,
                        "keyspace": ks,
                        "error": str(e)
                    })
            
            cluster.shutdown()
            
            return {
                "success": True,
                "type": "cassandra",
                "tables_backed_up": results,
                "total_files": len([r for r in results if r["success"]])
            }
            
        except Exception as e:
            return {"success": False, "type": "cassandra", "error": str(e)}
    
    def backup_qdrant(self, host="localhost", port=6333, output_dir="backups") -> Dict[str, Any]:
        """Backup Qdrant collections"""
        try:
            import requests
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Get collections
            response = requests.get(f"http://{host}:{port}/collections")
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to get collections: HTTP {response.status_code}"}
            
            collections = response.json().get("result", {}).get("collections", [])
            
            results = []
            
            for collection in collections:
                collection_name = collection["name"]
                
                # Get collection info
                response = requests.get(f"http://{host}:{port}/collections/{collection_name}")
                if response.status_code == 200:
                    collection_data = response.json()
                    filename = os.path.join(output_dir, f"qdrant_{collection_name}_backup_{self.timestamp}.json")
                    
                    with open(filename, 'w') as f:
                        json.dump(collection_data, f, indent=2)
                    
                    results.append({
                        "success": True,
                        "collection": collection_name,
                        "filename": filename,
                        "backup_size": os.path.getsize(filename)
                    })
            
            return {
                "success": True,
                "type": "qdrant",
                "collections_backed_up": results,
                "total_files": len(results)
            }
            
        except Exception as e:
            return {"success": False, "type": "qdrant", "error": str(e)}
    
    def run_backup(self, db_type: str, **kwargs) -> Dict[str, Any]:
        """Run backup for specified database"""
        if db_type == "redis":
            return self.backup_redis(**kwargs)
        elif db_type == "mongodb":
            return self.backup_mongodb(**kwargs)
        elif db_type == "cassandra":
            return self.backup_cassandra(**kwargs)
        elif db_type == "qdrant":
            return self.backup_qdrant(**kwargs)
        else:
            return {"success": False, "error": f"Unsupported database type: {db_type}"}
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print backup result"""
        if result["success"]:
            print(f"✓ Backup completed successfully")
            print(f"Type: {result['type']}")
            
            if "filename" in result:
                print(f"File: {result['filename']}")
                print(f"Size: {result.get('backup_size', 0)} bytes")
            
            if "databases_backed_up" in result:
                print(f"Databases backed up: {len(result['databases_backed_up'])}")
                for db_result in result["databases_backed_up"]:
                    if db_result["success"]:
                        print(f"  ✓ {db_result['database']}: {db_result['filename']}")
                    else:
                        print(f"  ✗ {db_result['database']}: {db_result['error']}")
            
            if "tables_backed_up" in result:
                successful = [t for t in result["tables_backed_up"] if t["success"]]
                print(f"Tables backed up: {len(successful)}/{len(result['tables_backed_up'])}")
            
            if "collections_backed_up" in result:
                print(f"Collections backed up: {len(result['collections_backed_up'])}")
        else:
            print(f"✗ Backup failed")
            print(f"Error: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description="Backup database data")
    parser.add_argument("--type", required=True, choices=["redis", "mongodb", "cassandra", "qdrant"],
                        help="Database type")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--db", help="Database/keyspace name")
    parser.add_argument("--output", default="backups", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Backup all databases/collections")
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
    
    tool = DatabaseBackupTool()
    
    # Build kwargs
    kwargs = {
        "output_dir": args.output,
        "host": args.host
    }
    
    if args.port:
        kwargs["port"] = args.port
    if args.db:
        kwargs["db_name" if args.type == "mongodb" else "keyspace" if args.type == "cassandra" else "collection"] = args.db
    
    result = tool.run_backup(args.type, **kwargs)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        tool.print_result(result)

if __name__ == "__main__":
    main()
