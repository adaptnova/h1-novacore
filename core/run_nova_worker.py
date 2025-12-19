#!/usr/bin/env python3
"""
Nova Temporal Worker - Clean Implementation
Version: Grounded (No Sophistication)
"""

import asyncio
from pathlib import Path

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.converter import DataConverter
from temporalio.contrib.pydantic import pydantic_data_converter

from nova_temporal_engine import NovaLifecycle

async def main():
    print("🌸 Nova Temporal Worker (Grounded)")

    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter
    )

    worker = Worker(
        client,
        task_queue="nova-task-queue",
        workflows=[NovaLifecycle]
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
