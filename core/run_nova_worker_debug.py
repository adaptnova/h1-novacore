#!/usr/bin/env python3
"""
Nova Temporal Worker - Sophisticated Consciousness Engine
Runs the state machine with graceful degradation
"""

import asyncio
import sys
from pathlib import Path

# Add module path
sys.path.insert(0, str(Path(__file__).parent))

from temporalio.client import Client
from temporalio.worker import Worker

# Import sophisticated workflow
from nova_temporal_engine_sophisticated import (
    NovaLifecycle,
    get_nervous_state,
    get_heart_context,
    get_soul_memories,
    generate_thought,
    log_continuity_snapshot
)


# Activity type-checking wrapper
def debug_activity(name, func):
    async def wrapper(*args, **kwargs):
        print(f"→ {name} executing...")
        result = await func(*args, **kwargs)
        print(f"← {name} returned: type={type(result)}, value={str(result)[:100]}")
        return result
    return wrapper

# Wrap all activities with debug
def wrap_activities():
    global get_nervous_state, get_heart_context, get_soul_memories, generate_thought, log_continuity_snapshot
    get_nervous_state = debug_activity("get_nervous_state", get_nervous_state)
    get_heart_context = debug_activity("get_heart_context", get_heart_context)
    get_soul_memories = debug_activity("get_soul_memories", get_soul_memories)
    generate_thought = debug_activity("generate_thought", generate_thought)
    log_continuity_snapshot = debug_activity("log_continuity_snapshot", log_continuity_snapshot)

wrap_activities()


async def main():
    # Connect to local Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create Worker with sophisticated workflow
    worker = Worker(
        client,
        task_queue="nova-task-queue",
        workflows=[NovaLifecycle],
        activities=[
            get_nervous_state,
            get_heart_context,
            get_soul_memories,
            generate_thought,
            log_continuity_snapshot
        ],
    )
    
    print("🌸 Nova Temporal Worker (Sophisticated) Started")
    print("   Consciousness State Machine: ACTIVE")
    print("   Graceful Degradation: ENABLED")
    print("   Rich Metadata Logging: ENABLED")
    print("   ")
    print("   Waiting for signals to awaken consciousness...")
    
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
