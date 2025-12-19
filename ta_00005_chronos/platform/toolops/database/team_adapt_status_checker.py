#!/usr/bin/env python3
"""
TeamADAPT Database Status Checker
Enhanced version that understands the TeamADAPT infrastructure
"""

import sys
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class TeamADAPTDatabaseStatusChecker:
    def __init__(self):
        self.results = {}
        self.config = self.load_team_adapt_config()
        
    def load_team_adapt_config(self) -> Dict[str, Any]:
        """Load TeamADAPT production configuration"""
        try:
            with open('team-adapt-production-config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "databases": {
                    "redis": {"host": "localhost", "port": 6379, "type": "redis"},
                    "dragonfly": {"host": "localhost", "port": 18000, "type": "dragonfly"},
                    "mongodb": {"host": "localhost", "port": 27017, "type": "mongodb"},
                    "postgresql": {"host": "localhost", "port": 18030, "type": "postgresql"},
                    "clickhouse": {"host": "localhost", "port": 18090, "type": "clickhouse"},
                    "weaviate": {"host": "localhost", "port": 18050, "type": "weaviate"},
                    "nats": {"host": "nats://localhost:4222", "port": 4222, "type": "nats"}
                }
            }
    
    def check_redis_service(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Redis/DragonflyDB service"""
        try:
            import redis
            
            # Determine if it's DragonflyDB by port or password
            is_dragonfly = "dragonfly" in name or config.get("port", 6379) >= 18000
            password = config.get("password")
            
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                password=password,
                decode_responses=True,
                socket_timeout=5
            )
            
            info = r.info()
            
            # Extract service type
            service_type = "DragonflyDB" if is_dragonfly else "Redis"
            if "cluster" in name:
                service_type += " Cluster"
            
            return {
                "status": "connected",
                "type": service_type.lower(),
                "version": info.get("version", "unknown"),
                "uptime": info.get("uptime_in_seconds", info.get("uptime", 0)),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", f"{info.get('used_memory_rss', 0) // 1024 // 1024}MB" if is_dragonfly else "unknown"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "port": config["port"],
                "service_name": name
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "redis" if "redis" in config.get("type", "") else "dragonfly",
                "error": str(e),
                "port": config["port"],
                "service_name": name
            }
    
    def check_postgresql_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check PostgreSQL service"""
        try:
            import psycopg2
            
            # Try to connect to PostgreSQL
            # Default credentials for TeamADAPT
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                user="postgres",
                password="postgres",
                database="postgres",
                connect_timeout=5
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            
            cur.execute("SELECT pg_database_size('postgres');")
            db_size = cur.fetchone()[0]
            
            cur.execute("SELECT count(*) FROM pg_stat_activity;")
            connections = cur.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "connected",
                "type": "postgresql",
                "version": version.split(",")[0],
                "database_size": f"{db_size // 1024 // 1024}MB",
                "connections": connections,
                "port": config["port"],
                "service_name": "PostgreSQL"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "postgresql",
                "error": str(e),
                "port": config["port"],
                "service_name": "PostgreSQL"
            }
    
    def check_clickhouse_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check ClickHouse service"""
        try:
            import requests
            
            response = requests.get(
                f"http://{config['host']}:{config['port']}/ping",
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "type": "clickhouse",
                    "version": "HTTP API responding",
                    "port": config["port"],
                    "service_name": "ClickHouse",
                    "http_endpoint": f"http://{config['host']}:{config['port']}"
                }
            else:
                return {
                    "status": "error",
                    "type": "clickhouse",
                    "error": f"HTTP {response.status_code}",
                    "port": config["port"],
                    "service_name": "ClickHouse"
                }
        except Exception as e:
            return {
                "status": "error",
                "type": "clickhouse",
                "error": str(e),
                "port": config["port"],
                "service_name": "ClickHouse"
            }
    
    def check_weaviate_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Weaviate service"""
        try:
            import requests
            
            response = requests.get(
                f"http://{config['host']}:{config['port']}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "connected",
                    "type": "weaviate",
                    "version": data.get("links", {}).get("name", "API v1"),
                    "api_url": f"http://{config['host']}:{config['port']}/v1",
                    "graphql_url": f"http://{config['host']}:{config['port']}/v1/graphql",
                    "port": config["port"],
                    "service_name": "Weaviate"
                }
            else:
                return {
                    "status": "error",
                    "type": "weaviate",
                    "error": f"HTTP {response.status_code}",
                    "port": config["port"],
                    "service_name": "Weaviate"
                }
        except Exception as e:
            return {
                "status": "error",
                "type": "weaviate",
                "error": str(e),
                "port": config["port"],
                "service_name": "Weaviate"
            }
    
    def check_nats_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check NATS service"""
        try:
            import nats
            import asyncio
            
            async def check_nats_async():
                nc = await nats.connect(config["host"], allow_reconnect=False)
                stats = nc.stats()
                await nc.close()
                return stats
            
            stats = asyncio.run(check_nats_async())
            return {
                "status": "connected",
                "type": "nats",
                "in_msgs": stats["in_msgs"],
                "out_msgs": stats["out_msgs"],
                "connections": stats["connections"],
                "port": config["port"],
                "service_name": "NATS"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "nats",
                "error": str(e),
                "port": config["port"],
                "service_name": "NATS"
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all database checks using TeamADAPT configuration"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "team_adapt_infrastructure": True,
            "checks": {}
        }
        
        databases = self.config.get("databases", {})
        
        for name, config in databases.items():
            print(f"Checking {config.get('service_name', name)} on port {config['port']}...", file=sys.stderr)
            
            db_type = config.get("type", "")
            
            if db_type in ["redis", "dragonfly"]:
                results["checks"][name] = self.check_redis_service(name, config)
            elif db_type == "postgresql":
                results["checks"][name] = self.check_postgresql_service(config)
            elif db_type == "clickhouse":
                results["checks"][name] = self.check_clickhouse_service(config)
            elif db_type == "weaviate":
                results["checks"][name] = self.check_weaviate_service(config)
            elif db_type == "nats":
                results["checks"][name] = self.check_nats_service(config)
            else:
                results["checks"][name] = {
                    "status": "unsupported",
                    "type": db_type,
                    "error": f"Unsupported database type: {db_type}",
                    "port": config["port"],
                    "service_name": config.get("service_name", name)
                }
        
        return results
    
    def print_team_adapt_summary(self, results: Dict[str, Any]) -> None:
        """Print TeamADAPT-specific summary"""
        print("\n" + "="*70)
        print("🏆 TeamADAPT Database Infrastructure - Status Report")
        print("="*70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Lead: Fleetwise DBOps")
        print()
        
        connected = 0
        errors = 0
        
        # Group by service type
        services = {}
        for name, result in results["checks"].items():
            service_type = result.get("service_name", name)
            if service_type not in services:
                services[service_type] = []
            services[service_type].append((name, result))
        
        for service_name, service_results in services.items():
            print(f"📊 {service_name}")
            print("-" * 50)
            
            for name, result in service_results:
                if result["status"] == "connected":
                    connected += 1
                    print(f"  ✓ {result.get('service_name', name).upper()} ({result.get('port', 'N/A')}): Connected")
                    
                    if "version" in result:
                        print(f"    Version: {result['version']}")
                    if "uptime" in result:
                        uptime_hours = result['uptime'] // 3600
                        print(f"    Uptime: {uptime_hours} hours")
                    if "used_memory" in result:
                        print(f"    Memory: {result['used_memory']}")
                    if "api_url" in result:
                        print(f"    API: {result['api_url']}")
                        
                else:
                    errors += 1
                    port = result.get('port', 'N/A')
                    error_msg = result.get('error', 'Unknown error')
                    print(f"  ✗ {result.get('service_name', name).upper()} ({port}): {error_msg}")
            print()
        
        print("="*70)
        print(f"📈 SUMMARY")
        print("="*70)
        print(f"Total Services: {connected + errors}")
        print(f"✅ Connected: {connected}")
        print(f"❌ Errors: {errors}")
        success_rate = (connected * 100 // (connected + errors)) if (connected + errors) > 0 else 0
        print(f"Success Rate: {success_rate}%")
        print()
        
        if errors == 0:
            print("🎉 ALL SERVICES HEALTHY! TeamADAPT infrastructure operational.")
        else:
            print("⚠️  Some services require attention. Check errors above.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="TeamADAPT Database Status Checker")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--install-deps", action="store_true", help="Install required dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        import subprocess
        print("Installing dependencies...")
        deps = ["redis", "psycopg2-binary", "requests", "nats"]
        for dep in deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")
        return
    
    checker = TeamADAPTDatabaseStatusChecker()
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        checker.print_team_adapt_summary(results)

if __name__ == "__main__":
    main()
