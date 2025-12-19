#!/usr/bin/env python3
"""
Database Connection Tester
Quickly test database connectivity and gather connection info
"""

import sys
import json
import argparse
import socket
from typing import Dict, Any, List

class DatabaseConnectionTester:
    def __init__(self):
        self.test_results = []
    
    def test_port(self, host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
        """Test if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return {
                "host": host,
                "port": port,
                "open": result == 0,
                "status": "open" if result == 0 else "closed"
            }
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "open": False,
                "status": f"error: {str(e)}"
            }
    
    def test_redis_connection(self, host="localhost", port=6379, password=None, timeout=5) -> Dict[str, Any]:
        """Test Redis connection"""
        try:
            import redis
            
            r = redis.Redis(
                host=host,
                port=port,
                password=password,
                socket_timeout=timeout,
                decode_responses=True
            )
            
            # Test with PING
            response = r.ping()
            
            # Get basic info
            info = r.info()
            
            return {
                "status": "connected",
                "type": "redis",
                "host": host,
                "port": port,
                "ping": response,
                "version": info.get("redis_version", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
            
        except redis.AuthenticationError:
            return {
                "status": "auth_error",
                "type": "redis",
                "host": host,
                "port": port,
                "error": "Authentication failed - wrong password"
            }
        except redis.ConnectionError as e:
            return {
                "status": "connection_error",
                "type": "redis",
                "host": host,
                "port": port,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "redis",
                "host": host,
                "port": port,
                "error": str(e)
            }
    
    def test_mongodb_connection(self, connection_string="mongodb://localhost:27017", timeout=5) -> Dict[str, Any]:
        """Test MongoDB connection"""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=timeout * 1000
            )
            
            # Test connection
            server_info = client.server_info()
            db_stats = client.admin.command("dbStats")
            
            # List databases
            databases = client.list_database_names()
            
            return {
                "status": "connected",
                "type": "mongodb",
                "connection_string": connection_string,
                "version": server_info.get("version", "unknown"),
                "uptime": server_info.get("uptime", 0),
                "databases": databases,
                "database_count": len(databases)
            }
            
        except pymongo.errors.ConnectionFailure as e:
            return {
                "status": "connection_error",
                "type": "mongodb",
                "connection_string": connection_string,
                "error": str(e)
            }
        except pymongo.errors.OperationFailure as e:
            return {
                "status": "auth_error",
                "type": "mongodb",
                "connection_string": connection_string,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "mongodb",
                "connection_string": connection_string,
                "error": str(e)
            }
    
    def test_cassandra_connection(self, host="localhost", port=9042, keyspace=None, timeout=5) -> Dict[str, Any]:
        """Test Cassandra connection"""
        try:
            from cassandra.cluster import Cluster
            from cassandra.policies import WhiteListRoundRobinPolicy
            
            cluster = Cluster(
                [host],
                port=port,
                protocol_version=4,
                connect_timeout=timeout
            )
            
            session = cluster.connect(keyspace)
            
            # Get cluster info
            hosts = cluster.metadata.all_hosts()
            keyspaces = cluster.metadata.keyspaces
            cluster_name = cluster.metadata.cluster_name
            
            # Test with a simple query
            result = session.execute("SELECT * FROM system.local LIMIT 1")
            
            cluster.shutdown()
            
            return {
                "status": "connected",
                "type": "cassandra",
                "host": host,
                "port": port,
                "cluster_name": cluster_name,
                "hosts_count": len(hosts),
                "keyspaces_count": len(keyspaces),
                "keyspace": keyspace
            }
            
        except cassandra.errors.AuthenticationFailed:
            return {
                "status": "auth_error",
                "type": "cassandra",
                "host": host,
                "port": port,
                "error": "Authentication failed"
            }
        except cassandra.cluster.NoHostAvailable:
            return {
                "status": "no_host_available",
                "type": "cassandra",
                "host": host,
                "port": port,
                "error": "No host available for connection"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "cassandra",
                "host": host,
                "port": port,
                "error": str(e)
            }
    
    def test_qdrant_connection(self, host="localhost", port=6333, timeout=5) -> Dict[str, Any]:
        """Test Qdrant connection"""
        try:
            import requests
            
            response = requests.get(
                f"http://{host}:{port}/collections",
                timeout=timeout
            )
            
            if response.status_code == 200:
                collections = response.json()
                return {
                    "status": "connected",
                    "type": "qdrant",
                    "host": host,
                    "port": port,
                    "collections_count": len(collections.get("result", {}).get("collections", [])),
                    "collections": [c["name"] for c in collections.get("result", {}).get("collections", [])]
                }
            else:
                return {
                    "status": "http_error",
                    "type": "qdrant",
                    "host": host,
                    "port": port,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "type": "qdrant",
                "host": host,
                "port": port,
                "error": "Connection refused"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "type": "qdrant",
                "host": host,
                "port": port,
                "error": "Connection timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "qdrant",
                "host": host,
                "port": port,
                "error": str(e)
            }
    
    def test_nats_connection(self, host="nats://localhost:4222", timeout=5) -> Dict[str, Any]:
        """Test NATS connection"""
        try:
            import nats
            import asyncio
            
            async def test_nats():
                try:
                    nc = await nats.connect(host, allow_reconnect=False, max_reconnect_attempts=1)
                    stats = nc.stats()
                    await nc.close()
                    return stats
                except Exception as e:
                    raise e
            
            stats = asyncio.run(test_nats())
            return {
                "status": "connected",
                "type": "nats",
                "host": host,
                "in_msgs": stats["in_msgs"],
                "out_msgs": stats["out_msgs"],
                "connections": stats["connections"]
            }
            
        except nats.errors.NoRespondersError:
            return {
                "status": "connection_error",
                "type": "nats",
                "host": host,
                "error": "No responders available"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "nats",
                "host": host,
                "error": str(e)
            }
    
    def scan_ports(self, host: str, ports: List[int], timeout: int = 2) -> Dict[str, Any]:
        """Scan multiple ports on a host"""
        results = []
        for port in ports:
            result = self.test_port(host, port, timeout)
            results.append(result)
        
        return {
            "host": host,
            "scanned_ports": ports,
            "results": results,
            "open_ports": [r["port"] for r in results if r["open"]]
        }
    
    def test_connection(self, db_type: str, **kwargs) -> Dict[str, Any]:
        """Test connection to specified database"""
        if db_type == "redis":
            return self.test_redis_connection(**kwargs)
        elif db_type == "mongodb":
            return self.test_mongodb_connection(**kwargs)
        elif db_type == "cassandra":
            return self.test_cassandra_connection(**kwargs)
        elif db_type == "qdrant":
            return self.test_qdrant_connection(**kwargs)
        elif db_type == "nats":
            return self.test_nats_connection(**kwargs)
        else:
            return {
                "status": "unsupported",
                "error": f"Unsupported database type: {db_type}"
            }
    
    def print_result(self, result: Dict[str, Any]) -> None:
        """Print test result"""
        status = result.get("status", "unknown")
        
        if status == "connected":
            print(f"✓ {result['type'].upper()}: Connected successfully")
            print(f"  Host: {result.get('host', 'N/A')}")
            print(f"  Port: {result.get('port', 'N/A')}")
            if 'version' in result:
                print(f"  Version: {result['version']}")
            if 'uptime' in result:
                print(f"  Uptime: {result['uptime']} seconds")
            if 'databases' in result:
                print(f"  Databases: {result['databases']}")
        elif status in ["auth_error", "connection_error", "no_host_available"]:
            print(f"✗ {result['type'].upper()}: {status.replace('_', ' ').title()}")
            print(f"  Host: {result.get('host', 'N/A')}")
            print(f"  Port: {result.get('port', 'N/A')}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        elif status == "unsupported":
            print(f"? Database type: {result.get('error', 'Unknown')}")
        else:
            print(f"? {result.get('type', 'unknown').upper()}: {status}")
            if 'error' in result:
                print(f"  Error: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description="Test database connections")
    parser.add_argument("--type", choices=["redis", "mongodb", "cassandra", "qdrant", "nats"],
                        help="Database type to test")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--password", help="Database password")
    parser.add_argument("--db", help="Database/keyspace name")
    parser.add_argument("--scan-ports", action="store_true", help="Scan for common database ports")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
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
    
    tester = DatabaseConnectionTester()
    
    if args.scan_ports:
        # Common database ports
        common_ports = [6379, 6380, 27017, 28017, 9042, 9043, 6333, 6334, 4222, 6222]
        result = tester.scan_ports(args.host, common_ports)
    elif args.type:
        # Build connection kwargs
        kwargs = {"host": args.host}
        if args.port:
            kwargs["port"] = args.port
        if args.password:
            kwargs["password"] = args.password
        if args.db:
            if args.type == "mongodb":
                kwargs["connection_string"] = f"mongodb://{args.host}:{args.port or 27017}"
            elif args.type == "cassandra":
                kwargs["keyspace"] = args.db
        
        result = tester.test_connection(args.type, **kwargs)
    else:
        print("Please specify either --type or --scan-ports")
        return
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "results" in result:
            # Port scan results
            print(f"\n=== Port Scan Results for {args.host} ===")
            print(f"Scanned ports: {result['scanned_ports']}")
            print(f"Open ports: {result['open_ports']}")
            for res in result["results"]:
                status = "✓" if res["open"] else "✗"
                print(f"{status} Port {res['port']}: {res['status']}")
        else:
            # Single connection test
            tester.print_result(result)

if __name__ == "__main__":
    main()
