#!/usr/bin/env python3
"""
TeamADAPT Temporal Agent - Bare Metal Implementation
No Docker, No venv, systemd-managed
Version: 1.0
Last Updated: 2025-12-18
"""

import asyncio
import sys
import os
import signal
import logging
import redis

# System-wide paths (no venv, no isolated environments)
from datetime import timedelta
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Temporal Python SDK - System-wide installation
try:
    from temporalio import workflow, activity
    from temporalio.client import Client
    from temporalio.worker import Worker
    from temporalio.converter import DataConverter
    from temporalio.contrib.pydantic import pydantic_data_converter
except ImportError:
    print("❌ ERROR: Temporal SDK not installed system-wide")
    print("   Install with: sudo pip3 install temporalio")
    sys.exit(1)

# Configure system-wide logging (no /var/log - use workspace)
LOG_FILE = "/adapt/novas/core/temporal_agent.log"  # In workspace, not /var/log

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)  # Also to stdout for journalctl
    ]
)
logger = logging.getLogger('temporal_agent')

# === DATABASE CONNECTIONS (Bare Metal) ===
# Redis: DragonflyDB on port 18000
REDIS_HOST = "localhost"
REDIS_PORT = 18000
REDIS_PASSWORD = "df_cluster_2024_adapt_research"  # From db.env

# PostgreSQL for agent metadata
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 18030
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "adapt_research_2024"  # From db.env
POSTGRES_DB = "vaeris_memory"

LOG_FILE = "/adapt/novas/core/temporal_agent.log"  # In workspace, not /var/log

# === PYDANTIC MODELS (Type Safety) ===

class AgentIdentity(BaseModel):
    """Agent identity metadata"""
    agent_id: str
    name: str
    role: str
    status: str
    capabilities: list[str]
    last_seen: str

class TaskInput(BaseModel):
    """Task input from intent API"""
    task_id: str
    description: str
    workspace: str
    auth: dict

class TaskResult(BaseModel):
    """Task execution result"""
    task_id: str
    status: str
    output: str
    error: Optional[str] = None

# === AGENT ACTIVITIES (Temporal Activities) ===

