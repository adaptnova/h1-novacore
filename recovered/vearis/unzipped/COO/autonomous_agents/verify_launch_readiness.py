#!/usr/bin/env python3

import os
import sys
import asyncio
import aiohttp
import logging
import yaml
from datetime import datetime
from typing import Dict, Any, List
import motor.motor_asyncio
import asyncpg
import neo4j
import aio_pika
from aiokafka import AIOKafkaProducer
import openai
from anthropic import AsyncAnthropic
import chromadb
from pymilvus import connections

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('launch_verification.log')
    ]
)
logger = logging.getLogger(__name__)

class LaunchVerifier:
    def __init__(self):
        self.load_env()
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S MST"),
            "systems": {},
            "overall_status": "PENDING"
        }

    def load_env(self):
        """Load environment variables"""
        required = {
            "POSTGRES_URL": "Database connection",
            "MONGODB_URL": "Database connection",
            "NEO4J_URL": "Database connection",
            "RABBITMQ_URL": "Message queue",
            "KAFKA_BROKERS": "Message queue",
            "OPENAI_API_KEY": "LLM integration",
            "ANTHROPIC_API_KEY": "LLM integration"
        }

        missing = []
        for var, purpose in required.items():
            if not os.getenv(var):
                missing.append(f"{var} ({purpose})")

        if missing:
            raise EnvironmentError(f"Missing required variables: {', '.join(missing)}")

    async def verify_postgres(self) -> Dict[str, Any]:
        """Verify PostgreSQL connection"""
        try:
            conn = await asyncpg.connect(os.getenv("POSTGRES_URL"))
            version = await conn.fetchval('SELECT version()')
            await conn.close()
            return {"status": "READY", "version": version}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def verify_mongodb(self) -> Dict[str, Any]:
        """Verify MongoDB connection"""
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
            server_info = await client.server_info()
            return {"status": "READY", "version": server_info["version"]}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def verify_neo4j(self) -> Dict[str, Any]:
        """Verify Neo4j connection"""
        try:
            driver = neo4j.AsyncGraphDatabase.driver(os.getenv("NEO4J_URL"))
            async with driver.session() as session:
                result = await session.run("RETURN 1")
                await result.consume()
            await driver.close()
            return {"status": "READY"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def verify_rabbitmq(self) -> Dict[str, Any]:
        """Verify RabbitMQ connection"""
        try:
            connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_URL"))
            await connection.close()
            return {"status": "READY"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def verify_kafka(self) -> Dict[str, Any]:
        """Verify Kafka connection"""
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BROKERS").split(",")
            )
            await producer.start()
            await producer.stop()
            return {"status": "READY"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def verify_llms(self) -> Dict[str, Any]:
        """Verify LLM API access"""
        results = {}

        # OpenAI
        try:
            client = openai.AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))
            models = await client.models.list()
            results["openai"] = {"status": "READY", "models": len(models.data)}
        except Exception as e:
            results["openai"] = {"status": "ERROR", "error": str(e)}

        # Anthropic
        try:
            client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            await client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            results["anthropic"] = {"status": "READY"}
        except Exception as e:
            results["anthropic"] = {"status": "ERROR", "error": str(e)}

        return results

    def verify_vector_stores(self) -> Dict[str, Any]:
        """Verify vector store connections"""
        results = {}

        # Chroma
        try:
            client = chromadb.Client()
            client.heartbeat()
            results["chroma"] = {"status": "READY"}
        except Exception as e:
            results["chroma"] = {"status": "ERROR", "error": str(e)}

        # Milvus
        try:
            connections.connect(host='localhost', port='19530')
            connections.disconnect()
            results["milvus"] = {"status": "READY"}
        except Exception as e:
            results["milvus"] = {"status": "ERROR", "error": str(e)}

        return results

    def verify_security(self) -> Dict[str, Any]:
        """Verify security systems"""
        results = {}

        # Basic security checks
        try:
            # Check SSL/TLS configuration
            import ssl
            context = ssl.create_default_context()
            results["ssl"] = {"status": "READY"}
        except Exception as e:
            results["ssl"] = {"status": "ERROR", "error": str(e)}

        # Check firewall
        try:
            import subprocess
            result = subprocess.run(['iptables', '-L'], capture_output=True)
            results["firewall"] = {
                "status": "READY" if result.returncode == 0 else "ERROR"
            }
        except Exception as e:
            results["firewall"] = {"status": "ERROR", "error": str(e)}

        return results

    def verify_monitoring(self) -> Dict[str, Any]:
        """Verify monitoring systems"""
        results = {}

        # Check log directory
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            results["logging"] = {"status": "READY"}
        except Exception as e:
            results["logging"] = {"status": "ERROR", "error": str(e)}

        # Check metrics collection
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            results["metrics"] = {
                "status": "READY",
                "cpu": cpu,
                "memory": memory
            }
        except Exception as e:
            results["metrics"] = {"status": "ERROR", "error": str(e)}

        return results

    async def verify_all_systems(self) -> Dict[str, Any]:
        """Verify all systems"""
        # Database systems
        self.results["systems"]["postgres"] = await self.verify_postgres()
        self.results["systems"]["mongodb"] = await self.verify_mongodb()
        self.results["systems"]["neo4j"] = await self.verify_neo4j()

        # Message queues
        self.results["systems"]["rabbitmq"] = await self.verify_rabbitmq()
        self.results["systems"]["kafka"] = await self.verify_kafka()

        # LLMs
        self.results["systems"]["llms"] = await self.verify_llms()

        # Vector stores
        self.results["systems"]["vector_stores"] = self.verify_vector_stores()

        # Support systems
        self.results["systems"]["security"] = self.verify_security()
        self.results["systems"]["monitoring"] = self.verify_monitoring()

        # Calculate overall status
        all_statuses = []
        for system_group in self.results["systems"].values():
            if isinstance(system_group, dict):
                if "status" in system_group:
                    all_statuses.append(system_group["status"] == "READY")
                else:
                    for subsystem in system_group.values():
                        if isinstance(subsystem, dict):
                            all_statuses.append(subsystem.get("status") == "READY")

        self.results["overall_status"] = "READY" if all(all_statuses) else "ERROR"
        return self.results

    def generate_report(self) -> str:
        """Generate verification report"""
        report = [
            "# Launch System Verification Report",
            f"Time: {self.results['timestamp']}\n",
            f"Overall Status: {self.results['overall_status']}\n"
        ]

        for system_name, system_status in self.results["systems"].items():
            report.append(f"## {system_name}")
            report.append("```yaml")
            report.append(yaml.dump(system_status, default_flow_style=False))
            report.append("```\n")

        if self.results["overall_status"] != "READY":
            report.append("## Issues Detected")
            for system_name, system_status in self.results["systems"].items():
                if isinstance(system_status, dict):
                    if system_status.get("status") == "ERROR":
                        report.append(f"- {system_name}: {system_status.get('error', 'Unknown error')}")
                    elif isinstance(system_status, dict):
                        for subsystem, substatus in system_status.items():
                            if isinstance(substatus, dict) and substatus.get("status") == "ERROR":
                                report.append(f"- {system_name}.{subsystem}: {substatus.get('error', 'Unknown error')}")

        return "\n".join(report)

async def main():
    try:
        verifier = LaunchVerifier()
        logger.info("Starting launch system verification...")

        results = await verifier.verify_all_systems()

        # Generate and save report
        report = verifier.generate_report()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"launch_verification_{timestamp}.md"

        with open(filename, 'w') as f:
            f.write(report)

        logger.info(f"Verification complete. Results saved to {filename}")

        # Exit with appropriate status code
        sys.exit(0 if results["overall_status"] == "READY" else 1)

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
