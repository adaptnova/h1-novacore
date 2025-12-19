"""
Memory System Usage Example
Demonstrates how to use the Nova Framework's memory system.
"""

import asyncio
import yaml
from datetime import datetime
from typing import Dict, Any

from src.handlers.memory import MemoryManager, MemoryType

async def load_config(path: str = "config/memory_config.yaml") -> Dict[str, Any]:
    """Load memory configuration from YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

async def demonstrate_short_term_memory(manager: MemoryManager):
    """Demonstrate short-term memory operations using Redis."""
    print("\n=== Short-term Memory Demo ===")

    # Store temporary data
    cache_key = "user:session:123"
    session_data = {
        "user_id": "user123",
        "last_access": datetime.now().isoformat(),
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }

    success = await manager.store(
        MemoryType.SHORT_TERM,
        cache_key,
        session_data,
        ttl=3600  # 1 hour expiry
    )
    print(f"Stored session data: {success}")

    # Retrieve the data
    retrieved_data = await manager.retrieve(MemoryType.SHORT_TERM, cache_key)
    print(f"Retrieved session data: {retrieved_data}")

    # Update preferences
    session_data["preferences"]["theme"] = "light"
    success = await manager.update(
        MemoryType.SHORT_TERM,
        cache_key,
        session_data
    )
    print(f"Updated session data: {success}")

async def demonstrate_long_term_memory(manager: MemoryManager):
    """Demonstrate long-term memory operations using MongoDB."""
    print("\n=== Long-term Memory Demo ===")

    # Store user profile
    profile_key = "user:profile:123"
    profile_data = {
        "user_id": "user123",
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": datetime.now().isoformat(),
        "settings": {
            "language": "en",
            "timezone": "UTC"
        }
    }

    success = await manager.store(MemoryType.LONG_TERM, profile_key, profile_data)
    print(f"Stored user profile: {success}")

    # Retrieve with metadata
    retrieved_data = await manager.retrieve(
        MemoryType.LONG_TERM,
        profile_key,
        include_metadata=True
    )
    print(f"Retrieved user profile with metadata: {retrieved_data}")

    # List all user profiles
    keys = await manager.list_keys(MemoryType.LONG_TERM, "user:profile:*")
    print(f"Found user profiles: {keys}")

async def demonstrate_semantic_memory(manager: MemoryManager):
    """Demonstrate semantic memory operations using Neo4j."""
    print("\n=== Semantic Memory Demo ===")

    # Store connected concepts
    concept_key = "concept:machine_learning"
    concept_data = {
        "name": "Machine Learning",
        "type": "technology",
        "description": "A field of AI focused on data-driven learning"
    }

    # Define relationships to other concepts
    relationships = [
        {
            "target_key": "concept:artificial_intelligence",
            "properties": {
                "type": "is_subset_of",
                "strength": 0.9
            }
        },
        {
            "target_key": "concept:deep_learning",
            "properties": {
                "type": "has_subset",
                "strength": 0.8
            }
        }
    ]

    success = await manager.store(
        MemoryType.SEMANTIC,
        concept_key,
        concept_data,
        relationships=relationships
    )
    print(f"Stored concept with relationships: {success}")

    # Retrieve with relationships
    retrieved_data = await manager.retrieve(
        MemoryType.SEMANTIC,
        concept_key,
        include_relationships=True
    )
    print(f"Retrieved concept with relationships: {retrieved_data}")

async def demonstrate_memory_management(manager: MemoryManager):
    """Demonstrate memory management operations."""
    print("\n=== Memory Management Demo ===")

    # Check health of all memory systems
    health = await manager.health_check()
    print(f"Memory system health: {health}")

    # Get statistics for each memory type
    stats = await manager.get_stats()
    print(f"Memory system statistics: {stats}")

async def main():
    """Main demonstration function."""
    try:
        # Load configuration
        config = await load_config()

        # Initialize memory manager
        manager = MemoryManager(config)
        await manager.connect()

        try:
            # Run demonstrations
            await demonstrate_short_term_memory(manager)
            await demonstrate_long_term_memory(manager)
            await demonstrate_semantic_memory(manager)
            await demonstrate_memory_management(manager)

        finally:
            # Clean up
            await manager.disconnect()

    except Exception as e:
        print(f"Error during demonstration: {e}")

if __name__ == "__main__":
    asyncio.run(main())