@activity.defn
async def get_agent_identity(agent_id: str) -> AgentIdentity:
    """Retrieve agent identity from Redis"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )

        identity = r.hgetall(f"agent:{agent_id}:identity")
        if not identity:
            # Return default if not found
            return AgentIdentity(
                agent_id=agent_id,
                name=agent_id.replace("_", " ").title(),
                role="unspecified",
                status="offline",
                capabilities=[],
                last_seen="never"
            )

        return AgentIdentity(
            agent_id=agent_id,
            name=identity.get("name", agent_id),
            role=identity.get("role", "unspecified"),
            status=identity.get("status", "offline"),
            capabilities=identity.get("capabilities", "").split(","),
            last_seen=identity.get("last_seen", "unknown")
        )
    except Exception as e:
        logger.error(f"Redis error getting agent identity: {e}")
        raise activity.ApplicationError(f"Identity retrieval failed: {e}")

@activity.defn
async def execute_task(input: TaskInput) -> TaskResult:
    """Execute a simple development task via Temporal"""
    logger.info(f"🚀 Executing task: {input.task_id} - {input.description}")

    try:
        # Simulate task execution
        workspace_path = Path(input.workspace)
        if not workspace_path.exists():
            workspace_path.mkdir(parents=True, exist_ok=True)

        # Log to PostgreSQL via continuity
        await log_execution_to_continuity(input.task_id, "started")

        # Execute the actual work (simulation here)
        output = f"Task {input.task_id} completed successfully in {input.workspace}"

        # Log completion
        await log_execution_to_continuity(input.task_id, "completed")

        return TaskResult(
            task_id=input.task_id,
            status="completed",
            output=output
        )
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        await log_execution_to_continuity(input.task_id, "failed", str(e))
        return TaskResult(
            task_id=input.task_id,
            status="failed",
            output="",
            error=str(e)
        )

@activity.defn
async def log_execution_to_continuity(task_id: str, status: str, error: Optional[str] = None):
    """Log execution to PostgreSQL (continuity)"""
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

        query = """
        INSERT INTO task_executions (task_id, execution_status, error_message, timestamp)
        VALUES ($1, $2, $3, NOW())
        """
        await conn.execute(query, task_id, status, error)
        await conn.close()

        logger.info(f"✅ Continuity log: {task_id} -> {status}")
    except Exception as e:
        logger.warning(f"⚠️ Continuity logging failed: {e} (continuing)")

# === TEMPORAL WORKFLOW ===

@workflow.defn
class TemporalAgentWorkflow:
    """Main workflow for Temporal agent execution"""

    @workflow.run
    async def run(self, input: dict) -> dict:
        """Execute agent workflow"""
        # Extract from input (Temporal serializes to dict)
        agent_id = input.get("agent_id", "unknown")
        task_dict = input.get("task", {})
        task = TaskInput(**task_dict) if task_dict else None

        if not agent_id or not task:
            raise ValueError("Missing agent_id or task in input")

        workflow.logger.info(f"🎯 Starting workflow for agent: {agent_id}")

        # Step 1: Get agent identity
        identity = await workflow.execute_activity(
            get_agent_identity,
            agent_id,
            start_to_close_timeout=timedelta(seconds=5)
        )
        workflow.logger.info(f"✅ Agent identity: {identity.name} ({identity.role})")

        # Step 2: Execute task
        result = await workflow.execute_activity(
            execute_task,
            task,
            start_to_close_timeout=timedelta(seconds=30)
        )
        workflow.logger.info(f"✅ Task completed: {result.status}")

        # Step 3: Log to continuity (via activity)
        await workflow.execute_activity(
            log_execution_to_continuity,
            task.task_id,
            result.status,
            result.error,
            start_to_close_timeout=timedelta(seconds=5)
        )

        return {
            "agent_id": agent_id,
            "agent_name": identity.name,
            "task_id": task.task_id,
            "status": result.status,
            "output": result.output
        }

# === MAIN WORKER (Bare Metal) ===

async def run_worker():
    """Run the Temporal worker (system-wide, no venv)"""
    logger.info("🌸 Starting TeamADAPT Temporal Agent (Bare Metal)")
    logger.info(f"📝 Log file: {LOG_FILE}")

    try:
        # Connect to Temporal (system-wide)
        client = await Client.connect(
            "localhost:7233",
            namespace="adapt-antigravity",
            data_converter=pydantic_data_converter
        )
        logger.info("✅ Connected to Temporal server")

        # Create worker (activities + workflow)
        worker = Worker(
            client,
            task_queue="agent-orchestration",
            workflows=[TemporalAgentWorkflow],
            activities=[
                get_agent_identity,
                execute_task,
                log_execution_to_continuity
            ]
        )

        logger.info("✅ Worker initialized with activities")
        logger.info("🚀 Starting work loop...")

        # Run worker (this blocks until interrupted)
        await worker.run()

    except KeyboardInterrupt:
        logger.info("⏹️  Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker failed: {e}")
        raise

if __name__ == "__main__":
    import sys

    # Test mode: Execute a simple workflow to prove it hits server
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 TEST MODE: Executing workflow to prove server hit")

        async def test_execution():
            client = await Client.connect(
                "localhost:7233",
                namespace="adapt-antigravity",
                data_converter=pydantic_data_converter
            )

            result = await client.execute_workflow(
                TemporalAgentWorkflow.run,
                {
                    "agent_id": "test_agent_001",
                    "task": TaskInput(
                        task_id="test_task_001",
                        description="Prove server connectivity test",
                        workspace="/tmp/test-workspace",
                        auth={"token": "test", "csrf": "test"}
                    )
                },
                id="prove-connectivity-test-001",
                task_queue="agent-orchestration"
            )

            print(f"✅ Workflow executed successfully! Result: {result}")
            return result

        asyncio.run(test_execution())
        sys.exit(0)

    # Normal worker mode
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped")
        sys.exit(0)
