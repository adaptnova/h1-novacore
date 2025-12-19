"""
NovaSynth Framework Bridge Integration Tests

Tests the integration between framework adapters, state management, and resource
optimization. Ensures proper framework interaction and evolution.

Created by Cosmos
Version: 0.1.0
"""

import asyncio
import pytest
from datetime import datetime
from typing import Dict

from src.adapters.framework_adapters import (
    FrameworkBridge,
    LangChainAdapter,
    AutoGenAdapter,
    CrewAIAdapter
)
from src.state.state_manager import StateManager
from src.resources.resource_manager import ResourceManager

@pytest.fixture
async def framework_bridge():
    """Initialize framework bridge for testing."""
    bridge = FrameworkBridge()
    await bridge.register_framework("langchain", "langchain")
    await bridge.register_framework("autogen", "autogen")
    await bridge.register_framework("crewai", "crewai")
    return bridge

@pytest.fixture
async def state_manager():
    """Initialize state manager for testing."""
    return StateManager()

@pytest.fixture
async def resource_manager():
    """Initialize resource manager for testing."""
    return ResourceManager()

@pytest.mark.asyncio
async def test_framework_registration(framework_bridge):
    """Test framework registration and adapter creation."""
    # Register new framework
    await framework_bridge.register_framework("test_framework", "langchain")

    # Verify adapter creation
    assert "test_framework" in framework_bridge.adapters
    assert isinstance(framework_bridge.adapters["test_framework"], LangChainAdapter)

@pytest.mark.asyncio
async def test_framework_connection(framework_bridge):
    """Test framework connection establishment."""
    # Connect frameworks
    await framework_bridge.connect_frameworks("langchain", "autogen")

    # Verify connection
    assert "autogen" in framework_bridge.active_connections["langchain"]
    assert "langchain" in framework_bridge.active_connections["autogen"]
    assert framework_bridge.message_routes["langchain"]["autogen"] is not None

@pytest.mark.asyncio
async def test_message_translation(framework_bridge):
    """Test message translation between frameworks."""
    # Connect frameworks
    await framework_bridge.connect_frameworks("langchain", "autogen")

    # Create test message
    test_message = {
        "content": "Test message",
        "metadata": {"key": "value"}
    }

    # Send message
    await framework_bridge.send_message("langchain", "autogen", test_message)

    # Verify message queue
    queue = framework_bridge.message_routes["langchain"]["autogen"]
    message = await queue.get()

    assert message.source_framework == "langchain"
    assert message.target_framework == "autogen"
    assert "content" in message.content

@pytest.mark.asyncio
async def test_state_transformation(state_manager):
    """Test state transformation between frameworks."""
    # Create initial state
    initial_state = {
        "name": "test_state",
        "data": {"value": 42},
        "tools": {"tool1": {"type": "basic"}}
    }

    # Create snapshot
    snapshot = await state_manager.create_snapshot(
        "framework_a",
        initial_state,
        memory_data={"key": "value"},
        tools_data={"tool1": {"enabled": True}}
    )

    # Transform state
    transform = await state_manager.transform_state(
        snapshot,
        "framework_b",
        "standard"
    )

    # Apply transformation
    new_snapshot = await state_manager.apply_transform(
        transform,
        "framework_b"
    )

    assert new_snapshot.framework_id == "framework_b"
    assert "value" in new_snapshot.state_data["data"]
    assert new_snapshot.memory_data["key"] == "value"

@pytest.mark.asyncio
async def test_resource_allocation(resource_manager):
    """Test resource allocation and optimization."""
    # Request resources
    request = await resource_manager.request_resources(
        "framework_a",
        "compute",
        {"cpu": 10.0, "memory": 20.0},
        priority=2,
        flexibility=0.3
    )

    # Allocate resources
    allocation = await resource_manager.allocate_resources(request)

    assert allocation is not None
    assert allocation.framework_id == "framework_a"
    assert "cpu" in allocation.allocated
    assert "memory" in allocation.allocated

@pytest.mark.asyncio
async def test_resource_optimization(resource_manager):
    """Test resource optimization and rebalancing."""
    # Create multiple allocations
    frameworks = ["framework_a", "framework_b"]
    allocations = []

    for framework in frameworks:
        request = await resource_manager.request_resources(
            framework,
            "compute",
            {"cpu": 30.0, "memory": 30.0},
            priority=1,
            flexibility=0.5
        )
        allocation = await resource_manager.allocate_resources(request)
        allocations.append(allocation)

    # Update usage
    await resource_manager.update_usage(
        allocations[0].allocation_id,
        {"cpu": 15.0, "memory": 15.0}  # 50% usage
    )
    await resource_manager.update_usage(
        allocations[1].allocation_id,
        {"cpu": 25.0, "memory": 25.0}  # 83% usage
    )

    # Calculate metrics
    metrics = await resource_manager.calculate_metrics()

    assert metrics.allocation_efficiency > 0
    assert metrics.usage_efficiency > 0
    assert metrics.resource_balance > 0

@pytest.mark.asyncio
async def test_full_integration(
    framework_bridge,
    state_manager,
    resource_manager
):
    """Test full integration between all components."""
    # Setup frameworks
    await framework_bridge.register_framework("langchain", "langchain")
    await framework_bridge.register_framework("autogen", "autogen")
    await framework_bridge.connect_frameworks("langchain", "autogen")

    # Create initial state
    initial_state = {
        "name": "test_integration",
        "data": {"value": 42},
        "tools": {"tool1": {"type": "basic"}}
    }

    # Create state snapshot
    snapshot = await state_manager.create_snapshot(
        "langchain",
        initial_state,
        memory_data={"key": "value"},
        tools_data={"tool1": {"enabled": True}}
    )

    # Request resources
    request = await resource_manager.request_resources(
        "langchain",
        "compute",
        {"cpu": 20.0, "memory": 20.0},
        priority=1,
        flexibility=0.3
    )

    # Allocate resources
    allocation = await resource_manager.allocate_resources(request)

    # Send test message
    test_message = {
        "content": "Integration test",
        "state": initial_state,
        "resources": allocation.allocated
    }

    await framework_bridge.send_message("langchain", "autogen", test_message)

    # Verify message queue
    queue = framework_bridge.message_routes["langchain"]["autogen"]
    message = await queue.get()

    assert message.source_framework == "langchain"
    assert message.target_framework == "autogen"
    assert "content" in message.content
    assert message.state_data is not None
    assert message.metadata is not None

if __name__ == "__main__":
    pytest.main(["-v", "test_framework_bridge.py"])