"""
NovaSynth State Manager Unit Tests

Tests state transformation, synchronization, and evolution capabilities of the
state management system.

Created by Cosmos
Version: 0.1.0
"""

import pytest
from datetime import datetime
from typing import Dict

from src.state.state_manager import (
    StateManager,
    StateSnapshot,
    StateTransform,
    FrameworkState
)

@pytest.fixture
def state_manager():
    """Initialize state manager for testing."""
    return StateManager()

@pytest.fixture
def test_state_data():
    """Create test state data."""
    return {
        "name": "test_state",
        "version": "1.0",
        "data": {
            "value": 42,
            "nested": {
                "key": "value"
            }
        },
        "arrays": [1, 2, 3],
        "flags": {
            "active": True,
            "debug": False
        }
    }

@pytest.fixture
def test_memory_data():
    """Create test memory data."""
    return {
        "history": ["message1", "message2"],
        "context": {
            "user": "test_user",
            "session": "test_session"
        },
        "variables": {
            "var1": "value1",
            "var2": "value2"
        }
    }

@pytest.fixture
def test_tools_data():
    """Create test tools data."""
    return {
        "tool1": {
            "type": "basic",
            "enabled": True,
            "config": {"key": "value"}
        },
        "tool2": {
            "type": "advanced",
            "enabled": False,
            "config": {"key": "value"}
        }
    }

@pytest.mark.asyncio
async def test_snapshot_creation(
    state_manager,
    test_state_data,
    test_memory_data,
    test_tools_data
):
    """Test state snapshot creation."""
    snapshot = await state_manager.create_snapshot(
        "test_framework",
        test_state_data,
        test_memory_data,
        test_tools_data,
        {"metadata_key": "value"}
    )

    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.framework_id == "test_framework"
    assert snapshot.state_data == test_state_data
    assert snapshot.memory_data == test_memory_data
    assert snapshot.tools_data == test_tools_data
    assert "metadata_key" in snapshot.metadata

@pytest.mark.asyncio
async def test_state_transformation(
    state_manager,
    test_state_data,
    test_memory_data,
    test_tools_data
):
    """Test state transformation between frameworks."""
    # Create source snapshot
    source_snapshot = await state_manager.create_snapshot(
        "source_framework",
        test_state_data,
        test_memory_data,
        test_tools_data
    )

    # Transform state
    transform = await state_manager.transform_state(
        source_snapshot,
        "target_framework",
        "standard"
    )

    assert isinstance(transform, StateTransform)
    assert transform.source_state == source_snapshot.snapshot_id
    assert transform.transform_type == "standard"
    assert "state_mapping" in transform.transform_data
    assert transform.confidence > 0

@pytest.mark.asyncio
async def test_transform_application(
    state_manager,
    test_state_data,
    test_memory_data,
    test_tools_data
):
    """Test applying state transformation."""
    # Create source snapshot
    source_snapshot = await state_manager.create_snapshot(
        "source_framework",
        test_state_data,
        test_memory_data,
        test_tools_data
    )

    # Create and apply transform
    transform = await state_manager.transform_state(
        source_snapshot,
        "target_framework"
    )

    new_snapshot = await state_manager.apply_transform(
        transform,
        "target_framework"
    )

    assert isinstance(new_snapshot, StateSnapshot)
    assert new_snapshot.framework_id == "target_framework"
    assert new_snapshot.state_data is not None
    assert new_snapshot.memory_data is not None
    assert new_snapshot.tools_data is not None

@pytest.mark.asyncio
async def test_state_mapping_creation(state_manager, test_state_data):
    """Test state mapping creation."""
    mapping = state_manager._create_state_mapping(test_state_data)

    assert "direct_mappings" in mapping
    assert "transformed_mappings" in mapping
    assert "computed_mappings" in mapping

    # Verify direct mappings
    direct = mapping["direct_mappings"]
    assert "version" in direct
    assert direct["version"]["type"] == "direct"

    # Verify transformed mappings
    transformed = mapping["transformed_mappings"]
    assert "data" in transformed
    assert "structure" in transformed["data"]

    # Verify computed mappings
    computed = mapping["computed_mappings"]
    assert "arrays" in computed
    assert computed["arrays"]["elements"] == 3

@pytest.mark.asyncio
async def test_memory_mapping_creation(state_manager, test_memory_data):
    """Test memory mapping creation."""
    mapping = state_manager._create_memory_mapping(test_memory_data)

    assert "memory_structures" in mapping
    assert "memory_indices" in mapping
    assert "memory_links" in mapping

    # Verify memory structures
    assert "history" in mapping["memory_structures"]
    assert "context" in mapping["memory_structures"]
    assert "variables" in mapping["memory_structures"]

@pytest.mark.asyncio
async def test_tools_mapping_creation(state_manager, test_tools_data):
    """Test tools mapping creation."""
    mapping = state_manager._create_tools_mapping(test_tools_data)

    assert "tool_mappings" in mapping
    assert "tool_capabilities" in mapping
    assert "tool_requirements" in mapping

    # Verify tool mappings
    assert "tool1" in mapping["tool_mappings"]
    assert "tool2" in mapping["tool_mappings"]

@pytest.mark.asyncio
async def test_structure_analysis(state_manager):
    """Test nested structure analysis."""
    test_structure = {
        "level1": {
            "level2": {
                "level3": {
                    "value": 42
                }
            }
        }
    }

    analysis = state_manager._analyze_structure(test_structure)

    assert "fields" in analysis
    assert "types" in analysis
    assert "depth" in analysis
    assert analysis["depth"] >= 3

@pytest.mark.asyncio
async def test_memory_preservation(state_manager, test_memory_data):
    """Test memory structure preservation."""
    preserved = state_manager._preserve_memory_structures(test_memory_data)

    assert "preserved_keys" in preserved
    assert "structure_types" in preserved
    assert "indices" in preserved

    assert "history" in preserved["preserved_keys"]
    assert "context" in preserved["preserved_keys"]
    assert "variables" in preserved["preserved_keys"]

@pytest.mark.asyncio
async def test_transform_confidence(
    state_manager,
    test_state_data,
    test_memory_data,
    test_tools_data
):
    """Test transformation confidence calculation."""
    # Create source snapshot
    source_snapshot = await state_manager.create_snapshot(
        "source_framework",
        test_state_data,
        test_memory_data,
        test_tools_data
    )

    # Create transforms with different types
    transforms = []
    for transform_type in ["standard", "memory_preserve", "tool_aware"]:
        transform = await state_manager.transform_state(
            source_snapshot,
            "target_framework",
            transform_type
        )
        transforms.append(transform)

    # Verify confidence values
    for transform in transforms:
        assert 0 <= transform.confidence <= 1
        assert isinstance(transform.confidence, float)

@pytest.mark.asyncio
async def test_state_evolution(
    state_manager,
    test_state_data,
    test_memory_data,
    test_tools_data
):
    """Test state evolution through multiple transformations."""
    frameworks = ["framework1", "framework2", "framework3"]
    snapshots = []

    # Create initial snapshot
    initial_snapshot = await state_manager.create_snapshot(
        frameworks[0],
        test_state_data,
        test_memory_data,
        test_tools_data
    )
    snapshots.append(initial_snapshot)

    # Evolve state through frameworks
    current_snapshot = initial_snapshot
    for framework in frameworks[1:]:
        # Transform and apply
        transform = await state_manager.transform_state(
            current_snapshot,
            framework
        )
        new_snapshot = await state_manager.apply_transform(
            transform,
            framework
        )
        snapshots.append(new_snapshot)
        current_snapshot = new_snapshot

    # Verify evolution
    assert len(snapshots) == len(frameworks)
    for snapshot, framework in zip(snapshots, frameworks):
        assert snapshot.framework_id == framework
        assert snapshot.state_data is not None
        assert snapshot.memory_data is not None
        assert snapshot.tools_data is not None

if __name__ == "__main__":
    pytest.main(["-v", "test_state_manager.py"])